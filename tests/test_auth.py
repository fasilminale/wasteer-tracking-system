"""
Tests for the authentication routes.
"""


def test_register(client):
    """Test user registration."""
    # Test successful registration
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'newuser@test.com',
        'password': 'newuserpass',
        'role_id': 3  # Employee role
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'
    assert response.json['user']['username'] == 'newuser'
    assert response.json['user']['email'] == 'newuser@test.com'
    assert response.json['user']['role']['name'] == 'Employee'
    
    # Test registration with existing username
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'another@test.com',
        'password': 'anotherpass'
    })
    assert response.status_code == 409
    assert response.json['message'] == 'Username already exists'
    
    # Test registration with existing email
    response = client.post('/api/auth/register', json={
        'username': 'another',
        'email': 'newuser@test.com',
        'password': 'anotherpass'
    })
    assert response.status_code == 409
    assert response.json['message'] == 'Email already exists'
    
    # Test registration with missing fields
    response = client.post('/api/auth/register', json={
        'username': 'incomplete'
    })
    assert response.status_code == 400
    assert response.json['message'] == 'Missing required fields'


def test_login(client):
    """Test user login."""
    # Test successful login
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'adminpass'
    })
    assert response.status_code == 200
    assert response.json['message'] == 'Login successful'
    assert 'access_token' in response.json
    assert response.json['user']['username'] == 'admin'
    assert response.json['user']['is_superuser'] is True
    
    # Test login with invalid username
    response = client.post('/api/auth/login', json={
        'username': 'nonexistent',
        'password': 'adminpass'
    })
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid username or password'
    
    # Test login with invalid password
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'wrongpass'
    })
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid username or password'
    
    # Test login with missing fields
    response = client.post('/api/auth/login', json={
        'username': 'admin'
    })
    assert response.status_code == 400
    assert response.json['message'] == 'Missing username or password'


def test_profile(client, auth_tokens):
    """Test user profile access."""
    # Test successful profile access
    response = client.get('/api/auth/profile', headers={
        'Authorization': f'Bearer {auth_tokens["admin"]}'
    })
    assert response.status_code == 200
    assert response.json['username'] == 'admin'
    assert response.json['email'] == 'admin@test.com'
    assert response.json['is_superuser'] is True
    assert response.json['role']['name'] == 'Admin'
    
    # Test profile access without token
    response = client.get('/api/auth/profile')
    assert response.status_code == 401
    
    # Test profile access with invalid token
    response = client.get('/api/auth/profile', headers={
        'Authorization': 'Bearer invalid-token'
    })
    assert response.status_code == 422  # JWT decode error 