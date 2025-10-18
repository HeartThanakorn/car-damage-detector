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
