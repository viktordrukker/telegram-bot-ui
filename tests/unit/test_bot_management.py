import pytest
import json
from telegram_bot_ui import app

def test_add_bot(client, auth_headers):
    response = client.post('/add_bot',
                          headers=auth_headers,
                          data=json.dumps({
                              'bot_token': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
                              'bot_name': 'TestBot'
                          }),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data.decode())
    assert 'bot_id' in data

def test_bot_status(client, auth_headers):
    # First add a bot
    response = client.post('/add_bot',
                          headers=auth_headers,
                          data=json.dumps({
                              'bot_token': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
                              'bot_name': 'TestBot'
                          }),
                          content_type='application/json')
    bot_id = json.loads(response.data.decode())['bot_id']
    
    # Then check its status
    response = client.get(f'/bots/{bot_id}/status',
                         headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert 'status' in data

def test_bot_control(client, auth_headers):
    # First add a bot
    response = client.post('/add_bot',
                          headers=auth_headers,
                          data=json.dumps({
                              'bot_token': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
                              'bot_name': 'TestBot'
                          }),
                          content_type='application/json')
    bot_id = json.loads(response.data.decode())['bot_id']
    
    # Test start
    response = client.post(f'/bots/{bot_id}/start',
                          headers=auth_headers)
    assert response.status_code == 200
    
    # Test stop
    response = client.post(f'/bots/{bot_id}/stop',
                          headers=auth_headers)
    assert response.status_code == 200
    
    # Test restart
    response = client.post(f'/bots/{bot_id}/restart',
                          headers=auth_headers)
    assert response.status_code == 200