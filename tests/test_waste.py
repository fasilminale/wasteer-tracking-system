"""
Tests for the waste routes.
"""
from app.models import WasteEntry, WasteType


def test_create_waste_entry(client, auth_tokens):
    """Test creating a waste entry."""
    # Test as employee (should succeed)
    response = client.post(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["employee"]}'},
        json={
            'waste_type': 'plastic',
            'weight': 1.5,
            'description': 'Test plastic waste'
        }
    )
    assert response.status_code == 201
    assert response.json['waste_entry']['waste_type'] == 'plastic'
    assert response.json['waste_entry']['weight'] == 1.5
    assert response.json['waste_entry']['description'] == 'Test plastic waste'
    
    # Test as manager (should succeed)
    response = client.post(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["manager"]}'},
        json={
            'waste_type': 'glass',
            'weight': 2.0,
            'description': 'Test glass waste'
        }
    )
    assert response.status_code == 201
    assert response.json['waste_entry']['waste_type'] == 'glass'
    
    # Test as admin without team_id (should fail)
    response = client.post(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
        json={
            'waste_type': 'paper',
            'weight': 3.0,
            'description': 'Test paper waste'
        }
    )
    assert response.status_code == 400
    assert response.json['message'] == 'Team ID is required for admin users'
    
    # Test as admin with team_id (should succeed)
    response = client.post(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
        json={
            'waste_type': 'paper',
            'weight': 3.0,
            'description': 'Test paper waste',
            'team_id': 1
        }
    )
    assert response.status_code == 201
    assert response.json['waste_entry']['waste_type'] == 'paper'
    assert response.json['waste_entry']['team_id'] == 1
    
    # Test as admin with invalid team_id (should fail)
    response = client.post(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
        json={
            'waste_type': 'paper',
            'weight': 3.0,
            'description': 'Test paper waste',
            'team_id': 999  # Invalid team ID
        }
    )
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid team ID'
    
    # Test with invalid waste type
    response = client.post(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["employee"]}'},
        json={
            'waste_type': 'invalid',
            'weight': 1.0,
            'description': 'Invalid waste type'
        }
    )
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid waste type'
    
    # Test without authentication
    response = client.post(
        '/api/waste',
        json={
            'waste_type': 'paper',
            'weight': 1.0,
            'description': 'Unauthenticated'
        }
    )
    assert response.status_code == 401


def test_get_waste_entries(client, auth_tokens, app):
    """Test getting waste entries."""
    # Test as admin (should see all entries)
    response = client.get(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
    )
    assert response.status_code == 200
    # Initial entry + entries created in test_create_waste_entry
    assert len(response.json['waste_entries']) >= 1
    
    # Test as manager (should see team entries)
    response = client.get(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["manager"]}'}
    )
    assert response.status_code == 200
    assert len(response.json['waste_entries']) >= 1
    
    # Test as employee (should see only their entries)
    response = client.get(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["employee"]}'}
    )
    assert response.status_code == 200
    # Should have at least the entries they created
    assert len(response.json['waste_entries']) >= 1
    
    # Test with waste type filter
    response = client.get(
        '/api/waste?waste_type=paper',
        headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
    )
    assert response.status_code == 200
    for entry in response.json['waste_entries']:
        assert entry['waste_type'] == 'paper'
    
    # Test without authentication
    response = client.get('/api/waste')
    assert response.status_code == 401


def test_get_waste_analytics(client, auth_tokens):
    """Test getting waste analytics."""
    # Test as admin (should succeed)
    response = client.get(
        '/api/waste/analytics',
        headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
    )
    assert response.status_code == 200
    assert 'total_entries' in response.json
    assert 'total_weight' in response.json
    assert 'waste_by_type' in response.json
    
    # Test as manager (should succeed)
    response = client.get(
        '/api/waste/analytics',
        headers={'Authorization': f'Bearer {auth_tokens["manager"]}'}
    )
    assert response.status_code == 200
    assert 'total_entries' in response.json
    assert 'total_weight' in response.json
    assert 'waste_by_type' in response.json
    
    # Test as employee (should be denied)
    response = client.get(
        '/api/waste/analytics',
        headers={'Authorization': f'Bearer {auth_tokens["employee"]}'}
    )
    assert response.status_code == 403
    
    # Test with period parameter
    response = client.get(
        '/api/waste/analytics?period=month',
        headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
    )
    assert response.status_code == 200
    assert response.json['period'] == 'month'
    
    # Test without authentication
    response = client.get('/api/waste/analytics')
    assert response.status_code == 401 