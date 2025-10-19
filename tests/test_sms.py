import pytest
from unittest.mock import Mock, patch
from app.services.sms import SMSService
from app.schemas.sms import SMSStatus

@pytest.fixture
def mock_twilio_client():
    with patch('app.services.sms.Client') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Mock successful message creation
        mock_message = Mock()
        mock_message.sid = "test_sid_123"
        mock_instance.messages.create.return_value = mock_message
        
        yield mock_instance

@pytest.fixture
def sms_service_with_mock(mock_twilio_client):
    with patch('app.services.sms.settings') as mock_settings:
        mock_settings.SMS_ENABLED = True
        mock_settings.TWILIO_ACCOUNT_SID = "test_sid"
        mock_settings.TWILIO_AUTH_TOKEN = "test_token"
        mock_settings.TWILIO_PHONE_NUMBER = "+1234567890"
        
        service = SMSService()
        service.client = mock_twilio_client
        return service

def test_send_order_notification_success(sms_service_with_mock, mock_twilio_client):
    """Test successful order notification SMS"""
    response = sms_service_with_mock.send_order_notification(
        restaurant_name="El Curioso",
        customer_name="John Doe",
        customer_phone="+447756811243",
        order_amount="$25.50",
        order_ref="ORD123"
    )
    
    assert response.status == SMSStatus.success
    assert response.sid == "test_sid_123"
    assert "SMS sent successfully" in response.message
    
    # Verify Twilio was called with correct parameters
    mock_twilio_client.messages.create.assert_called_once()
    call_args = mock_twilio_client.messages.create.call_args
    assert call_args[1]['to'] == "+447756811243"
    assert "El Curioso" in call_args[1]['body']
    assert "John Doe" in call_args[1]['body']
    assert "$25.50" in call_args[1]['body']
    assert "ORD123" in call_args[1]['body']

def test_send_order_notification_without_ref(sms_service_with_mock, mock_twilio_client):
    """Test order notification SMS without order reference"""
    response = sms_service_with_mock.send_order_notification(
        restaurant_name="Pizza Palace",
        customer_name="Jane Smith",
        customer_phone="+447756811243",
        order_amount="$18.75"
    )
    
    assert response.status == SMSStatus.success
    call_args = mock_twilio_client.messages.create.call_args
    assert "Pizza Palace" in call_args[1]['body']
    assert "Jane Smith" in call_args[1]['body']
    assert "$18.75" in call_args[1]['body']
    # Should not contain order reference
    assert "Order #" not in call_args[1]['body']

def test_phone_number_formatting(sms_service_with_mock, mock_twilio_client):
    """Test phone number formatting"""
    response = sms_service_with_mock.send_order_notification(
        restaurant_name="Test Restaurant",
        customer_name="Test Customer",
        customer_phone="+447756811243",  # No + prefix
        order_amount="$10.00",
        order_ref="ORD123"
    )
    
    assert response.status == SMSStatus.success
    call_args = mock_twilio_client.messages.create.call_args
    assert call_args[1]['to'] == "+447756811243"

@patch('app.services.sms.settings')
def test_sms_disabled(mock_settings):
    """Test SMS service when disabled"""
    mock_settings.SMS_ENABLED = False
    
    service = SMSService()
    response = service.send_order_notification(
        restaurant_name="Test",
        customer_name="Test",
        customer_phone="+447756811243",
        order_amount="$10.00",
        order_ref="ORD123"
    )
    
    assert response.status == SMSStatus.disabled
    assert "SMS service is disabled" in response.message

def test_real_sms_integration():
    """
    Integration test that sends a real SMS 
    Only runs if Twilio credentials are available in environment
    """
    import os 
    from dotenv import load_dotenv 
    from pathlib import Path
    from app.services.sms import SMSService 

    env_path = Path(__file__).parent.parent / "app" / ".env"
    load_dotenv(env_path)
    
    # Skip test if Twilio credentials are not available 
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    phone_number = os.getenv('TWILIO_PHONE_NUMBER')
    test_recipient = os.getenv('TEST_SMS_RECIPIENT')

    print(f"🔍 Debug - Environment variables:")
    print(f"  TWILIO_ACCOUNT_SID: {'✅ Set' if account_sid else '❌ Missing'}")
    print(f"  TWILIO_AUTH_TOKEN: {'✅ Set' if auth_token else '❌ Missing'}")
    print(f"  TWILIO_PHONE_NUMBER: {'✅ Set' if phone_number else '❌ Missing'}")
    print(f"  TEST_SMS_RECIPIENT: {'✅ Set' if test_recipient else '❌ Missing'}")

    if not all([account_sid, auth_token, phone_number, test_recipient]):
        pytest.skip("Twilio credentials or test recipient not available")

    # Create a real SMS service instance 
    with patch('app.services.sms.settings') as mock_settings: 
        mock_settings.SMS_ENABLED = True 
        mock_settings.TWILIO_ACCOUNT_SID = account_sid 
        mock_settings.TWILIO_AUTH_TOKEN = auth_token 
        mock_settings.TWILIO_PHONE_NUMBER = phone_number 

        service = SMSService()

        # Send a real test SMS 
        response = service.send_order_notification(
            restaurant_name="Test Restaurant (Integration Test)", 
            customer_name="Test Customer",
            customer_phone=test_recipient, 
            order_amount="15.99",
            order_ref="TEST123"
        )

        # Verify the response 
        assert response.status == SMSStatus.success 
        assert response.sid is not None 
        assert "SMS sent successfully" in response.message 

        print(f"✅ Real SMS sent successfully! SID: {response.sid}")
        print(f"📱 Check your phone ({test_recipient}) for the message")