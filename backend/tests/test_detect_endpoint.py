"""
Basic test to verify the /detect endpoint implementation
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from io import BytesIO
from PIL import Image


client = TestClient(app)


def create_test_image(size=(100, 100), format='JPEG'):
    """Create a simple test image in memory"""
    img = Image.new('RGB', size, color='red')
    buf = BytesIO()
    img.save(buf, format=format)
    buf.seek(0)
    return buf


def test_detect_endpoint_validates_file_type():
    """Test that the endpoint rejects non-image files"""
    files = {'file': ('test.txt', b'not an image', 'text/plain')}
    response = client.post('/detect', files=files)
    
    assert response.status_code == 400
    assert 'Invalid file type' in response.json()['detail']


def test_detect_endpoint_validates_file_size():
    """Test that the endpoint rejects files larger than 10MB"""
    # Create a large fake file (11MB)
    large_data = b'x' * (11 * 1024 * 1024)
    files = {'file': ('large.jpg', large_data, 'image/jpeg')}
    response = client.post('/detect', files=files)
    
    assert response.status_code == 413
    assert 'exceeds' in response.json()['detail'].lower()


def test_health_endpoint():
    """Test that the health endpoint works"""
    response = client.get('/health')
    
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'
    assert 'timestamp' in response.json()


def test_error_response_format_for_invalid_file_type():
    """Test that error responses follow the ErrorResponse model format"""
    files = {'file': ('test.pdf', b'fake pdf content', 'application/pdf')}
    response = client.post('/detect', files=files)
    
    assert response.status_code == 400
    json_response = response.json()
    # Verify ErrorResponse format
    assert 'error' in json_response
    assert 'detail' in json_response
    assert json_response['error'] == 'Bad Request'


def test_error_response_format_for_file_size():
    """Test that file size errors return proper ErrorResponse format"""
    large_data = b'x' * (11 * 1024 * 1024)
    files = {'file': ('large.jpg', large_data, 'image/jpeg')}
    response = client.post('/detect', files=files)
    
    assert response.status_code == 413
    json_response = response.json()
    # Verify ErrorResponse format
    assert 'error' in json_response
    assert 'detail' in json_response
    assert json_response['error'] == 'Payload Too Large'
