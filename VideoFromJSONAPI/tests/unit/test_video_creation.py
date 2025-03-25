"""Unit tests for video creation endpoint."""
import json
from unittest.mock import patch


def test_create_video_success(client, sample_video_data):
    """Test successful video creation."""
    with patch('app.endpoints.video_creation.create_video') as mock_create:
        mock_create.return_value = {"video_id": "test123", "status": "processing"}
        
        response = client.post(
            '/api/creation',
            data=json.dumps(sample_video_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["video_id"] == "test123"
        assert data["status"] == "processing"


def test_create_video_invalid_data(client):
    """Test video creation with invalid data."""
    invalid_data = {
        "segments": [],  # Empty segments list
        "output_format": "invalid_format"
    }
    
    response = client.post(
        '/api/creation',
        data=json.dumps(invalid_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_create_video_missing_required_fields(client):
    """Test video creation with missing required fields."""
    incomplete_data = {
        "segments": [
            {
                "duration": 5
                # Missing type and source
            }
        ]
    }
    
    response = client.post(
        '/api/creation',
        data=json.dumps(incomplete_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_create_video_invalid_transition(client, sample_video_data):
    """Test video creation with invalid transition effect."""
    invalid_data = sample_video_data.copy()
    invalid_data["segments"][0]["transition"] = "invalid_transition"
    
    response = client.post(
        '/api/creation',
        data=json.dumps(invalid_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_create_video_server_error(client, sample_video_data):
    """Test video creation when server encounters an error."""
    with patch('app.endpoints.video_creation.create_video') as mock_create:
        mock_create.side_effect = Exception("Server error")
        
        response = client.post(
            '/api/creation',
            data=json.dumps(sample_video_data),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data 