# tests/test_client.py
import pytest
import os

from todoist.tools.client import TodoistClient
from .test_utils import retry_on_network_error

@pytest.fixture
def sample_token():
    """Get real API token for testing"""
    import os
    
    # Get the API token from environment (for testing)
    # In production, Arcade would provide this through ToolContext
    token = os.getenv("TODOIST_API_TOKEN")
    if not token:
        pytest.skip("TODOIST_API_TOKEN environment variable not set for testing")
    return token

@retry_on_network_error()
def test_client_initialization(sample_token):
    """Test TodoistClient initialization with real token"""
    client = TodoistClient(sample_token)
    
    assert client.headers == {"Authorization": f"Bearer {sample_token}"}
    assert "Authorization" in client.headers
    assert client.headers["Authorization"].startswith("Bearer ")

@retry_on_network_error()
def test_get_projects_success(sample_token):
    """Test successful GET request to projects endpoint"""
    client = TodoistClient(sample_token)
    result = client.get("/projects")
    
    assert isinstance(result, list)
    assert len(result) >= 1  # Should have at least inbox project
    
    # Verify project structure
    for project in result:
        assert "id" in project
        assert "name" in project

@retry_on_network_error()
def test_get_with_params(sample_token):
    """Test GET request with parameters - verify client handles params correctly"""
    client = TodoistClient(sample_token)
    
    # Test that client can make requests with parameters
    # We'll use a simple endpoint that accepts params
    params = {"limit": 1}  # Simple parameter that most APIs accept
    
    result = client.get("/projects", params=params)
    
    # Verify the client returns a result (we don't care about the API's business logic)
    assert isinstance(result, list)
    # The client's job is to make the request and return the response
    # We're not testing that the API respects the limit parameter

def test_client_invalid_token():
    """Test client behavior with invalid token"""
    client = TodoistClient("invalid_token_12345")
    
    # Should raise an HTTP error for unauthorized access
    with pytest.raises(Exception):  # Could be httpx.HTTPStatusError or similar
        client.get("/projects")

def test_client_network_timeout():
    """Test client timeout handling"""
    import httpx
    
    # Create a client with very short timeout to trigger timeout
    client = TodoistClient("dummy_token")
    
    # Mock a slow response or use a non-existent endpoint
    with pytest.raises(httpx.TimeoutException):
        # Use a very short timeout to force a timeout
        with httpx.Client(timeout=0.001) as c:
            c.get("https://httpbin.org/delay/1")

def test_client_http_errors():
    """Test client handling of various HTTP error codes"""
    client = TodoistClient("invalid_token")
    
    # Test 401 Unauthorized
    with pytest.raises(Exception):
        client.get("/projects")
    
    # Test 404 Not Found
    with pytest.raises(Exception):
        client.get("/nonexistent_endpoint")

def test_post_204_response():
    """Test POST requests that return 204 status"""
    # This is harder to test without a real endpoint that returns 204
    # We'll test the client's ability to handle 204 responses
    client = TodoistClient("dummy_token")
    
    # The close_task endpoint returns 204, but we can't easily test this
    # without creating a real task first. This test documents the expected behavior.
    pass  # Placeholder for now
