"""
Tests for the teams routes.
"""
import pytest
from app.models import Team


def test_get_teams(client, auth_tokens):
    """Test getting teams."""
    # Test as admin (should see all teams)
    response = client.get('/api/teams', headers={
        'Authorization': f'Bearer {auth_tokens["admin"]}'
    })
    assert response.status_code == 200
    assert len(response.json['teams']) == 2  # Engineering and Marketing
    
    # Test as manager (should see only their team)
    response = client.get('/api/teams', headers={
        'Authorization': f'Bearer {auth_tokens["manager"]}'
    })
    assert response.status_code == 200
    assert len(response.json['teams']) == 1
    assert response.json['teams'][0]['name'] == 'Engineering'
    
    # Test as employee (should be denied)
    response = client.get('/api/teams', headers={
        'Authorization': f'Bearer {auth_tokens["employee"]}'
    })
    assert response.status_code == 403
    
    # Test without authentication
    response = client.get('/api/teams')
    assert response.status_code == 401


def test_create_team(client, auth_tokens):
    """Test creating a team."""
    # Test as admin (should succeed)
    response = client.post('/api/teams', 
                          headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
                          json={'name': 'Finance', 'description': 'Finance team'})
    assert response.status_code == 201
    assert response.json['team']['name'] == 'Finance'
    assert response.json['team']['description'] == 'Finance team'
    
    # Test creating team with existing name
    response = client.post('/api/teams', 
                          headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
                          json={'name': 'Finance', 'description': 'Another finance team'})
    assert response.status_code == 409
    assert response.json['message'] == 'Team name already exists'
    
    # Test as manager (should be denied)
    response = client.post('/api/teams', 
                          headers={'Authorization': f'Bearer {auth_tokens["manager"]}'},
                          json={'name': 'HR', 'description': 'HR team'})
    assert response.status_code == 403
    
    # Test as employee (should be denied)
    response = client.post('/api/teams', 
                          headers={'Authorization': f'Bearer {auth_tokens["employee"]}'},
                          json={'name': 'IT', 'description': 'IT team'})
    assert response.status_code == 403
    
    # Test without authentication
    response = client.post('/api/teams', 
                          json={'name': 'Legal', 'description': 'Legal team'})
    assert response.status_code == 401


def test_get_team(client, auth_tokens, app):
    """Test getting a specific team."""
    with app.app_context():
        # Get the Engineering team ID
        engineering = Team.query.filter_by(name='Engineering').first()
        team_id = engineering.id
        
        # Test as admin
        response = client.get(f'/api/teams/{team_id}', 
                             headers={'Authorization': f'Bearer {auth_tokens["admin"]}'})
        assert response.status_code == 200
        assert response.json['name'] == 'Engineering'
        
        # Test as manager of the team
        response = client.get(f'/api/teams/{team_id}', 
                             headers={'Authorization': f'Bearer {auth_tokens["manager"]}'})
        assert response.status_code == 200
        assert response.json['name'] == 'Engineering'
        
        # Test as employee (should be denied)
        response = client.get(f'/api/teams/{team_id}', 
                             headers={'Authorization': f'Bearer {auth_tokens["employee"]}'})
        assert response.status_code == 403
        
        # Test with non-existent team ID
        response = client.get('/api/teams/999', 
                             headers={'Authorization': f'Bearer {auth_tokens["admin"]}'})
        assert response.status_code == 404
        
        # Test without authentication
        response = client.get(f'/api/teams/{team_id}')
        assert response.status_code == 401


def test_update_team(client, auth_tokens, app):
    """Test updating a team."""
    with app.app_context():
        # Get the Engineering team ID
        engineering = Team.query.filter_by(name='Engineering').first()
        team_id = engineering.id
        
        # Test as admin
        response = client.put(f'/api/teams/{team_id}', 
                             headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
                             json={'name': 'Engineering Department', 'description': 'Updated description'})
        assert response.status_code == 200
        assert response.json['team']['name'] == 'Engineering Department'
        assert response.json['team']['description'] == 'Updated description'
        
        # Test as manager (should be denied)
        response = client.put(f'/api/teams/{team_id}', 
                             headers={'Authorization': f'Bearer {auth_tokens["manager"]}'},
                             json={'name': 'Eng Team', 'description': 'Manager update'})
        assert response.status_code == 403
        
        # Test as employee (should be denied)
        response = client.put(f'/api/teams/{team_id}', 
                             headers={'Authorization': f'Bearer {auth_tokens["employee"]}'},
                             json={'name': 'Eng', 'description': 'Employee update'})
        assert response.status_code == 403
        
        # Test with non-existent team ID
        response = client.put('/api/teams/999', 
                             headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
                             json={'name': 'Nonexistent', 'description': 'Update nonexistent'})
        assert response.status_code == 404
        
        # Test without authentication
        response = client.put(f'/api/teams/{team_id}', 
                             json={'name': 'Unauthenticated', 'description': 'Unauthenticated update'})
        assert response.status_code == 401


def test_get_team_members(client, auth_tokens, app):
    """Test getting team members."""
    with app.app_context():
        # Get the Engineering team ID
        engineering = Team.query.filter_by(name='Engineering').first()
        team_id = engineering.id
        
        # Test as admin
        response = client.get(f'/api/teams/{team_id}/members', 
                             headers={'Authorization': f'Bearer {auth_tokens["admin"]}'})
        assert response.status_code == 200
        assert len(response.json['members']) == 2  # manager and employee
        
        # Test as manager of the team
        response = client.get(f'/api/teams/{team_id}/members', 
                             headers={'Authorization': f'Bearer {auth_tokens["manager"]}'})
        assert response.status_code == 200
        assert len(response.json['members']) == 2
        
        # Test as employee (should be denied)
        response = client.get(f'/api/teams/{team_id}/members', 
                             headers={'Authorization': f'Bearer {auth_tokens["employee"]}'})
        assert response.status_code == 403
        
        # Test with non-existent team ID
        response = client.get('/api/teams/999/members', 
                             headers={'Authorization': f'Bearer {auth_tokens["admin"]}'})
        assert response.status_code == 404
        
        # Test without authentication
        response = client.get(f'/api/teams/{team_id}/members')
        assert response.status_code == 401 