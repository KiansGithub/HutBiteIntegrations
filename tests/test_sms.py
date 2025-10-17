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
        customer_phone="+1987654321",
        order_amount="$25.50",
        order_ref="ORD123"
    )
    
    assert response.status == SMSStatus.success
    assert response.sid == "test_sid_123"
    assert "SMS sent successfully" in response.message
    
    # Verify Twilio was called with correct parameters
    mock_twilio_client.messages.create.assert_called_once()
    call_args = mock_twilio_client.messages.create.call_args
    assert call_args[1]['to'] == "+1987654321"
    assert "El Curioso" in call_args[1]['body']
    assert "John Doe" in call_args[1]['body']
    assert "$25.50" in call_args[1]['body']
    assert "ORD123" in call_args[1]['body']

def test_send_order_notification_without_ref(sms_service_with_mock, mock_twilio_client):
    """Test order notification SMS without order reference"""
    response = sms_service_with_mock.send_order_notification(
        restaurant_name="Pizza Palace",
        customer_name="Jane Smith",
        customer_phone="+1555123456",
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
        customer_phone="1234567890",  # No + prefix
        order_amount="$10.00"
    )
    
    assert response.status == SMSStatus.success
    call_args = mock_twilio_client.messages.create.call_args
    assert call_args[1]['to'] == "+1234567890"

@patch('app.services.sms.settings')
def test_sms_disabled(mock_settings):
    """Test SMS service when disabled"""
    mock_settings.SMS_ENABLED = False
    
    service = SMSService()
    response = service.send_order_notification(
        restaurant_name="Test",
        customer_name="Test",
        customer_phone="+1234567890",
        order_amount="$10.00"
    )
    
    assert response.status == SMSStatus.disabled
    assert "SMS service is disabled" in response.message