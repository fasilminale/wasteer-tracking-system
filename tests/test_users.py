"""
Tests for the users routes.
"""
from app.models import User, UserRole


def test_get_users(client, auth_tokens):
    """Test getting users."""
    # Test as admin (should succeed)
    response = client.get(
        '/api/users',
        headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
    )
    assert response.status_code == 200
    assert len(response.json['users']) >= 3  # admin, manager, employee
    
    # Test as manager (should be denied)
    response = client.get(
        '/api/users',
        headers={'Authorization': f'Bearer {auth_tokens["manager"]}'}
    )
    assert response.status_code == 403
    
    # Test as employee (should be denied)
    response = client.get(
        '/api/users',
        headers={'Authorization': f'Bearer {auth_tokens["employee"]}'}
    )
    assert response.status_code == 403
    
    # Test with team_id filter
    with client.application.app_context():
        # Get the Engineering team ID
        manager = User.query.filter_by(username='manager').first()
        team_id = manager.team_id
        
        response = client.get(
            f'/api/users?team_id={team_id}',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
        )
        assert response.status_code == 200
        for user in response.json['users']:
            assert user['team_id'] == team_id
    
    # Test with role filter
    response = client.get(
        '/api/users?role=manager',
        headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
    )
    assert response.status_code == 200
    for user in response.json['users']:
        assert user['role'] == 'manager'
    
    # Test without authentication
    response = client.get('/api/users')
    assert response.status_code == 401


def test_get_user(client, auth_tokens, app):
    """Test getting a specific user."""
    with app.app_context():
        # Get the employee user ID
        employee = User.query.filter_by(username='employee').first()
        user_id = employee.id
        
        # Test as admin
        response = client.get(
            f'/api/users/{user_id}',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
        )
        assert response.status_code == 200
        assert response.json['username'] == 'employee'
        assert response.json['email'] == 'employee@test.com'
        
        # Test as manager (should be denied)
        response = client.get(
            f'/api/users/{user_id}',
            headers={'Authorization': f'Bearer {auth_tokens["manager"]}'}
        )
        assert response.status_code == 403
        
        # Test as employee (should be denied)
        response = client.get(
            f'/api/users/{user_id}',
            headers={'Authorization': f'Bearer {auth_tokens["employee"]}'}
        )
        assert response.status_code == 403
        
        # Test with non-existent user ID
        response = client.get(
            '/api/users/999',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
        )
        assert response.status_code == 404
        
        # Test without authentication
        response = client.get(f'/api/users/{user_id}')
        assert response.status_code == 401


def test_update_user(client, auth_tokens, app):
    """Test updating a user."""
    with app.app_context():
        # Get the employee user ID
        employee = User.query.filter_by(username='employee').first()
        user_id = employee.id
        
        # Test as admin
        response = client.put(
            f'/api/users/{user_id}',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
            json={
                'username': 'updated_employee',
                'email': 'updated_employee@test.com',
                'role': 'manager'
            }
        )
        assert response.status_code == 200
        assert response.json['user']['username'] == 'updated_employee'
        assert response.json['user']['email'] == 'updated_employee@test.com'
        assert response.json['user']['role'] == 'manager'
        
        # Test as manager (should be denied)
        response = client.put(
            f'/api/users/{user_id}',
            headers={'Authorization': f'Bearer {auth_tokens["manager"]}'},
            json={'username': 'manager_update'}
        )
        assert response.status_code == 403
        
        # Test as employee (should be denied)
        response = client.put(
            f'/api/users/{user_id}',
            headers={'Authorization': f'Bearer {auth_tokens["employee"]}'},
            json={'username': 'employee_update'}
        )
        assert response.status_code == 403
        
        # Test with non-existent user ID
        response = client.put(
            '/api/users/999',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
            json={'username': 'nonexistent_update'}
        )
        assert response.status_code == 404
        
        # Test without authentication
        response = client.put(
            f'/api/users/{user_id}',
            json={'username': 'unauthenticated_update'}
        )
        assert response.status_code == 401


def test_delete_user(client, auth_tokens, app):
    """Test deleting a user."""
    with app.app_context():
        # Create a test user to delete
        test_user = User(
            username="test_delete",
            email="test_delete@test.com",
            password="testpass",
            role=UserRole.EMPLOYEE
        )
        from app import db
        db.session.add(test_user)
        db.session.commit()
        
        user_id = test_user.id
        
        # Test as admin
        response = client.delete(
            f'/api/users/{user_id}',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
        )
        assert response.status_code == 200
        assert response.json['message'] == 'User deleted successfully'
        
        # Verify user is deleted
        deleted_user = db.session.get(User, user_id)
        assert deleted_user is None
        
        # Test deleting non-existent user
        response = client.delete(
            f'/api/users/{user_id}',  # Already deleted
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
        )
        assert response.status_code == 404
        
        # Create another test user
        test_user2 = User(
            username="test_delete2",
            email="test_delete2@test.com",
            password="testpass",
            role=UserRole.EMPLOYEE
        )
        db.session.add(test_user2)
        db.session.commit()
        
        user_id2 = test_user2.id
        
        # Test as manager (should be denied)
        response = client.delete(
            f'/api/users/{user_id2}',
            headers={'Authorization': f'Bearer {auth_tokens["manager"]}'}
        )
        assert response.status_code == 403
        
        # Test as employee (should be denied)
        response = client.delete(
            f'/api/users/{user_id2}',
            headers={'Authorization': f'Bearer {auth_tokens["employee"]}'}
        )
        assert response.status_code == 403
        
        # Test without authentication
        response = client.delete(f'/api/users/{user_id2}')
        assert response.status_code == 401 