"""
Tests for the waste routes.
"""

def test_create_waste_entry(client, auth_tokens):
    """Test creating waste entries."""
    # Test as admin
    response = client.post(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
        json={
            'waste_type': 'paper',
            'weight': 1.5,
            'description': 'Test waste entry by admin',
            'team_id': 1  # Engineering team
        }
    )
    assert response.status_code == 201
    assert response.json['message'] == 'Waste entry created successfully'
    assert response.json['waste_entry']['waste_type'] == 'paper'
    assert response.json['waste_entry']['weight'] == 1.5
    assert 'Test waste entry by admin' in response.json['waste_entry']['description']
    
    # Test as manager
    response = client.post(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["manager"]}'},
        json={
            'waste_type': 'plastic',
            'weight': 2.5,
            'description': 'Test waste entry by manager'
        }
    )
    assert response.status_code == 201
    assert response.json['message'] == 'Waste entry created successfully'
    assert response.json['waste_entry']['waste_type'] == 'plastic'
    assert response.json['waste_entry']['weight'] == 2.5
    assert 'Test waste entry by manager' in response.json['waste_entry']['description']
    
    # Test as employee
    response = client.post(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["employee"]}'},
        json={
            'waste_type': 'glass',
            'weight': 3.5,
            'description': 'Test waste entry by employee'
        }
    )
    assert response.status_code == 201
    assert response.json['message'] == 'Waste entry created successfully'
    assert response.json['waste_entry']['waste_type'] == 'glass'
    assert response.json['waste_entry']['weight'] == 3.5
    assert 'Test waste entry by employee' in response.json['waste_entry']['description']
    
    # Test with invalid waste type
    response = client.post(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["employee"]}'},
        json={
            'waste_type': 'invalid_type',
            'weight': 4.5,
            'description': 'Test waste entry with invalid type'
        }
    )
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid waste type'
    
    # Test with missing required fields
    response = client.post(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["employee"]}'},
        json={
            'description': 'Test waste entry with missing fields'
        }
    )
    assert response.status_code == 400
    assert response.json['message'] == 'Missing required fields'
    
    # Test without authentication
    response = client.post(
        '/api/waste',
        json={
            'waste_type': 'paper',
            'weight': 5.5,
            'description': 'Test waste entry without auth'
        }
    )
    assert response.status_code == 401


def test_get_waste_entries(client, auth_tokens, app):
    """Test getting waste entries."""s
    client.post(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
        json={
            'waste_type': 'paper',
            'weight': 1.5,
            'description': 'Test waste entry for get test',
            'team_id': 1  # Engineering team
        }
    )
    
    # Also create one as an employee
    client.post(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["employee"]}'},
        json={
            'waste_type': 'plastic',
            'weight': 2.5,
            'description': 'Test entry by employee'
        }
    )
    
    # Test as admin (should be authorized)
    response = client.get(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
    )
    assert response.status_code == 200
    
    # Test as manager (should be authorized)
    response = client.get(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["manager"]}'}
    )
    assert response.status_code == 200
    
    # Test as employee (should be authorized)
    response = client.get(
        '/api/waste',
        headers={'Authorization': f'Bearer {auth_tokens["employee"]}'}
    )
    assert response.status_code == 200
    
    # Test with waste type filter
    response = client.get(
        '/api/waste?waste_type=paper',
        headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
    )
    assert response.status_code == 200
    
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