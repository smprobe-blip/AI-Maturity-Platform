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
            return True
        except Exception as e:
            print("EmailService: send failed: %s" % e)
            return False

email_service = EmailService()
