""" SERVER TESTS FOR CHANNELS FUNCTIONS """

from subprocess import Popen, PIPE
from time import sleep
import re
import signal
import json
import requests
import pytest
from auth import encode_token


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

def _USER_1(url):
    """
    Registers and logs in a user returning a dictionary containing the
    token and u_id.

    Returns:
        dictionary: {
            'token':
            'u_id:
            }
    """
    user = {
        'email': 'test@gmail.com',
        'password': 'iliketrains',
        'name_first': 'Oliver',
        'name_last': 'Xu'
    }

    login = {
        'email': 'test@gmail.com',
        'password': 'iliketrains'
    }

    requests.post(url + "/auth/register", json=user)
    payload = requests.post(url + "/auth/login", json=login).json()
    return payload

def _USER_2(url):
    """
    Registers and logs in another user returning a dictionary containing the
    token and u_id.

    Returns:
        dictionary: {
            'token':
            'u_id:
            }
    """
    user = {
        'email': 'hellothere@gmail.com',
        'password': 'ilikemonkeys',
        'name_first': 'Monty',
        'name_last': 'Python'
    }

    login = {
        'email': 'hellothere@gmail.com',
        'password': 'ilikemonkeys'
    }

    requests.post(url + "/auth/register", json=user)
    payload = requests.post(url + "/auth/login", json=login).json()
    return payload


################### HTTP TESTS FOR channels_list #########################

def test_url(url):
    """
    Sanity check to test that server is setup properly.
    """
    assert url.startswith("http")


def test_server_channels_list_none(url):
    """
    Test that the server returns an empty list when the user is part of
    NO channels.
    """

    token = _USER_1(url)['token']
    payload = requests.get(url + "/channels/list",
                           params={'token': token}).json()

    assert payload == {'channels': []}


def test_server_channels_list_spec(url):
    """
    Testing channels_list now that the user is part of a channel.
    """

    token = _USER_1(url)['token']

    channel_params = {
        'token': token,
        'name': 'testchannel',
        'is_public': True
    }
    requests.post(url + "/channels/create", json=channel_params).json()

    payload = requests.get(url + "/channels/list",
                           params={'token': token}).json()

    assert len(payload['channels']) == 1
    assert isinstance(payload['channels'], list) is True


def test_server_channels_list_multiple(url):
    """
    Test that channels_list returns the correct number of channels for
    a user who is part of multiple channels.
    """

    token = _USER_1(url)['token']

    channel_params = {
        'token': token,
        'name': 'testchannel',
        'is_public': True
    }

    requests.post(url + "/channels/create", json=channel_params).json()
    requests.post(url + "/channels/create", json=channel_params).json()
    requests.post(url + "/channels/create", json=channel_params).json()

    payload = requests.get(url + "/channels/list",
                           params={'token': token}).json()

    assert len(payload['channels']) == 3
    assert isinstance(payload['channels'], list) is True


def test_server_list_invalid_token(url):
    """
    Test that Error 400 (AccessError) is raised when an invalid token is
    passed.
    """

    invalid_token = encode_token("thisisaveryinvalidtoken")

    payload = requests.get(url + "/channels/list",
                           params={'token': invalid_token}).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>User is not authorised</p>")



#################### HTTP TESTS FOR channels_listall #####################

def test_server_channels_listall_none(url):
    """
    Test that channels_listall returns an empty list when no channels have
    been created.
    """

    token = _USER_1(url)['token']
    payload = requests.get(url + "/channels/listall",
                           params={'token': token}).json()

    assert payload == {'channels': []}


def test_server_channels_listall_single(url):
    """
    Testing channels_listall after one channel has been created.
    """

    token = _USER_1(url)['token']

    channel_params = {
        'token': token,
        'name': 'testchannel',
        'is_public': True
    }
    requests.post(url + "/channels/create", json=channel_params).json()

    payload = requests.get(url + "/channels/listall",
                           params={'token': token}).json()

    assert len(payload['channels']) == 1
    assert isinstance(payload['channels'], list) is True


def test_server_channels_listall_multiple(url):
    """
    Test that channels_listall returns ALL channels even if a user is
    NOT part of a channel.
    """
    token1 = _USER_1(url)['token']
    token2 = _USER_2(url)['token']

    channel_params1 = {
        'token': token1,
        'name': 'channel1',
        'is_public': True
    }

    channel_params2 = {
        'token': token2,
        'name': 'channel2',
        'is_public': True
    }

    requests.post(url + "/channels/create", json=channel_params1).json()
    requests.post(url + "/channels/create", json=channel_params2).json()

    # Note that _USER_2 is NOT part of channel1, but the payload should
    # still list all channels.
    payload = requests.get(url + "/channels/listall",
                           params={'token': token1}).json()

    assert len(payload['channels']) == 2
    assert isinstance(payload['channels'], list) is True


def test_server_channels_listall_invalid(url):
    """
    Test that Error 400 (AccessError) is raised when an invalid token is
    passed.
    """
    invalid_token = encode_token("thisisaninvalidtoken")

    payload = requests.get(url + "/channels/listall",
                           params={'token': invalid_token}).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>User is not authorised</p>")



################### HTTP TESTS FOR channels_create #######################

def test_server_channels_create(url):
    """
    Server test for creating a single channel.
    """

    user = _USER_1(url)

    channel_params = {
        'token': user['token'],
        'name': 'testchannel',
        'is_public': True
    }

    payload = requests.post(url + "/channels/create",
                            json=channel_params).json()

    assert isinstance(payload['channel_id'], int) is True


def test_server_channels_create_multiple(url):
    """
    Server test for creating multiple channels.
    """

    user = _USER_1(url)

    channel_params_1 = {
        'token': user['token'],
        'name': 'testchannel1',
        'is_public': True
    }

    channel_params_2 = {
        'token': user['token'],
        'name': 'testanotherchannel',
        'is_public': False
    }

    payload_1 = requests.post(url + "/channels/create",
                              json=channel_params_1).json()

    payload_2 = requests.post(url + "/channels/create",
                              json=channel_params_2).json()

    assert isinstance(payload_1['channel_id'], int) is True
    assert isinstance(payload_2['channel_id'], int) is True
    assert payload_1['channel_id'] != payload_2['channel_id']


def test_server_channel_name_too_long(url):
    """
    Test that Error 400 (InputError) is raised when the channel name is
    invalid (longer than 20 characters).
    """

    user = _USER_1(url)

    channel_params = {
        'token': user['token'],
        'name': 'testchannelthatiswayyyyyytoolong',
        'is_public': True
    }

    payload = requests.post(url + "/channels/create",
                            json=channel_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>Invalid channel name. Name must not be "
                                  "longer than 20 characters.</p>")


def test_server_create_invalid_user(url):
    """
    Test that Error 400 (AccessError) is raised when an invalid token is
    passed.
    """

    channel_params = {
        'token': encode_token('thisisaninvalidtoken'),
        'name': 'testchannel',
        'is_public': True
    }

    payload = requests.post(url + "/channels/create",
                            json=channel_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>User is not authorised</p>")
