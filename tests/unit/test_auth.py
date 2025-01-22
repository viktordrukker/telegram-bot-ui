import pytest
import json
from telegram_bot_ui import app

def test_register(client):
    response = client.post('/register',
                          data=json.dumps({
                              'username': 'testuser',
                              'password': 'testpass'
                          }),
                          content_type='application/json')
    assert response.status_code == 201
    assert b'User registered successfully!' in response.data

def test_login_success(client):
    # First register a user
    client.post('/register',
                data=json.dumps({
                    'username': 'testuser',
                    'password': 'testpass'
                }),
                content_type='application/json')
    
    # Then try to login
    response = client.post('/login',
                          data=json.dumps({
                              'username': 'testuser',
                              'password': 'testpass'
                          }),
                          content_type='application/json')
    assert response.status_code == 200
    assert 'token' in json.loads(response.data.decode())

def test_login_invalid_credentials(client):
    response = client.post('/login',
                          data=json.dumps({
                              'username': 'wronguser',
                              'password': 'wrongpass'
                          }),
                          content_type='application/json')
    assert response.status_code == 404