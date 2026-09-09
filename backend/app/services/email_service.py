"""
Email Service: отправка PDF-отчётов через SMTP (MailHog в dev).
"""
import glob
import json
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.services.pdf_service import generate_pdf_report


class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "mailhog")
        self.smtp_port = int(os.getenv("SMTP_PORT", "1025"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.use_tls = os.getenv("SMTP_USE_TLS", "false").lower() == "true"
        self.from_email = os.getenv("FROM_EMAIL", "reports@ai-maturity.platform")
        self.from_name = os.getenv("FROM_NAME", "AI Maturity Platform")
        self.raw_path = os.getenv("RAW_AUDITS_PATH", "/data_storage/raw_audits")
        # Postbox (Yandex Cloud, SES v2 совместимый API)
        self.postbox_key_id = os.getenv("POSTBOX_ACCESS_KEY_ID", "")
        self.postbox_secret = os.getenv("POSTBOX_SECRET_ACCESS_KEY", "")
        self.postbox_endpoint = os.getenv("POSTBOX_ENDPOINT", "https://postbox.cloud.yandex.net").rstrip("/")
        self.postbox_region = os.getenv("POSTBOX_REGION", "ru-central1")
        self.postbox_from_email = os.getenv("POSTBOX_FROM_EMAIL", "")
        self.postbox_from_name = os.getenv("POSTBOX_FROM_NAME", "AI Maturity Platform")
        self.provider = "postbox" if self.postbox_key_id and self.postbox_secret else "smtp"

    def _load_audit(self, audit_id):
        patterns = [
            os.path.join(self.raw_path, "**", "audit_%s.json" % audit_id),
            os.path.join(self.raw_path, "**", "%s.json" % audit_id),
        ]
        for pat in patterns:
            files = glob.glob(pat, recursive=True)
            if files:
                try:
                    with open(files[0], encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    print("EmailService: read error %s: %s" % (files[0], e))
        return None

    def get_status(self) -> dict:
        """Статус почтового провайдера (без секретов)."""
        return {
            "provider": self.provider,
            "configured": self.provider == "postbox" or bool(os.getenv("SMTP_HOST")),
            "host": self.smtp_host,
            "port": self.smtp_port,
            "use_tls": self.use_tls,
            "from_email": self.postbox_from_email or self.from_email,
            "from_name": self.postbox_from_name or self.from_name,
            "auth_enabled": bool(self.smtp_user and self.smtp_password),
            "postbox": {
                "endpoint": self.postbox_endpoint,
                "region": self.postbox_region,
                "configured": bool(self.postbox_key_id and self.postbox_secret),
                "from_email": self.postbox_from_email,
            },
        }

    def send_email(self, to_emails, subject, html_body: str = "", text_body: str = "") -> bool:
        """Отправка письма без вложений. Возвращает True при успехе."""
        if self.provider == "postbox":
            return self._send_via_postbox(to_emails, subject, html_body=html_body, text_body=text_body)
        to_list = [to_emails] if isinstance(to_emails, str) else list(to_emails)
        msg = MIMEMultipart()
        msg["From"] = "%s <%s>" % (self.from_name, self.from_email)
        msg["To"] = ", ".join(to_list)
        msg["Subject"] = subject
        msg.attach(MIMEText(
            html_body or text_body or "",
            "html" if html_body else "plain",
            "utf-8",
        ))
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_password:
                    try:
                        server.login(self.smtp_user, self.smtp_password)
                    except Exception:
                        pass
                server.sendmail(self.from_email, to_list, msg.as_string())
            print("EmailService: send_email ok -> %s" % to_list)
            return True
        except Exception as e:
            print("EmailService: send_email failed: %s" % e)
            return False

    def _sigv4_headers(self, method: str, path_qs: str, payload: bytes) -> dict:
        """AWS Signature V4 (Yandex Cloud: region ru-central1, service ses)."""
        import hashlib
        import hmac
        from datetime import datetime, timezone

        access_key = self.postbox_key_id
        secret_key = self.postbox_secret
        region = self.postbox_region
        service = "ses"

        now = datetime.now(timezone.utc)
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = now.strftime("%Y%m%d")

        payload_hash = hashlib.sha256(payload).hexdigest()
        host = self.postbox_endpoint.split("//", 1)[-1]

        canonical_headers = f"host:{host}\nx-amz-content-sha256:{payload_hash}\nx-amz-date:{amz_date}\n"
        signed_headers = "host;x-amz-content-sha256;x-amz-date"
        canonical_request = "\n".join([
            method, path_qs, "",
            canonical_headers,
            signed_headers,
            payload_hash,
        ])
        scope = f"{date_stamp}/{region}/{service}/aws4_request"
        string_to_sign = "\n".join([
            "AWS4-HMAC-SHA256", amz_date, scope, hashlib.sha256(canonical_request.encode()).hexdigest(),
        ])

        def _hmac(key, msg):
            return hmac.new(key, msg.encode(), hashlib.sha256).digest()

        k_date = _hmac(("AWS4" + secret_key).encode(), date_stamp)
        k_region = _hmac(k_date, region)
        k_service = _hmac(k_region, service)
        k_signing = _hmac(k_service, "aws4_request")
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()

        return {
            "Authorization": (
                f"AWS4-HMAC-SHA256 Credential={access_key}/{scope}, "
                f"SignedHeaders={signed_headers}, Signature={signature}"
            ),
            "x-amz-content-sha256": payload_hash,
            "x-amz-date": amz_date,
            "Content-Type": "application/json",
        }

    def _postbox_send(self, payload: dict) -> bool:
        """POST в SES v2 совместимый API Postbox. payload — Simple или Raw."""
        import requests

        path = "/v2/email/outbound-emails"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = self._sigv4_headers("POST", path, body)
        headers["Host"] = self.postbox_endpoint.split("//", 1)[-1]
        try:
            resp = requests.post(self.postbox_endpoint + path, data=body,
                                 headers=headers, timeout=20)
            ok = resp.status_code in (200, 201)
            print("Postbox: send status %s %s" % (resp.status_code, resp.text[:200] if not ok else ""))
            return ok
        except Exception as e:
            print("Postbox: send failed: %s" % e)
            return False

    def _send_via_postbox(self, to_emails, subject, html_body="", text_body=""):
        from_addr = (
            f"{self.postbox_from_name} <{self.postbox_from_email}>"
            if self.postbox_from_name and self.postbox_from_email
            else (self.postbox_from_email or self.from_email)
        )
        to_list = [to_emails] if isinstance(to_emails, str) else list(to_emails)
        body: dict = {}
        if html_body:
            body["Html"] = {"Data": html_body, "Charset": "UTF-8"}
        if text_body:
            body["Text"] = {"Data": text_body, "Charset": "UTF-8"}
        payload = {
            "FromEmailAddress": from_addr,
            "Destination": {"ToAddresses": to_list},
            "Content": {"Simple": {
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": body,
            }},
        }
        return self._postbox_send(payload)

    def _send_raw_via_postbox(self, to_email: str, mime_bytes: bytes) -> bool:
        import base64 as _b64

        from_addr = (
            f"{self.postbox_from_name} <{self.postbox_from_email}>"
            if self.postbox_from_name and self.postbox_from_email
            else (self.postbox_from_email or self.from_email)
        )
        payload = {
            "FromEmailAddress": from_addr,
            "Destination": {"ToAddresses": [to_email] if isinstance(to_email, str) else list(to_email)},
            "Content": {"Raw": {"Data": _b64.b64encode(mime_bytes).decode("ascii")}},
        }
        return self._postbox_send(payload)

    def send_report(self, to_email, audit_id, body=""):
        audit_data = self._load_audit(audit_id) or {"audit_id": audit_id}

        pdf_bytes = None
        try:
            pdf_bytes = generate_pdf_report(audit_data)
            print("EmailService: PDF generated OK, %d bytes" % len(pdf_bytes or b""))
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("EmailService: PDF generation failed: %s" % e)

        indices = audit_data.get("calculated_indices", {}) or {}
        composite = indices.get("composite_score", 0)
        level = indices.get("maturity_level", "")

        msg = MIMEMultipart()
        msg["From"] = "%s <%s>" % (self.from_name, self.from_email)
        msg["To"] = to_email
        msg["Subject"] = "Ваш отчёт об оценке зрелости ИИ — %s" % level

        if body and ("<html" in body.lower() or "<div" in body.lower() or "<p" in body.lower()):
            msg.attach(MIMEText(body, "html", "utf-8"))
        else:
            text_body = body or (
                "Здравствуйте!\n\n"
                "Спасибо за прохождение аудита зрелости ИИ на AI Maturity Platform.\n\n"
                "Ваш общий балл: %.2f / 5.00\n"
                "Уровень зрелости: %s\n\n"
                "Во вложении — полный PDF-отчёт:\n"
                "- Радар зрелости по 7 осям (текущее / целевое / бенчмарк)\n"
                "- Диагноз и ключевые рекомендации\n"
                "- Персональные рекомендуемые услуги\n\n"
                "С уважением,\nКоманда AI Maturity Platform" % (composite, level)
            )
            msg.attach(MIMEText(text_body, "plain", "utf-8"))

        if pdf_bytes:
            import tempfile
            import os
            
            # Сохраняем PDF во временный файл
            pdf_filename = "audit_%s.pdf" % audit_id
            tmp_path = os.path.join(tempfile.gettempdir(), pdf_filename)
            with open(tmp_path, 'wb') as f:
                f.write(pdf_bytes)
            
            # Читаем обратно и прикрепляем
            with open(tmp_path, 'rb') as f:
                att = MIMEApplication(f.read(), _subtype="pdf")
                att.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=pdf_filename
                )
                msg.attach(att)
            
            print("EmailService: PDF attached from %s, %d bytes" % (tmp_path, len(pdf_bytes)))
            
            # Удаляем временный файл
            try:
                os.remove(tmp_path)
            except:
                pass

        if self.provider == "postbox":
            sender = self.postbox_from_email or self.from_email
            from_header = (
                "%s <%s>" % (self.postbox_from_name, sender)
                if self.postbox_from_name else sender
            )
            try:
                msg.replace_header("From", from_header)
            except KeyError:
                msg["From"] = from_header
            sent_ok = self._send_raw_via_postbox(to_email, msg.as_string().encode("utf-8"))
            if sent_ok:
                print("EmailService: sent via Postbox to %s" % to_email)
            return sent_ok

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_password:
                    try:
                        server.login(self.smtp_user, self.smtp_password)
                    except Exception:
                        pass
                server.sendmail(self.from_email, [to_email], msg.as_string())
            print("EmailService: sent to %s" % to_email)
            try:
                from app.services.baserow_service import baserow_service
                req_data = audit_data.get("request", {}) or {}
                baserow_service.create_lead(
                    contact_email=to_email,
                    contact_name=req_data.get("contact_name", ""),
                    audit_id=audit_id,
                    industry=req_data.get("company_industry", ""),
                    company_size=req_data.get("company_size", ""),
                    composite_score=composite,
                    maturity_level=level,
                    source="email_request",
                )
            except Exception as lead_err:
                print("EmailService: lead creation failed: %s" % lead_err)
            return True
        except Exception as e:
            print("EmailService: send failed: %s" % e)
            return False

email_service = EmailService()
