#!/usr/bin/env python3
"""
RICK Trading System - Alert Notifier
Sends alerts via configured channels (email, webhook, etc.) from env file
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Optional

class AlertNotifier:
    def __init__(self):
        # Load alert configuration from environment
        self.email_enabled = os.getenv('ALERT_EMAIL_ENABLED', 'false').lower() == 'true'
        self.webhook_enabled = os.getenv('ALERT_WEBHOOK_ENABLED', 'false').lower() == 'true'
        self.telegram_enabled = os.getenv('ALERT_TELEGRAM_ENABLED', 'false').lower() == 'true'
        
        # Email settings
        self.email_to = os.getenv('ALERT_EMAIL_TO', '')
        self.email_from = os.getenv('ALERT_EMAIL_FROM', '')
        self.smtp_server = os.getenv('ALERT_SMTP_SERVER', '')
        self.smtp_port = os.getenv('ALERT_SMTP_PORT', '587')
        self.smtp_username = os.getenv('ALERT_SMTP_USERNAME', '')
        self.smtp_password = os.getenv('ALERT_SMTP_PASSWORD', '')
        
        # Webhook settings
        self.webhook_url = os.getenv('ALERT_WEBHOOK_URL', '')
        
        # Telegram settings
        self.telegram_bot_token = os.getenv('ALERT_TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.getenv('ALERT_TELEGRAM_CHAT_ID', '')
    
    def send_alert(self, title: str, message: str, level: str = "INFO") -> bool:
        """
        Send alert through all configured channels
        
        Args:
            title: Alert title
            message: Alert message
            level: INFO, WARNING, ERROR, CRITICAL
        
        Returns:
            True if at least one channel succeeded
        """
        success = False
        
        if self.webhook_enabled and self.webhook_url:
            success = self._send_webhook(title, message, level) or success
        
        if self.telegram_enabled and self.telegram_bot_token and self.telegram_chat_id:
            success = self._send_telegram(title, message, level) or success
        
        if self.email_enabled and self.email_to:
            success = self._send_email(title, message, level) or success
        
        return success
    
    def _send_webhook(self, title: str, message: str, level: str) -> bool:
        """Send alert via webhook"""
        try:
            payload = {
                'title': title,
                'message': message,
                'level': level,
                'timestamp': datetime.now().isoformat(),
                'system': 'RICK Trading System'
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook alert failed: {e}")
            return False
    
    def _send_telegram(self, title: str, message: str, level: str) -> bool:
        """Send alert via Telegram"""
        try:
            emoji = {
                'INFO': 'ℹ️',
                'WARNING': '⚠️',
                'ERROR': '❌',
                'CRITICAL': '🚨'
            }.get(level, 'ℹ️')
            
            text = f"{emoji} *{title}*\n\n{message}\n\n_{datetime.now().strftime('%Y-%m-%d %I:%M:%S %p EST')}_"
            
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram alert failed: {e}")
            return False
    
    def _send_email(self, title: str, message: str, level: str) -> bool:
        """Send alert via email"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[RICK Trading] {level}: {title}"
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            
            body = f"""
RICK Trading System Alert

Level: {level}
Time: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p EST')}

{title}

{message}

---
RICK Trading System
Automated Alert
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, int(self.smtp_port)) as server:
                server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Email alert failed: {e}")
            return False


# Convenience functions
def send_system_alert(title: str, message: str, level: str = "INFO"):
    """Send system alert through configured channels"""
    notifier = AlertNotifier()
    return notifier.send_alert(title, message, level)


def send_shutdown_alert():
    """Send alert when system shuts down unexpectedly"""
    return send_system_alert(
        "System Shutdown Detected",
        "RICK Trading System has been shut down. Trading engines stopped.",
        "WARNING"
    )


def send_startup_alert():
    """Send alert when system starts up"""
    return send_system_alert(
        "System Starting Up",
        "RICK Trading System is initializing...",
        "INFO"
    )


def send_restart_alert():
    """Send alert when system restarts"""
    return send_system_alert(
        "System Restarted",
        "RICK Trading System has been restarted automatically.",
        "WARNING"
    )


if __name__ == "__main__":
    # Test alerts
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == "startup":
            send_startup_alert()
            print("✅ Startup alert sent")
        elif action == "shutdown":
            send_shutdown_alert()
            print("✅ Shutdown alert sent")
        elif action == "restart":
            send_restart_alert()
            print("✅ Restart alert sent")
        else:
            send_system_alert("Test Alert", f"Testing alert system: {action}", "INFO")
            print("✅ Test alert sent")
    else:
        print("Alert Notifier Configuration:")
        notifier = AlertNotifier()
        print(f"  Email: {'✅ Enabled' if notifier.email_enabled else '❌ Disabled'}")
        print(f"  Webhook: {'✅ Enabled' if notifier.webhook_enabled else '❌ Disabled'}")
        print(f"  Telegram: {'✅ Enabled' if notifier.telegram_enabled else '❌ Disabled'}")
        print("")
        print("Usage: python3 alert_notifier.py [startup|shutdown|restart|test]")
