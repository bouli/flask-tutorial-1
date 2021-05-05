import pytest
from flaskr.db import get_db 

def test_index(client, auth):
    response = client.get('/')
    assert b'Log In' in response.data
    assert b'Register' in response.data

    auth.login()

    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    
    assert b'href="/1/update"' in response.data
    
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client,path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'

def test_author_required(app, client, auth):
    with app.app_context():
        db = get_db()
        db.execute('UPDATE posts SET author_id = 2 WHERE id = 1')
        db.commit()
    
    auth.login()
    assert client.post('/1/update').status_code == 403 #403 = forbidden
    assert client.post('/1/delete').status_code == 403 #403 = forbidden

    assert b'href="/1/update"' not in client.get('/').data

@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404

def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    response = client.post('/create', data={'title':'My title', 'body': 'My body'})

    with app.app_context():
        assert get_db().execute('SELECT COUNT(*) FROM posts').fetchone()[0] == 2

def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'body': 'asdf'})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM posts WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': 'asdf'})
    assert b'Title is required' in response.data
    
    response = client.post(path, data={'title': 'asdf', 'body': ''})
    assert b'Body is required' in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM posts WHERE id = 1').fetchone()
        assert post is None