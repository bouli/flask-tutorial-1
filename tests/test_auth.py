import pytest
from flask import session, g
from flaskr.db import get_db

def test_register(client, app):
    #Page access
    assert client.get('/auth/register').status_code == 200
    
    #Sent form
    response = client.post(
        'auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM users WHERE username ='a'"
        ).fetchone() is not None

@pytest.mark.parametrize(('username','password','message'), (
    ('','',b'Username is required'),
    ('a','',b'Password is required'),
    ('test','test',b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data

def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'
    
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

@pytest.mark.parametrize(('username','password','message'), (
    ('test','a',b'Username and password don'),
    ('a','test',b'Username and password don'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username=username,password=password)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session