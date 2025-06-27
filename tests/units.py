# Unit tests

import pytest
import json
from unittest.mock import patch, MagicMock
import os
import sys

# Add the parent directory to sys.path to import the Flask app
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')

sys.path.insert(0, src_path)

# Import your Flask app (assuming it's saved as app.py)
from app import app, r

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_redis():
    """Mock Redis connection for testing."""
    with patch('app.r') as mock_r:
        yield mock_r

class TestFlaskRedisApp:
    
    def test_index_route(self, client):
        """Test the index route returns expected message."""
        response = client.get('/')
        assert response.status_code == 200
        assert response.data.decode() == "Hello from Flask app connected to Redis!"
    
    def test_set_value_success(self, client, mock_redis):
        """Test successful key-value setting."""
        mock_redis.set.return_value = True
        
        data = {"key": "test_key", "value": "test_value"}
        response = client.post('/set', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["message"] == "Set test_key = test_value"
        mock_redis.set.assert_called_once_with("test_key", "test_value")
    
    def test_set_value_missing_key(self, client, mock_redis):
        """Test setting value with missing key parameter."""
        data = {"value": "test_value"}
        response = client.post('/set',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["error"] == "Both 'key' and 'value' are required."
        mock_redis.set.assert_not_called()
    
    def test_set_value_missing_value(self, client, mock_redis):
        """Test setting value with missing value parameter."""
        data = {"key": "test_key"}
        response = client.post('/set',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["error"] == "Both 'key' and 'value' are required."
        mock_redis.set.assert_not_called()
    
    def test_set_value_empty_key(self, client, mock_redis):
        """Test setting value with empty key."""
        data = {"key": "", "value": "test_value"}
        response = client.post('/set',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["error"] == "Both 'key' and 'value' are required."
        mock_redis.set.assert_not_called()
    
    def test_set_value_empty_value(self, client, mock_redis):
        """Test setting value with empty value."""
        data = {"key": "test_key", "value": ""}
        response = client.post('/set',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["error"] == "Both 'key' and 'value' are required."
        mock_redis.set.assert_not_called()
    
    def test_set_value_invalid_json(self, client, mock_redis):
        """Test setting value with invalid JSON."""
        response = client.post('/set',
                             data="invalid json",
                             content_type='application/json')
        
        # This will cause a 400 error due to invalid JSON
        assert response.status_code == 400
        mock_redis.set.assert_not_called()
    
    def test_get_value_success(self, client, mock_redis):
        """Test successful key retrieval."""
        mock_redis.get.return_value = "test_value"
        
        response = client.get('/get/test_key')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["test_key"] == "test_value"
        mock_redis.get.assert_called_once_with("test_key")
    
    def test_get_value_not_found(self, client, mock_redis):
        """Test retrieving non-existent key."""
        mock_redis.get.return_value = None
        
        response = client.get('/get/nonexistent_key')
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data["error"] == "Key not found."
        mock_redis.get.assert_called_once_with("nonexistent_key")
    
    def test_get_value_with_special_characters(self, client, mock_redis):
        """Test retrieving key with special characters."""
        mock_redis.get.return_value = "special_value"
        special_key = "key-with_special.chars123"
        
        response = client.get(f'/get/{special_key}')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data[special_key] == "special_value"
        mock_redis.get.assert_called_once_with(special_key)
    
    @patch('app.redis.Redis')
    def test_redis_connection_configuration(self, mock_redis_class):
        """Test Redis connection is configured with correct parameters."""
        # Mock environment variables
        with patch.dict(os.environ, {'REDIS_HOST': 'custom_host', 'REDIS_PORT': '1234'}):
            # Reimport to trigger Redis connection with new env vars
            import importlib
            import app as test_app
            importlib.reload(test_app)
            
            # Check if Redis was called with correct parameters
            mock_redis_class.assert_called_with(
                host='custom_host',
                port=1234,
                decode_responses=True
            )
    
    @patch('app.redis.Redis')
    def test_redis_connection_default_values(self, mock_redis_class):
        """Test Redis connection uses default values when env vars not set."""
        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            # Reimport to trigger Redis connection with default values
            import importlib
            import app as test_app
            importlib.reload(test_app)
            
            # Check if Redis was called with default parameters
            mock_redis_class.assert_called_with(
                host='redis',
                port=6379,
                decode_responses=True
            )

class TestIntegrationScenarios:
    """Integration-style tests for common workflows."""
    
    def test_set_then_get_workflow(self, client, mock_redis):
        """Test setting a value and then retrieving it."""
        # Mock Redis to return the value we set
        mock_redis.set.return_value = True
        mock_redis.get.return_value = "stored_value"
        
        # Set a value
        set_data = {"key": "workflow_key", "value": "stored_value"}
        set_response = client.post('/set',
                                 data=json.dumps(set_data),
                                 content_type='application/json')
        
        assert set_response.status_code == 200
        
        # Get the value
        get_response = client.get('/get/workflow_key')
        
        assert get_response.status_code == 200
        response_data = json.loads(get_response.data)
        assert response_data["workflow_key"] == "stored_value"
        
        # Verify Redis calls
        mock_redis.set.assert_called_once_with("workflow_key", "stored_value")
        mock_redis.get.assert_called_once_with("workflow_key")
    
    def test_overwrite_existing_key(self, client, mock_redis):
        """Test overwriting an existing key."""
        mock_redis.set.return_value = True
        
        # Set initial value
        initial_data = {"key": "overwrite_key", "value": "initial_value"}
        client.post('/set',
                   data=json.dumps(initial_data),
                   content_type='application/json')
        
        # Overwrite with new value
        new_data = {"key": "overwrite_key", "value": "new_value"}
        response = client.post('/set',
                             data=json.dumps(new_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["message"] == "Set overwrite_key = new_value"
        
        # Verify Redis was called twice with the same key
        assert mock_redis.set.call_count == 2
        mock_redis.set.assert_any_call("overwrite_key", "initial_value")
        mock_redis.set.assert_any_call("overwrite_key", "new_value")


# Test configuration and setup
if __name__ == '__main__':
    pytest.main([__file__])
