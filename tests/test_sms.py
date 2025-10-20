import pytest
from unittest.mock import Mock, patch
from app.services.sms import SMSService, _e164_uk
from app.schemas.sms import SMSStatus
import json
import requests

@pytest.fixture
def mock_clicksend_success_response():
    """Mock successful ClickSend API response"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = True
    mock_response.json.return_value = {
        "http_code": 200,
        "response_code": "SUCCESS",
        "response_msg": "Messages queued for delivery.",
        "data": {
            "total_price": 0.0792,
            "total_count": 1,
            "queued_count": 1,
            "messages": [
                {
                    "message_id": "test_message_id_123",
                    "to": "+447756811243",
                    "body": "Test message",
                    "status": "SUCCESS"
                }
            ],
            "blocked_count": 0
        }
    }
    return mock_response

@pytest.fixture
def mock_clicksend_error_response():
    """Mock error ClickSend API response"""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.content = True
    mock_response.json.return_value = {
        "http_code": 400,
        "response_code": "BAD_REQUEST",
        "response_msg": "Invalid phone number",
        "data": {}
    }
    return mock_response

@pytest.fixture
def sms_service_with_mock():
    with patch('app.services.sms.settings') as mock_settings:
        mock_settings.SMS_ENABLED = True
        mock_settings.CLICKSEND_USERNAME = "test_username"
        mock_settings.CLICKSEND_API_KEY = "test_api_key"
        mock_settings.SMS_SENDER = "HUTBITE"
        
        service = SMSService()
        return service

@patch('app.services.sms.requests.post')
def test_send_order_notification_success(mock_post, sms_service_with_mock, mock_clicksend_success_response):
    """Test successful order notification SMS"""
    mock_post.return_value = mock_clicksend_success_response
    
    response = sms_service_with_mock.send_order_notification(
        restaurant_name="El Curioso",
        customer_name="John Doe",
        customer_phone="+447756811243",
        order_amount="$25.50",
        order_ref="ORD123"
    )
    
    assert response.status == SMSStatus.success
    assert response.sid == "test_message_id_123"
    assert "SMS queued for delivery" in response.message
    
    # Verify ClickSend was called with correct parameters
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    
    # Check URL
    assert call_args[0][0] == "https://rest.clicksend.com/v3/sms/send"
    
    # Check headers
    headers = call_args[1]['headers']
    assert "Authorization" in headers
    assert headers["Content-Type"] == "application/json"
    
    # Check payload
    payload = json.loads(call_args[1]['data'])
    assert payload["messages"][0]["to"] == "+447756811243"
    assert "El Curioso" in payload["messages"][0]["body"]
    assert "John Doe" in payload["messages"][0]["body"]
    assert "$25.50" in payload["messages"][0]["body"]
    assert "ORD123" in payload["messages"][0]["body"]

@patch('app.services.sms.requests.post')
def test_send_order_notification_without_ref(mock_post, sms_service_with_mock, mock_clicksend_success_response):
    """Test order notification SMS without order reference"""
    mock_post.return_value = mock_clicksend_success_response
    
    response = sms_service_with_mock.send_order_notification(
        restaurant_name="Pizza Palace",
        customer_name="Jane Smith",
        customer_phone="+447756811243",
        order_amount="$18.75"
    )
    
    assert response.status == SMSStatus.success
    
    # Check payload
    payload = json.loads(mock_post.call_args[1]['data'])
    message_body = payload["messages"][0]["body"]
    assert "Pizza Palace" in message_body
    assert "Jane Smith" in message_body
    assert "$18.75" in message_body
    # Should not contain order reference
    assert "Order #" not in message_body

@patch('app.services.sms.requests.post')
def test_send_custom_sms(mock_post, sms_service_with_mock, mock_clicksend_success_response):
    """Test custom SMS message"""
    mock_post.return_value = mock_clicksend_success_response
    
    response = sms_service_with_mock.send_custom_sms(
        phone_number="+447756811243",
        message="Test custom message"
    )
    
    assert response.status == SMSStatus.success
    
    # Check payload
    payload = json.loads(mock_post.call_args[1]['data'])
    assert payload["messages"][0]["body"] == "Test custom message"
    assert payload["messages"][0]["to"] == "+447756811243"

def test_phone_number_formatting():
    """Test UK phone number E.164 formatting"""
    # Test cases for UK number formatting
    assert _e164_uk("+447756811243") == "+447756811243"  # Already formatted
    assert _e164_uk("07756811243") == "+447756811243"    # UK mobile
    assert _e164_uk("447756811243") == "+447756811243"   # Without +
    assert _e164_uk("0020123456789") == "+20123456789"   # International with 00
    assert _e164_uk("7756811243") == "+447756811243"     # Assume UK if 10 digits

@patch('app.services.sms.requests.post')
def test_clicksend_error_response(mock_post, sms_service_with_mock, mock_clicksend_error_response):
    """Test ClickSend API error handling"""
    mock_post.return_value = mock_clicksend_error_response
    
    response = sms_service_with_mock.send_custom_sms(
        phone_number="invalid",
        message="Test message"
    )
    
    assert response.status == SMSStatus.error
    assert "ClickSend error" in response.message
    assert response.error_code == "BAD_REQUEST"

@patch('app.services.sms.requests.post')
def test_network_error(mock_post, sms_service_with_mock):
    """Test network error handling"""
    mock_post.side_effect = requests.RequestException("Network error")
    
    response = sms_service_with_mock.send_custom_sms(
        phone_number="+447756811243",
        message="Test message"
    )
    
    assert response.status == SMSStatus.error
    assert "HTTP error" in response.message

@patch('app.services.sms.settings')
def test_sms_disabled(mock_settings):
    """Test SMS service when disabled"""
    mock_settings.SMS_ENABLED = False
    mock_settings.CLICKSEND_USERNAME = None
    mock_settings.CLICKSEND_API_KEY = None
    mock_settings.SMS_SENDER = None
    
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

@patch('app.services.sms.settings')
def test_missing_credentials(mock_settings):
    """Test SMS service with missing credentials"""
    mock_settings.SMS_ENABLED = True
    mock_settings.CLICKSEND_USERNAME = None  # Missing
    mock_settings.CLICKSEND_API_KEY = "test_key"
    mock_settings.SMS_SENDER = None
    
    service = SMSService()
    response = service.send_custom_sms(
        phone_number="+447756811243",
        message="Test message"
    )
    
    assert response.status == SMSStatus.disabled
    assert "SMS service is disabled" in response.message

def test_real_clicksend_integration():
    """
    Integration test that sends a real SMS via ClickSend
    Only runs if ClickSend credentials are available in environment
    """
    import os 
    from dotenv import load_dotenv 
    from pathlib import Path
    from app.services.sms import SMSService 

    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
    
    # Skip test if ClickSend credentials are not available 
    username = os.getenv('CLICKSEND_USERNAME')
    api_key = os.getenv('CLICKSEND_API_KEY')
    test_recipient = os.getenv('TEST_SMS_RECIPIENT')

    print(f"🔍 Debug - Environment variables:")
    print(f"  CLICKSEND_USERNAME: {'✅ Set' if username else '❌ Missing'}")
    print(f"  CLICKSEND_API_KEY: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"  TEST_SMS_RECIPIENT: {'✅ Set' if test_recipient else '❌ Missing'}")

    if not all([username, api_key, test_recipient]):
        pytest.skip("ClickSend credentials or test recipient not available")

    # Create a real SMS service instance 
    with patch('app.services.sms.settings') as mock_settings: 
        mock_settings.SMS_ENABLED = True 
        mock_settings.CLICKSEND_USERNAME = username 
        mock_settings.CLICKSEND_API_KEY = api_key 
        mock_settings.SMS_SENDER = "HUTBITE"

        service = SMSService()

        # Send a real test SMS 
        response = service.send_order_notification(
            restaurant_name="Test Restaurant (ClickSend Integration)", 
            customer_name="Test Customer",
            customer_phone=test_recipient, 
            order_amount="£15.99",
            order_ref="TEST123"
        )

        # Verify the response 
        assert response.status == SMSStatus.success 
        assert response.sid is not None 
        assert "SMS queued for delivery" in response.message 

        print(f"✅ Real SMS sent successfully! Message ID: {response.sid}")
        print(f"📱 Check your phone ({test_recipient}) for the message")