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
    
    def send_audit_report(
        self,
        to_email: str,
        company_name: str,
        score: float,
        level: str,
        audit_id: str
    ) -> bool:
        """Send audit report email."""
        subject = f"AI Maturity Assessment Report: {company_name}"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #667eea;">AI Maturity Assessment Report</h1>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h2 style="color: #333; margin-top: 0;">{company_name}</h2>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Composite Score:</td>
                            <td style="padding: 8px 0; font-weight: bold; color: #667eea; font-size: 18px;">{score:.1f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Maturity Level:</td>
                            <td style="padding: 8px 0; font-weight: bold;">{level}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Audit ID:</td>
                            <td style="padding: 8px 0; font-family: monospace; font-size: 12px;">{audit_id}</td>
                        </tr>
                    </table>
                </div>
                
                <p>Thank you for completing the AI Maturity Assessment!</p>
                <p>The full detailed report is available in the admin panel.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">AI Maturity Platform</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email([to_email], subject, html_body)
    
    def get_status(self) -> dict:
        """Get email service status."""
        return {
            "smtp_host": self.smtp_host,
            "smtp_port": self.smtp_port,
            "from_email": self.from_email,
            "configured": bool(self.smtp_host and self.smtp_port)
        }


email_service = EmailService()
