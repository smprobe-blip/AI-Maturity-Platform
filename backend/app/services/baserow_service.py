"""Baserow CRM Integration Service."""
import os
from datetime import datetime
import httpx

# Точные имена полей таблицы "Лиды из аудита" (table_id=513)
# Используем как fallback, если API-запрос полей не проходит
KNOWN_FIELDS = [
    "Имя", "Email", "Audit ID", "Отрасль", "Размер компании",
    "Балл зрелости", "Уровень зрелости", "Интересующая услуга",
    "Источник", "Дата создания",
]

FIELD_MAP = {
    "name": "Имя",
    "email": "Email",
    "audit_id": "Audit ID",
    "industry": "Отрасль",
    "company_size": "Размер компании",
    "score": "Балл зрелости",
    "level": "Уровень зрелости",
    "service": "Интересующая услуга",
    "source": "Источник",
    "created_at": "Дата создания",
}


class BaserowService:
    def __init__(self):
        self.api_token = os.getenv("BASEROW_API_TOKEN", "")
        self.base_url = os.getenv("BASEROW_URL", "http://baserow:80")
        self.leads_table_id = os.getenv("BASEROW_LEADS_TABLE_ID", "")
        self.enabled = bool(self.api_token and self.leads_table_id)
        print("BaserowService: enabled=%s table=%s url=%s" % (
            self.enabled, self.leads_table_id, self.base_url))

    def _build_payload(self, logical):
        """Строит payload из логического dict, игнорируя пустые значения."""
        payload = {}
        for key, target_field in FIELD_MAP.items():
            value = logical.get(key)
            if value in ("", None):
                continue
            # Для чисел убеждаемся, что передаётся число, а не None
            if target_field == "Балл зрелости" and not isinstance(value, (int, float)):
                continue
            payload[target_field] = value
        return payload

    def create_lead(self, contact_email, contact_name="", audit_id="", industry="",
                    company_size="", composite_score=None, maturity_level="",
                    service_interest="", source="upsell_funnel"):
        if not self.enabled:
            print("BaserowService: disabled, skipping")
            return False

        logical = {
            "name": contact_name or "Не указано",
            "email": contact_email,
            "audit_id": audit_id,
            "industry": industry or "Не указана",
            "company_size": company_size,
            "score": round(composite_score, 1) if composite_score else None,
            "level": maturity_level,
            "service": service_interest,
            "source": source,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
        }
        payload = self._build_payload(logical)
        if not payload:
            print("BaserowService: empty payload, skipping")
            return False

        print("BaserowService: sending payload: %s" % payload)

        url = "%s/api/database/rows/table/%s/?user_field_names=true" % (
            self.base_url, self.leads_table_id
        )
        try:
            with httpx.Client(timeout=15) as client:
                resp = client.post(url, json=payload, headers={
                    "Authorization": "Token %s" % self.api_token,
                    "Content-Type": "application/json",
                    "Host": "localhost",
                })
                if resp.status_code in (200, 201):
                    print("BaserowService: lead created id=%s" % resp.json().get("id"))
                    return True
                print("BaserowService: create failed %s body=%s" % (
                    resp.status_code, resp.text[:500]))
                return False
        except Exception as e:
            print("BaserowService: error: %s" % e)
            return False


baserow_service = BaserowService()
