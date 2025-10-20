import base64
import json
import logging
from typing import Optional

import httpx

from app.core.config import settings
from app.schemas.sms import SMSResponse, SMSStatus

logger = logging.getLogger(__name__)

CLICKSEND_URL = "https://rest.clicksend.com/v3/sms/send"


def _e164_uk(number: str) -> str:
    """
    Minimal E.164 normaliser for UK numbers.
    - If already starts with '+', return as-is.
    - If starts with '0', replace leading 0 with +44.
    - Else if startswith '44', prefix with '+'.
    - Else if looks like 10-11 digits, assume +44.
    """
    n = number.strip().replace(" ", "")
    if n.startswith("+"):
        return n
    if n.startswith("00"):
        return "+" + n[2:]
    if n.startswith("0"):
        return "+44" + n[1:]
    if n.startswith("44"):
        return "+" + n
    if n.isdigit() and 9 <= len(n) <= 11:
        return "+44" + n
    return n  # last resort, let API validate


class SMSService:
    def __init__(self):
        self.enabled = bool(
            settings.SMS_ENABLED
            and settings.CLICKSEND_USERNAME
            and settings.CLICKSEND_API_KEY
        )
        if not self.enabled:
            logger.info("SMS service disabled or missing ClickSend credentials")
        # Prebuild auth header if enabled
        if self.enabled:
            token = f"{settings.CLICKSEND_USERNAME}:{settings.CLICKSEND_API_KEY}".encode()
            self.auth_header = "Basic " + base64.b64encode(token).decode()
        else:
            self.auth_header = None

        self.sender = settings.SMS_SENDER  # optional

    def _send_via_clicksend(self, to_phone: str, message: str) -> SMSResponse:
        if not self.enabled or not self.auth_header:
            return SMSResponse(status=SMSStatus.disabled, message="SMS service is disabled")

        to = _e164_uk(to_phone)
        payload = {
            "shorten_urls": False,
            "messages": [
                {
                    "source": "python",
                    "to": to,
                    "body": message,
                    **({"_from": self.sender} if self.sender else {}),
                }
            ],
        }

        try:
            resp = requests.post(
                CLICKSEND_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": self.auth_header,
                },
                data=json.dumps(payload),
                timeout=15,
            )
            data = resp.json() if resp.content else {}
            if resp.status_code == 200 and data.get("response_code") == "SUCCESS":
                # ClickSend returns message details in data["data"]["messages"]
                messages = (data.get("data") or {}).get("messages") or []
                # There isn't a Twilio-style SID; capture ClickSend message ID if present
                msg_id = messages[0].get("message_id") if messages else None
                logger.info(f"SMS queued successfully via ClickSend. ID: {msg_id}")
                return SMSResponse(
                    status=SMSStatus.success,
                    message="SMS queued for delivery",
                    sid=msg_id,
                )
            else:
                # Surface ClickSend error details if available
                err_msg = (
                    data.get("response_msg")
                    or (data.get("data") or {}).get("messages")
                    or data
                )
                logger.error(f"ClickSend error: {err_msg}")
                return SMSResponse(
                    status=SMSStatus.error,
                    message=f"ClickSend error: {err_msg}",
                    error_code=data.get("response_code"),
                )
        except requests.RequestException as e:
            logger.error(f"HTTP error sending SMS via ClickSend: {e}")
            return SMSResponse(status=SMSStatus.error, message=f"HTTP error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending SMS via ClickSend: {e}")
            return SMSResponse(status=SMSStatus.error, message=f"Unexpected error: {e}")

    # Public API mirrors your existing service
    def send_order_notification(
        self,
        restaurant_name: str,
        customer_name: str,
        customer_phone: str,
        order_amount: str,
        order_ref: Optional[str] = None,
    ) -> SMSResponse:
        if not self.enabled:
            return SMSResponse(status=SMSStatus.disabled, message="SMS service is disabled")

        msg = f"You have an order for {restaurant_name} by {customer_name} for {order_amount}"
        if order_ref:
            msg += f" (Order #{order_ref})"
        msg += ". Thank you for your order!"
        return self._send_via_clicksend(customer_phone, msg)

    def send_custom_sms(self, phone_number: str, message: str) -> SMSResponse:
        if not self.enabled:
            return SMSResponse(status=SMSStatus.disabled, message="SMS service is disabled")
        return self._send_via_clicksend(phone_number, message)

# Create a singleton instance
sms_service = SMSService()

