"""
Test file for standup features in the server
"""


import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
import random
import string
import auth

# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
@pytest.fixture
def url():
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")

############ FIXTURES FOR REGISTERING AND LOGGING IN USERS ###############

@pytest.fixture
def _USER_1(url):
    '''
    Registers and logs in a user returning a dictionary containing the
    token and u_id. As this is the first register, this user is the
    flockr owner

    Returns:
        dictionary: {
            'token':
            'u_id':
        }
    '''

    user = {
        'email': 'daniel.steyn@gmail.com',
        'password': 'mypassword2',
        'name_first': 'Daniel',
        'name_last': 'Steyn',
    }

    login = {
        'email': 'daniel.steyn@gmail.com',
        'password': 'mypassword2',
    }

    requests.post(url +'/auth/register', json=user)
    payload = requests.post(url + '/auth/login', json=login).json()
    return payload

@pytest.fixture
def _USER_2(url):
    '''
    Registers and logs in a user returning a dictionary containing the
    token and u_id.

    Returns:
        dictionary: {
            'token':
            'u_id':
        }
    '''

    user = {
        'email': 'liam.treavors@gmail.com',
        'password': 'mypassword1',
        'name_first': 'Liam',
        'name_last': 'Treavors',
    }

    login = {
        'email': 'liam.treavors@gmail.com',
        'password': 'mypassword1',
    }

    requests.post(url +'/auth/register', json=user)
    payload = requests.post(url + '/auth/login', json=login).json()
    return payload

@pytest.fixture
def _USER_3(url):
    '''
    Registers and logs in a user returning a dictionary containing the
    token and u_id.

    Returns:
        dictionary: {
            'token':
            'u_id':
        }
    '''

    user = {
        'email': 'mikkel@gmail.com',
        'password': 'mypassword3',
        'name_first': 'Mikkel',
        'name_last': 'Endresen',
    }

    login = {
        'email': 'mikkel@gmail.com',
        'password': 'mypassword3',
    }

    requests.post(url +'/auth/register', json=user)
    payload = requests.post(url + '/auth/login', json=login).json()
    return payload

@pytest.fixture
def _CHANNEL_1(url, _USER_1):
    '''
    Creates a public channel

    Returns a channel_id in a dictionary
    '''
    user_token = _USER_1['token']

    channel = {
        'token': user_token,
        'name': 'channel_1',
        'is_public': True,
    }

    payload = requests.post(url + '/channels/create', json=channel).json()
    return payload


@pytest.fixture
def _CHANNEL_2(url, _USER_1):
    '''
    Creates a public channel

    Returns a channel_id in a dictionary
    '''
    user_token = _USER_1['token']

    channel = {
        'token': user_token,
        'name': 'channel_2',
        'is_public': True,
    }

    payload = requests.post(url + '/channels/create', json=channel).json()
    return payload

@pytest.fixture
def valid_messages():
    '''
    Returns a list of valid messages
    '''
    message1 = 'Hello! How are we, everyone?'
    message2 = 'Wallah brusjan! Skjera? Turer du eller?'
    message3 = 'Hello World!'
    message4 = 'Message_send works...'
    message5 = '123'
    messages = [message1, message2, message3, message4, message5]
    return messages

@pytest.fixture
def invalid_message():
    '''
    Invalid message for message_send
    1001 characters long to test edge case
    '''
    message = ''.join(random.choice(string.ascii_letters) for _ in range(0, 1001))
    return message

################ STANDUP_START Tests ################

def test_server_standup_start_invalid_channel(url, _USER_1):
    """
    Test that Error 400 (InputError) is raised when an invalid
    channel_id is passed
    """

    token = _USER_1['token']
    channel_id = 1000
    length = 2

    details = {
        "token": token,
        "channel_id": channel_id,
        "length": length,
    }

    payload = requests.post(url + "/standup/start",
                           json=details).json()

    assert payload['code'] == 400
    assert payload['message'] == "<p>Please enter a valid channel id</p>"


def test_server_standup_start_invalid_length(url, _USER_1, _CHANNEL_1):
    """
    Test that Error 400 (InputError) is raised when an invalid
    channel_id is passed
    """

    token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    length = -2

    details = {
        "token": token,
        "channel_id": channel_id,
        "length": length,
    }

    payload = requests.post(url + "/standup/start",
                           json=details).json()

    assert payload['code'] == 400
    assert payload['message'] == "<p>Enter a valid length of time</p>"

def test_server_standup_start_user_not_in_channel(url, _USER_1, _USER_2, _CHANNEL_1):
    """
    Test that Error 400 (AccessError) is raised when user is not
    in channel
    """

    token = _USER_2['token']
    channel_id = _CHANNEL_1['channel_id']
    length = 2

    details = {
        "token": token,
        "channel_id": channel_id,
        "length": length,
    }

    payload = requests.post(url + "/standup/start",
                           json=details).json()

    assert payload['code'] == 400
    assert payload['message'] == "<p>User is not in channel</p>"

def test_server_standup_start_invalid_token(url, _USER_1, _CHANNEL_1):
    """
    Test that Error 400 (AccessError) is raised when invalid token
    is passed
    """

    token = auth.encode_token('invalid@gmail.com_i')
    channel_id = _CHANNEL_1['channel_id']
    length = 2

    details = {
        "token": token,
        "channel_id": channel_id,
        "length": length,
    }

    payload = requests.post(url + "/standup/start",
                           json=details).json()

    assert payload['code'] == 400
    assert payload['message'] == "<p>User is not authorised</p>"


def test_server_standup_start_success(url, _USER_1, _CHANNEL_1):
    """
    Test that Error 400 (AccessError) is raised when invalid token
    is passed
    """

    token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    length = 2

    details = {
        "token": token,
        "channel_id": channel_id,
        "length": length,
    }

    payload = requests.post(url + "/standup/start",
                           json=details).json()

    assert payload['time_finish'] is not None

def test_server_standup_start_already_active(url, _USER_1, _CHANNEL_1):
    """
    Test that Error 400 (AccessError) is raised when invalid token
    is passed
    """

    token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    length = 2

    details = {
        "token": token,
        "channel_id": channel_id,
        "length": length,
    }

    payload_1 = requests.post(url + "/standup/start",
                           json=details).json()
    
    assert payload_1["time_finish"] is not None

    payload_2 = requests.post(url + "/standup/start",
                           json=details).json()
    
    assert payload_2['code'] == 400
    assert payload_2['message'] == "<p>Standup is already active</p>"


################ STANDUP_ACTIVE Tests ################

def test_server_standup_active_invalid_channel(url, _USER_1):
    """
    Test that Error 400 (InputError) is raised when an invalid
    channel_id is passed
    """

    token = _USER_1['token']
    channel_id = 1000

    details = {
        "token": token,
        "channel_id": channel_id,
    }

    payload = requests.get(url + "/standup/active",
                           params=details).json()

    assert payload['code'] == 400
    assert payload['message'] == "<p>Please enter a valid channel id</p>"

def test_server_standup_active_user_not_in_channel(url, _USER_1, _USER_2, _CHANNEL_1):
    """
    Test that Error 400 (AccessError) is raised when user is not
    in channel
    """

    token = _USER_2['token']
    channel_id = _CHANNEL_1['channel_id']

    details = {
        "token": token,
        "channel_id": channel_id,
    }

    payload = requests.get(url + "/standup/active",
                           params=details).json()

    assert payload['code'] == 400
    assert payload['message'] == "<p>User is not in channel</p>"


def test_server_standup_active_invalid_token(url, _USER_1, _USER_2, _CHANNEL_1):
    """
    Test that Error 400 (AccessError) is raised when invalid token
    is passed
    """

    token = auth.encode_token('invalid@gmail.com_i')
    channel_id = _CHANNEL_1['channel_id']

    details = {
        "token": token,
        "channel_id": channel_id,
    }

    payload = requests.get(url + "/standup/active",
                           params=details).json()

    assert payload['code'] == 400
    assert payload['message'] == "<p>User is not authorised</p>"

def test_server_standup_active_inactive(url, _USER_1, _CHANNEL_1, _CHANNEL_2):
    """
    Test that standup_active correctly identifies no standup
    is occurring
    """

    token = _USER_1['token']
    channel_id = _CHANNEL_2['channel_id']

    details = {
        "token": token,
        "channel_id": channel_id,
    }

    payload = requests.get(url + "/standup/active",
                           params=details).json()

    assert payload['is_active'] is False
    assert payload['time_finish'] is None


################ STANDUP_SEND Tests ################

def test_server_standup_send_invalid_channel(url, _USER_1, valid_messages):
    """
    Test that Error 400 (InputError) is raised when an invalid
    channel_id is passed
    """

    token = _USER_1['token']
    channel_id = 1000
    message = valid_messages[0]

    details = {
        "token": token,
        "channel_id": channel_id,
        "message": message,
    }

    payload = requests.post(url + "/standup/send",
                           json=details).json()

    assert payload['code'] == 400
    assert payload['message'] == "<p>Please enter a valid channel id</p>"


def test_server_standup_send_invalid_token(url, _USER_1, _CHANNEL_1, valid_messages):
    """
    Test that Error 400 (AccessError) is raised when invalid token
    is passed
    """

    token = auth.encode_token('invalid@gmail.com_i')
    channel_id = _CHANNEL_1['channel_id']
    message = valid_messages[0]

    details = {
        "token": token,
        "channel_id": channel_id,
        "message": message,
    }

    payload = requests.post(url + "/standup/send",
                           json=details).json()

    assert payload['code'] == 400
    assert payload['message'] == "<p>User is not authorised</p>"


def test_server_standup_send_user_not_in_channel(url, _USER_1, _USER_2, _CHANNEL_1, valid_messages):
    """
    Test that Error 400 (AccessError) is raised when user is not in the
    channel
    """

    token = _USER_2['token']
    channel_id = _CHANNEL_1['channel_id']
    message = valid_messages[0]

    details = {
        "token": token,
        "channel_id": channel_id,
        "message": message,
    }

    payload = requests.post(url + "/standup/send",
                           json=details).json()

    assert payload['code'] == 400
    assert payload['message'] == "<p>User is not in channel</p>"

def test_server_standup_send_invalid_message(url, _USER_1, _CHANNEL_1, invalid_message):
    """
    Test that Error 400 (InputError) is raised when invalid message
    is sent
    """

    token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    message = invalid_message

    details = {
        "token": token,
        "channel_id": channel_id,
        "message": message,
    }

    payload = requests.post(url + "/standup/send",
                           json=details).json()

    assert payload['code'] == 400
    assert payload['message'] == "<p>Message longer than 1000 characters</p>"

def test_server_standup_send_inactive(url, _USER_1, _CHANNEL_1, valid_messages):
    """
    Test that Error 400 (InputError) is raised when no standup is currently
    running
    """

    token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    message = valid_messages[0]

    details = {
        "token": token,
        "channel_id": channel_id,
        "message": message,
    }

    payload = requests.post(url + "/standup/send",
                           json=details).json()

    assert payload['code'] == 400
    assert payload['message'] == "<p>Standup not currently active</p>"

def test_server_standup_send_success(url, _USER_1, _CHANNEL_1, valid_messages):
    """
    Test that Error 400 (InputError) is raised when no standup is currently
    running
    """


    token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    length = 5
    message = valid_messages[0]

    start = {
        "token": token,
        "channel_id": channel_id,
        "length": length,
    }
    requests.post(url + "/standup/start",
                           json=start).json()

    details = {
        "token": token,
        "channel_id": channel_id,
        "message": message,
    }

    payload = requests.post(url + "/standup/send",
                           json=details).json()

    assert payload == {}

