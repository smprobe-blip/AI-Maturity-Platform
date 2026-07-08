"""Email Service for sending notifications."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.use_tls = settings.smtp_use_tls
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """Send email via SMTP."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            
            if text_body:
                msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info("email_sent", to=to_emails, subject=subject)
            return True
        except Exception as e:
            logger.error("email_send_failed", error=str(e), to=to_emails)
            return False
    
    def send_audit_notification(self, to_emails: List[str], company_name: str, score: float):
        """Send audit completion notification."""
        subject = f"AI Maturity Assessment Complete: {company_name}"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #667eea;">AI Maturity Assessment Complete</h2>
            <p>Company: <strong>{company_name}</strong></p>
            <p>Composite Score: <strong>{score:.1f}</strong></p>
            <p>The full report is available in the admin panel.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">AI Maturity Platform</p>
        </body>
        </html>
        """
        return self.send_email(to_emails, subject, html_body)
    
    def get_status(self) -> dict:
        """Get email service status."""
        return {
            "smtp_host": self.smtp_host,
            "smtp_port": self.smtp_port,
            "from_email": self.from_email,
            "configured": bool(self.smtp_host and self.smtp_port)
        }


email_service = EmailService()
