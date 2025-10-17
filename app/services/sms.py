import logging
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from app.core.config import settings
from app.schemas.sms import SMSResponse, SMSStatus

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        if settings.SMS_ENABLED:
            try:
                self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                self.from_number = settings.TWILIO_PHONE_NUMBER
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.client = None
        else:
            self.client = None
            logger.info("SMS service is disabled")

    def send_order_notification(
        self, 
        restaurant_name: str, 
        customer_name: str, 
        customer_phone: str, 
        order_amount: str,
        order_ref: Optional[str] = None
    ) -> SMSResponse:
        """
        Send order notification SMS to customer
        Format: "You have an order for [Restaurant Name] by [Customer Name] for [Amount]"
        """
        if not settings.SMS_ENABLED or not self.client:
            return SMSResponse(
                status=SMSStatus.disabled,
                message="SMS service is disabled"
            )

        # Create the message
        message = f"You have an order for {restaurant_name} by {customer_name} for {order_amount}"
        if order_ref:
            message += f" (Order #{order_ref})"
        message += ". Thank you for your order!"

        return self._send_sms(customer_phone, message)

    def send_custom_sms(self, phone_number: str, message: str) -> SMSResponse:
        """Send a custom SMS message"""
        if not settings.SMS_ENABLED or not self.client:
            return SMSResponse(
                status=SMSStatus.disabled,
                message="SMS service is disabled"
            )

        return self._send_sms(phone_number, message)

    def _send_sms(self, to_phone: str, message: str) -> SMSResponse:
        """Internal method to send SMS via Twilio"""
        try:
            # Validate phone number format
            if not to_phone.startswith('+'):
                logger.warning(f"Phone number {to_phone} doesn't start with +, adding +1")
                to_phone = f"+1{to_phone.lstrip('1')}"

            # Send SMS via Twilio
            twilio_message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_phone
            )

            logger.info(f"SMS sent successfully. SID: {twilio_message.sid}")
            return SMSResponse(
                status=SMSStatus.success,
                message="SMS sent successfully",
                sid=twilio_message.sid
            )

        except TwilioException as e:
            logger.error(f"Twilio error sending SMS to {to_phone}: {e}")
            return SMSResponse(
                status=SMSStatus.error,
                message=f"Twilio error: {str(e)}",
                error_code=getattr(e, 'code', None)
            )
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {to_phone}: {e}")
            return SMSResponse(
                status=SMSStatus.error,
                message=f"Unexpected error: {str(e)}"
            )

# Create a singleton instance
sms_service = SMSService()

