import pytest
import requests
import json
import time
import redis
from typing import Generator

# Configuration
FLASK_URL = "http://localhost:4000"
REDIS_URL = "redis://redis:6379"
REDIS_SERVICE = "redis"

def check_service_health():
    """Check if required services are running and accessible."""
    try:
        # Check Flask service
        response = requests.get(FLASK_URL, timeout=5)
        if response.status_code != 200:
            raise Exception(f"Flask service not responding correctly: {response.status_code}")
        
        # Check Redis service
        r = redis.Redis(host="localhost", port=6379, socket_timeout=5)
        r.ping()
        
        return True
    except Exception as e:
        raise Exception(f"Services not ready. Please ensure Docker Compose is running. Error: {e}")

@pytest.fixture(scope="session", autouse=True)
def verify_services():
    """Verify that required services are running before tests start."""
    print("Verifying that Docker Compose services are running...")
    check_service_health()
    print("✓ All services are accessible!")

@pytest.fixture
def redis_client():
    """Fixture to provide a Redis client for direct database access."""
    client = redis.Redis(host=REDIS_SERVICE, port=6379, decode_responses=True)
    yield client
    # Cleanup: flush all keys after each test
    client.flushall()

@pytest.fixture
def api_client():
    """Fixture to provide a configured requests session."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session

class TestFlaskRedisIntegration:
    """Integration tests for Flask Redis application."""
    
    def test_index_endpoint(self, api_client):
        """Test the index endpoint returns expected response."""
        response = api_client.get(f"{FLASK_URL}/")
        
        assert response.status_code == 200
        assert response.text == "Hello from Flask app connected to Redis!"
    
    def test_set_and_get_value(self, api_client, redis_client):
        """Test setting and getting a value through the API."""
        # Set a value via API
        set_data = {"key": "integration_test", "value": "test_value_123"}
        set_response = api_client.post(
            f"{FLASK_URL}/set",
            data=json.dumps(set_data)
        )
        
        assert set_response.status_code == 200
        set_result = set_response.json()
        assert set_result["message"] == "Set integration_test = test_value_123"
        
        # Verify the value was actually stored in Redis
        redis_value = redis_client.get("integration_test")
        assert redis_value == "test_value_123"
        
        # Get the value via API
        get_response = api_client.get(f"{FLASK_URL}/get/integration_test")
        
        assert get_response.status_code == 200
        get_result = get_response.json()
        assert get_result["integration_test"] == "test_value_123"
    
    def test_get_nonexistent_key(self, api_client):
        """Test getting a key that doesn't exist."""
        response = api_client.get(f"{FLASK_URL}/get/nonexistent_key_12345")
        
        assert response.status_code == 404
        result = response.json()
        assert result["error"] == "Key not found."
    
    def test_set_invalid_payload(self, api_client):
        """Test setting with invalid JSON payload."""
        # Missing key
        response = api_client.post(
            f"{FLASK_URL}/set",
            data=json.dumps({"value": "test_value"})
        )
        
        assert response.status_code == 400
        result = response.json()
        assert result["error"] == "Both 'key' and 'value' are required."
        
        # Missing value
        response = api_client.post(
            f"{FLASK_URL}/set",
            data=json.dumps({"key": "test_key"})
        )
        
        assert response.status_code == 400
        result = response.json()
        assert result["error"] == "Both 'key' and 'value' are required."
    
    def test_set_empty_values(self, api_client):
        """Test setting with empty key or value."""
        # Empty key
        response = api_client.post(
            f"{FLASK_URL}/set",
            data=json.dumps({"key": "", "value": "test_value"})
        )
        
        assert response.status_code == 400
        result = response.json()
        assert result["error"] == "Both 'key' and 'value' are required."
        
        # Empty value
        response = api_client.post(
            f"{FLASK_URL}/set",
            data=json.dumps({"key": "test_key", "value": ""})
        )
        
        assert response.status_code == 400
        result = response.json()
        assert result["error"] == "Both 'key' and 'value' are required."
    
    def test_overwrite_existing_key(self, api_client, redis_client):
        """Test overwriting an existing key."""
        key = "overwrite_test"
        
        # Set initial value
        initial_data = {"key": key, "value": "initial_value"}
        response = api_client.post(
            f"{FLASK_URL}/set",
            data=json.dumps(initial_data)
        )
        assert response.status_code == 200
        
        # Verify initial value in Redis
        assert redis_client.get(key) == "initial_value"
        
        # Overwrite with new value
        new_data = {"key": key, "value": "new_value"}
        response = api_client.post(
            f"{FLASK_URL}/set",
            data=json.dumps(new_data)
        )
        assert response.status_code == 200
        
        # Verify new value in Redis
        assert redis_client.get(key) == "new_value"
        
        # Verify via API
        get_response = api_client.get(f"{FLASK_URL}/get/{key}")
        assert get_response.status_code == 200
        result = get_response.json()
        assert result[key] == "new_value"
    
    def test_special_characters_in_key(self, api_client, redis_client):
        """Test keys with special characters."""
        special_key = "key-with_special.chars123"
        test_value = "special_character_value"
        
        # Set value with special key
        set_data = {"key": special_key, "value": test_value}
        response = api_client.post(
            f"{FLASK_URL}/set",
            data=json.dumps(set_data)
        )
        assert response.status_code == 200
        
        # Verify in Redis
        assert redis_client.get(special_key) == test_value
        
        # Get value with special key
        get_response = api_client.get(f"{FLASK_URL}/get/{special_key}")
        assert get_response.status_code == 200
        result = get_response.json()
        assert result[special_key] == test_value
    
    def test_unicode_values(self, api_client, redis_client):
        """Test storing and retrieving Unicode values."""
        unicode_data = {
            "key": "unicode_test", 
            "value": "Hello 世界! 🌍 Café naïve résumé"
        }
        
        # Set Unicode value
        response = api_client.post(
            f"{FLASK_URL}/set",
            data=json.dumps(unicode_data, ensure_ascii=False)
        )
        assert response.status_code == 200
        
        # Verify in Redis
        stored_value = redis_client.get("unicode_test")
        assert stored_value == unicode_data["value"]
        
        # Get Unicode value
        get_response = api_client.get(f"{FLASK_URL}/get/unicode_test")
        assert get_response.status_code == 200
        result = get_response.json()
        assert result["unicode_test"] == unicode_data["value"]
    
    def test_large_value(self, api_client, redis_client):
        """Test storing and retrieving large values."""
        large_value = "x" * 10000  # 10KB string
        
        set_data = {"key": "large_value_test", "value": large_value}
        response = api_client.post(
            f"{FLASK_URL}/set",
            data=json.dumps(set_data)
        )
        assert response.status_code == 200
        
        # Verify in Redis
        assert redis_client.get("large_value_test") == large_value
        
        # Get large value
        get_response = api_client.get(f"{FLASK_URL}/get/large_value_test")
        assert get_response.status_code == 200
        result = get_response.json()
        assert result["large_value_test"] == large_value
    
    def test_multiple_keys_workflow(self, api_client, redis_client):
        """Test working with multiple keys."""
        test_data = [
            {"key": "key1", "value": "value1"},
            {"key": "key2", "value": "value2"},
            {"key": "key3", "value": "value3"}
        ]
        
        # Set multiple keys
        for data in test_data:
            response = api_client.post(
                f"{FLASK_URL}/set",
                data=json.dumps(data)
            )
            assert response.status_code == 200
        
        # Verify all keys exist in Redis
        for data in test_data:
            assert redis_client.get(data["key"]) == data["value"]
        
        # Get all keys via API
        for data in test_data:
            response = api_client.get(f"{FLASK_URL}/get/{data['key']}")
            assert response.status_code == 200
            result = response.json()
            assert result[data["key"]] == data["value"]

class TestRedisConnectivity:
    """Test Redis connectivity and data persistence."""
    
    def test_direct_redis_connection(self):
        """Test direct connection to Redis service."""
        client = redis.Redis(host=REDIS_SERVICE, port=6379, decode_responses=True)
        
        # Test basic Redis operations
        assert client.ping() is True
        
        # Set and get a value directly
        client.set("direct_test", "direct_value")
        assert client.get("direct_test") == "direct_value"
        
        # Cleanup
        client.delete("direct_test")
    
    def test_redis_persistence_across_requests(self, api_client):
        """Test that data persists across multiple API requests."""
        # Set a value
        set_data = {"key": "persistence_test", "value": "persistent_value"}
        api_client.post(f"{FLASK_URL}/set", data=json.dumps(set_data))
        
        # Make multiple GET requests to ensure persistence
        for _ in range(5):
            response = api_client.get(f"{FLASK_URL}/get/persistence_test")
            assert response.status_code == 200
            result = response.json()
            assert result["persistence_test"] == "persistent_value"
            time.sleep(0.1)  # Small delay between requests

class TestErrorHandling:
    """Test error handling in integration environment."""
    
    def test_malformed_json(self, docker_services, api_client):
        """Test handling of malformed JSON."""
        response = api_client.post(
            f"{FLASK_URL}/set",
            data="{ invalid json }",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
    
    def test_missing_content_type(self, docker_services):
        """Test request without proper content type."""
        response = requests.post(
            f"{FLASK_URL}/set",
            data=json.dumps({"key": "test", "value": "test"})
        )
        
        # Should still work, but may handle differently
        # The exact behavior depends on Flask's request parsing
        assert response.status_code in [200, 400]  # Either works or fails gracefully

if __name__ == "__main__":
    # Run with pytest integration_tests.py -v
    pytest.main([__file__, "-v"])
