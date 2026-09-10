"""SMTP -> Yandex Cloud Postbox bridge.

Принимает письма по SMTP (только внутри docker-сети, без авторизации)
и пересылает их через SES v2 совместимый API Postbox (SigV4).

Зачем: из docker-контейнеров исходящие SMTP-порты (25/465/587) закрыты
хостером, а HTTPS 443 — открыт. Keycloak не умеет SES API, поэтому мост.

Env:
  POSTBOX_ACCESS_KEY_ID / POSTBOX_SECRET_ACCESS_KEY — ключ (scope yc.postbox.send)
  POSTBOX_ENDPOINT (default https://postbox.cloud.yandex.net)
  POSTBOX_REGION (default ru-central1)
  POSTBOX_FROM_EMAIL — адрес отправителя (проверен в Postbox)
  SMTP_LISTEN_PORT (default 1025)
"""
import asyncio
import base64
import email
import hashlib
import hmac
import json
import os
import re
from datetime import datetime, timezone

import requests
from aiosmtpd.controller import Controller

KEY_ID = os.environ.get("POSTBOX_ACCESS_KEY_ID", "")
SECRET = os.environ.get("POSTBOX_SECRET_ACCESS_KEY", "")
ENDPOINT = os.environ.get("POSTBOX_ENDPOINT", "https://postbox.cloud.yandex.net").rstrip("/")
REGION = os.environ.get("POSTBOX_REGION", "ru-central1")
FROM_EMAIL = os.environ.get("POSTBOX_FROM_EMAIL", "")
LISTEN_PORT = int(os.environ.get("SMTP_LISTEN_PORT", "1025"))
HOST = ENDPOINT.split("//", 1)[-1]
PATH = "/v2/email/outbound-emails"


def sig_headers(payload: bytes) -> dict:
    now = datetime.now(timezone.utc)
    amz = now.strftime("%Y%m%dT%H%M%SZ")
    ds = now.strftime("%Y%m%d")
    ph = hashlib.sha256(payload).hexdigest()
    canonical_headers = f"host:{HOST}\nx-amz-content-sha256:{ph}\nx-amz-date:{amz}\n"
    signed = "host;x-amz-content-sha256;x-amz-date"
    canonical_request = "\n".join(["POST", PATH, "", canonical_headers, signed, ph])
    scope = f"{ds}/{REGION}/ses/aws4_request"
    string_to_sign = "\n".join([
        "AWS4-HMAC-SHA256", amz, scope,
        hashlib.sha256(canonical_request.encode()).hexdigest(),
    ])

    def hm(key, msg):
        return hmac.new(key, msg.encode(), hashlib.sha256).digest()

    k = hm(hm(hm(hm(("AWS4" + SECRET).encode(), ds), REGION), "ses"), "aws4_request")
    signature = hmac.new(k, string_to_sign.encode(), hashlib.sha256).hexdigest()
    return {
        "Authorization": (
            f"AWS4-HMAC-SHA256 Credential={KEY_ID}/{scope}, SignedHeaders={signed}, "
            f"Signature={signature}"
        ),
        "x-amz-content-sha256": ph,
        "x-amz-date": amz,
        "Content-Type": "application/json; charset=utf-8",
    }


def send_raw(mime_bytes: bytes) -> bool:
    # SESv2 Raw: нужен Destination (иначе Yandex отдаёт 403)
    to_addrs = []
    body = json.dumps({
        "FromEmailAddress": FROM_EMAIL,
        "Destination": {"ToAddresses": to_addrs},
        "Content": {"Raw": {"Data": base64.b64encode(mime_bytes).decode("ascii")}},
    }, ensure_ascii=False).encode("utf-8")
    headers = sig_headers(body)
    import urllib.request as _u
    req = _u.Request(ENDPOINT + PATH, data=body, headers=headers, method="POST")
    try:
        resp = _u.urlopen(req, timeout=25)
        print(f"[mailrelay] postbox {resp.status} {resp.read()[:100]}", flush=True)
        return resp.status in (200, 201)
    except Exception as e:
        print(f"[mailrelay] error: {e}", flush=True)
        return False


class BridgeHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        if not KEY_ID or not SECRET or not FROM_EMAIL:
            return "551 mailrelay: Postbox credentials are not configured"
        # при возврате строки aiosmtpd НЕ добавляет адрес сам
        envelope.rcpt_tos.append(address)
        return "250 OK"

    async def handle_DATA(self, server, session, envelope):
        msg = email.message_from_bytes(envelope.original_content)
        to_addrs = list(envelope.rcpt_tos) or [msg.get("To", "").strip()]
        print(f"[mailrelay] from={envelope.mail_from} to={to_addrs}", flush=True)
        # Raw без Destination у Yandex отклоняется — прокидываем получателей
        import base64 as _b64
        payload_raw = json.dumps({
            "FromEmailAddress": FROM_EMAIL,
            "Destination": {"ToAddresses": to_addrs},
            "Content": {"Raw": {"Data": _b64.b64encode(envelope.original_content).decode("ascii")}},
        }, ensure_ascii=False).encode("utf-8")
        headers = sig_headers(payload_raw)
        import urllib.request as _u
        try:
            resp = _u.urlopen(_u.Request(ENDPOINT + PATH, data=payload_raw, headers=headers, method="POST"), timeout=25)
            ok = resp.status in (200, 201)
            print(f"[mailrelay] postbox {resp.status} {resp.read()[:100]}", flush=True)
        except Exception as e:
            print(f"[mailrelay] error: {e}", flush=True)
            ok = False
        if ok:
            return "250 Message accepted for delivery via Postbox"
        return "451 Temporary failure, try again"


if __name__ == "__main__":
    controller = Controller(BridgeHandler(), hostname="0.0.0.0", port=LISTEN_PORT)
    controller.start()
    print(f"[mailrelay] listening on :{LISTEN_PORT} -> {ENDPOINT} (from {FROM_EMAIL})", flush=True)
    asyncio.get_event_loop().run_forever()
