"""
Baserow CRM Integration Service.
Динамический маппинг логических полей на реальные имена колонок таблицы.
"""
import os
from datetime import datetime

import httpx

FIELD_VARIANTS = {
    "name": ["Имя", "Name", "Имя контакта", "Контакт"],
    "email": ["Email", "E-mail", "Почта"],
    "audit_id": ["Audit ID", "Аудит ID", "ID аудита", "audit_id"],
    "industry": ["Отрасль", "Industry"],
    "company_size": ["Размер компании", "Размер", "Company size"],
    "score": ["Балл зрелости", "Балл", "Score", "Комплексная оценка"],
    "level": ["Уровень зрелости", "Уровень", "Level"],
    "service": ["Интересующая услуга", "Услуга", "Service"],
    "source": ["Источник", "Source"],
    "created_at": ["Дата создания", "Дата", "Created"],
}


class BaserowService:
    def __init__(self):
        self.api_token = os.getenv("BASEROW_API_TOKEN", "")
        self.base_url = os.getenv("BASEROW_URL", "http://baserow:80")
        self.leads_table_id = os.getenv("BASEROW_LEADS_TABLE_ID", "")
        self.enabled = bool(self.api_token and self.leads_table_id)
        self._fields_cache = None

        if self.enabled:
            print("BaserowService: enabled (table_id=%s)" % self.leads_table_id)
        else:
            print("BaserowService: disabled (missing env vars)")

    def _get_field_names(self):
        if self._fields_cache is not None:
            return self._fields_cache
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(
                    "%s/api/database/fields/table/%s/" % (self.base_url, self.leads_table_id),
                    headers={"Authorization": "Token %s" % self.api_token},
                )
                if resp.status_code == 200:
                    self._fields_cache = [f["name"] for f in resp.json()]
                else:
                    print("BaserowService: fields fetch %s" % resp.status_code)
                    self._fields_cache = []
        except Exception as e:
            print("BaserowService: fields fetch error: %s" % e)
            self._fields_cache = []
        return self._fields_cache

    def _map_payload(self, logical):
        names = self._get_field_names()
        payload = {}
        for key, value in logical.items():
            if value in ("", None):
                continue
            for variant in FIELD_VARIANTS.get(key, []):
                if variant in names:
                    payload[variant] = value
                    break
        return payload

    def create_lead(
        self,
        contact_email,
        contact_name="",
        audit_id="",
        industry="",
        company_size="",
        composite_score=None,
        maturity_level="",
        service_interest="",
        source="upsell_funnel",
    ) -> bool:
        if not self.enabled:
            print("BaserowService: disabled, skipping lead")
            return False

        logical = {
            "name": contact_name or "Не указано",
            "email": contact_email,
            "audit_id": audit_id,
            "industry": industry or "Не указана",
            "company_size": company_size,
            "score": composite_score,
            "level": maturity_level,
            "service": service_interest,
            "source": source,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
        }
        payload = self._map_payload(logical)
        if not payload:
            print("BaserowService: empty payload after mapping, skipping")
            return False

        url = "%s/api/database/rows/table/%s/?user_field_names=true" % (
            self.base_url, self.leads_table_id
        )
        try:
            with httpx.Client(timeout=15) as client:
                resp = client.post(
                    url,
                    json=payload,
                    headers={
                        "Authorization": "Token %s" % self.api_token,
                        "Content-Type": "application/json",
                    },
                )
                if resp.status_code in (200, 201):
                    print("BaserowService: lead created (id=%s)" % resp.json().get("id"))
                    return True
                print("BaserowService: create failed %s: %s" % (resp.status_code, resp.text[:200]))
                return False
        except Exception as e:
            print("BaserowService: error: %s" % e)
            return False


baserow_service = BaserowService()
