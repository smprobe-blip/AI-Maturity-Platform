#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Смоук-тест полного цикла платформы (ручной запуск).

Проверяет: создание аудита → сохранение → PDF-отчёт → лид в CRM → удаление.

Запуск:
  export SMOKE_BASE_URL=https://audit.netbrainpower.ru
  export SMOKE_ADMIN_USER=admin
  export SMOKE_ADMIN_PASSWORD=...
  python3 scripts/smoke_audit.py            # полный цикл
  python3 scripts/smoke_audit.py --no-cleanup   # оставить тестовый аудит
  python3 scripts/smoke_audit.py --with-email user@example.com  # + письмо с отчётом

Каждый шаг печатает PASS/FAIL; код выхода 0 — всё прошло, 1 — есть FAIL.
"""
import argparse
import json
import os
import sys
import time
import ssl
import urllib.error
import urllib.parse
import urllib.request

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()

BASE = os.environ.get("SMOKE_BASE_URL", "https://audit.netbrainpower.ru")
ADMIN_USER = os.environ.get("SMOKE_ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("SMOKE_ADMIN_PASSWORD", "")
KEYCLOAK_URL = os.environ.get("SMOKE_KEYCLOAK_URL", BASE + "/auth")
SOURCE = "smoke_test"

RESULTS = []


def step(name, fn):
    t0 = time.time()
    try:
        detail = fn() or ""
        dt = f"{time.time() - t0:.1f}s"
        RESULTS.append((name, "PASS", f"{detail} ({dt})"))
        print(f"  ✓ PASS  {name:42} {detail} ({dt})")
        return True
    except AssertionError as e:
        RESULTS.append((name, "FAIL", str(e)))
        print(f"  ✗ FAIL  {name:42} {e}")
        return False
    except Exception as e:
        RESULTS.append((name, "FAIL", f"{type(e).__name__}: {e}"))
        print(f"  ✗ FAIL  {name:42} {type(e).__name__}: {e}")
        return False


def http(method, url, token=None, payload=None, timeout=30):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX)
        raw = resp.read()
        ct = resp.headers.get("Content-Type", "")
        try:
            return resp.status, (json.loads(raw) if "json" in ct else raw)
        except json.JSONDecodeError:
            return resp.status, raw
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, body


def admin_token():
    url = KEYCLOAK_URL + "/realms/ai-maturity/protocol/openid-connect/token"
    data = urllib.parse.urlencode({
        "grant_type": "password", "client_id": "frontend-spa",
        "username": ADMIN_USER, "password": ADMIN_PASSWORD,
    }).encode()
    resp = urllib.request.urlopen(url, data=data, timeout=20, context=SSL_CTX)
    return json.load(resp)["access_token"]


RESPONSES = {str(d): {str(q): 4 for q in range(1, 6)} for d in range(1, 8)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-cleanup", action="store_true", help="не удалять тестовый аудит")
    ap.add_argument("--with-email", metavar="EMAIL", help="дополнительно отправить отчёт на email")
    args = ap.parse_args()

    if not ADMIN_PASSWORD:
        print("SMOKE_ADMIN_PASSWORD не задан")
        return 1

    api = BASE + "/api/v1"
    print(f"Смоук-тест: {BASE}")
    print("-" * 72)

    state = {"token": None, "audit_id": None}

    def s1():
        state["token"] = admin_token()
        assert len(state["token"]) > 100, "токен не получен"
    step("1. Аутентификация администратора (Keycloak)", s1)

    tok = state["token"]

    def s2():
        st, d = http("POST", api + "/public/audits/express", payload={
            "company_industry": "it", "company_size": "small",
            "contact_email": "smoke-test@netbrainpower.ru",
            "contact_name": "SMOKE TEST", "report_type": "express",
            "responses": RESPONSES, "pdn_consent": True, "source": SOURCE,
        })
        assert st == 201, f"HTTP {st}: {json.dumps(d, ensure_ascii=False)[:120]}"
        state["audit_id"] = d.get("audit_id") or d.get("id")
        assert state["audit_id"], "нет audit_id в ответе"
    step("2. Создание аудита (public API, 35 ответов)", s2)

    aid = state["audit_id"]

    def s3():
        st, d = http("GET", api + f"/public/audits/{aid}")
        assert st == 200, f"HTTP {st}"
        score = (d.get("calculated_indices") or {}).get("composite_score")
        assert score is not None, "composite_score отсутствует"
        assert 0 <= float(score) <= 5, f"composite_score вне диапазона: {score}"
    step("3. Чтение аудита, расчёт индекса", s3)

    def s4():
        st, raw = http("GET", api + f"/admin/audits/{aid}/report/pdf", token=tok, timeout=60)
        assert st == 200, f"HTTP {st}"
        assert isinstance(raw, bytes) and len(raw) > 10000, f"PDF подозрительно мал: {len(raw)} байт"
    step("4. PDF-отчёт (генерация, >10 КБ)", s4)

    def s5():
        st, d = http("GET", api + f"/admin/audits?search=smoke-test@netbrainpower.ru", token=tok)
        assert st == 200, f"HTTP {st}"
        found = [a for a in (d.get("items") or []) if a.get("audit_id") == aid]
        assert found, "аудит не найден в списке"
        assert (found[0].get("source") or "") == SOURCE, "source != smoke_test"
    step("5. Аудит в списке с source=smoke_test", s5)

    def s6():
        url = api + "/admin/leads?limit=200"
        st, d = http("GET", url, token=tok)
        if st != 200:
            req_dbg = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
            hdrs = {}
            try:
                probe = urllib.request.urlopen(req_dbg, timeout=20, context=SSL_CTX)
                hdrs = {"status": probe.status, "server": probe.headers.get("server", ""), "body": probe.read()[:60].decode("utf-8", "ignore")}
            except urllib.error.HTTPError as e2:
                hdrs = {"status": e2.code, "server": e2.headers.get("server", ""), "body": e2.read()[:60].decode("utf-8", "ignore")}
            assert False, f"HTTP {st} на {url}; повторный запрос: {hdrs}"
        found = []
        for attempt in range(6):  # синк лида может отставать — до ~10 с
            rows = d.get("items") if isinstance(d, dict) else d
            found = [r for r in (rows or []) if str(r.get("audit_id") or r.get("Audit ID", "")) == aid]
            if found:
                break
            time.sleep(2)
            st, d = http("GET", url, token=tok)
        assert found, f"лид CRM не создан (попытки: {attempt + 1}, всего лидов: {d.get('total', '?') if isinstance(d, dict) else '?'})"
        rows = d.get("items") if isinstance(d, dict) else d
        found = [r for r in (rows or []) if str(r.get("Audit ID", "")) == aid]
    step("6. Лид в CRM (Baserow)", s6)

    if args.with_email:
        def s7():
            st, d = http("POST", api + f"/public/audits/{aid}/email",
                         payload={"email": args.with_email}, timeout=90)
            assert st in (200, 202), f"HTTP {st}: {json.dumps(d, ensure_ascii=False)[:120]}"
        step(f"7. Отправка отчёта на email ({args.with_email})", s7)

    if not args.no_cleanup:
        def s8():
            st, d = http("DELETE", api + f"/admin/audits/{aid}", token=tok)
            assert st == 200, f"HTTP {st}: {d}"
        step("8. Удаление тестового аудита (+ лид CRM)", s8)

        def s9():
            st, d = http("GET", api + f"/admin/audits?search=smoke-test@netbrainpower.ru", token=tok)
            assert st == 200, f"HTTP {st}"
            left = [a for a in (d.get("items") or []) if a.get("audit_id") == aid]
            assert not left, "аудит остался после удаления"
        step("9. Проверка: аудит удалён", s9)

    fails = sum(1 for _, s, _ in RESULTS if s == "FAIL")
    print("-" * 72)
    print(f"Итог: {len(RESULTS) - fails}/{len(RESULTS)} шагов PASS" + (f", {fails} FAIL" if fails else " — сервис работоспособен"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
