from fastapi import APIRouter, HTTPException, status 
from app.schemas.sms import OrderSMSRequest, SMSTestRequest, SMSResponse, SMSStatus 
from app.services.sms import sms_service 
import logging 

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sms", tags=["SMS Notifications"])

@router.post("/send-order-notification", response_model=SMSResponse)
async def send_order_notification(request: OrderSMSRequest):
    """
    Send SMS notification for a new order 

    The message format will be:
    "You have an order for [Restaurant Name] by [Customer Name] for [Amount] (Order #[Ref])"
    """
    try: 
        response = sms_service.send_order_notification(
            restaurant_name=request.restaurant_name, 
            customer_name=request.customer_name, 
            customer_phone=request.customer_phone, 
            order_amount=request.order_amount, 
            order_ref=request.order_ref 
        )

        if response.status == SMSStatus.error: 
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Failed to send SMS: {response.message}"
            )
        
        return response 

    except Exception as e:
        logger.error(f"Error in send_order_notification endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error while sending SMS"
        )

@router.post("/send-test", response_model=SMSResponse)
async def send_test_sms(request: SMSTestRequest):
    """
    Send a test SMS message
    """
    try:
        response = sms_service.send_custom_sms(
            phone_number=request.phone_number, 
            message=request.message
        )

        if response.status == SMSStatus.error: 
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Failed to send SMS: {response.message}"
            )

        return response 
    
    except Exception as e:
        logger.error(f"Error in send_test_sms endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error while sending SMS"
        )

@router.get("/status")
async def get_sms_status():
    """
    Check SMS service status
    """
    return {
        "sms_enabled": sms_service.enabled,
        "service_status": "active" if sms_service.enabled else "disabled"
    }