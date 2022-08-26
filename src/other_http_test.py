'''running tests for user functions'''

import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import pytest

@pytest.fixture
def url():
    '''generates a url for flask testing'''
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

@pytest.fixture
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


@pytest.fixture
def _USER_3(url):
    """

    Registersanother user returning a dictionary containing the
    token and u_id.

    Returns:
        dictionary: {
            'token':
            'u_id:
            }

    """
    user = {
        'email': 'mikkel@gmail.com',
        'password': 'mypassword2',
        'name_first': 'Mikkel',
        'name_last': 'Endresen'
    }

    payload = requests.post(url + "/auth/register", json=user).json()
    return payload



################# FIXTURES FOR CREATING CHANNEL AND SENDING MESSAGES #######

@pytest.fixture
def channel_1(url, _USER_1, _USER_2):
    """

    Sets up a channel to send messages in

    Returns:
        channel_id (integer):

    """
    params = {
        "token": _USER_1['token'],
        "name": "channel_1",
        "is_public": True,
    }

    payload = requests.post(url + "/channels/create", json=params).json()

    invite_user_2 = {
        "token": _USER_1['token'],
        "channel_id": payload['channel_id'],
        "u_id": _USER_2['u_id'],
    }
    requests.post(url + "/channel/invite", json=invite_user_2).json()

    return payload

@pytest.fixture
def channel_2(url, _USER_1, _USER_2):
    """

    Sets up a channel to send messages in

    Returns:
        channel_id (integer):

    """
    params = {
        "token": _USER_1['token'],
        "name": "channel_2",
        "is_public": True,
    }

    payload = requests.post(url + "/channels/create", json=params).json()

    return payload

@pytest.fixture
def send_messages(url, _USER_1, _USER_2, channel_1, channel_2):
    """
    Send messages to each channel
    """
    msg_1 = {
        "token": _USER_1['token'],
        "channel_id": channel_1['channel_id'],
        "message": "hello world",
    }

    msg_2 = {
        "token": _USER_2['token'],
        "channel_id": channel_1['channel_id'],
        "message": "hello",
    }

    msg_3 = {
        "token": _USER_1['token'],
        "channel_id": channel_2['channel_id'],
        "message": "hello worl",
    }

    msg_4 = {
        "token": _USER_1['token'],
        "channel_id": channel_2['channel_id'],
        "message": "hello w",
    }

    requests.post(url + "/message/send", json=msg_1).json()
    requests.post(url + "/message/send", json=msg_2).json()
    requests.post(url + "/message/send", json=msg_3).json()
    requests.post(url + "/message/send", json=msg_4).json()

    return {}



################## HTTP Tests for users_all #####################

def test_users_all_one_user(url, _USER_1):
    """
    testing users_all server for one users
    """

    token = _USER_1['token']

    all_users = requests.get(url + "/users/all",
                             params={'token': token}).json()

    assert all_users == {'users': [{'u_id': 1,
                          'email': 'test@gmail.com',
                          'name_first': 'Oliver',
                          'name_last': 'Xu',
                          'handle_str': 'oliverxu0',
                          'profile_img_url': None
                         }]}

def test_users_all_two_users(url, _USER_1, _USER_2):
    """
    testing users_all server for one users
    """

    token = _USER_2['token']

    all_users = requests.get(url + "/users/all",
                             params={'token': token}).json()

    assert all_users == {'users': [{'u_id': 1,
                          'email': 'test@gmail.com',
                          'name_first': 'Oliver',
                          'name_last': 'Xu',
                          'handle_str': 'oliverxu0',
                          'profile_img_url': None
                         },
                         {'u_id': 2,
                          'email': 'hellothere@gmail.com',
                          'name_first': 'Monty',
                          'name_last': 'Python',
                          'handle_str': 'montypython0',
                          'profile_img_url': None
                         }]}

################## HTTP Tests for admin_userpermission_change #####################

def test_server_admin_permission_invalid_token(url, _USER_1, _USER_2):
    """
    Test that Error 400 (AccessError) is raised when an invalid
    token is passed, i.e. user is not an owner
    """

    invalid_user_token = _USER_2['token']
    change_user = _USER_1['u_id']
    permission_id = 2

    perm_params = {
        "token": invalid_user_token,
        "u_id": change_user,
        "permission_id": permission_id,
    }

    payload = requests.post(url + "/admin/userpermission/change",
                            json=perm_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>User is not authorised</p>")


def test_server_admin_permission_invalid_user_id(url, _USER_1):
    """
    Test that Error 400 (InputError) is raised when an invalid
    user_id is passed
    """

    user_token = _USER_1['token']
    change_user = 1000
    permission_id = 1

    perm_params = {
        "token": user_token,
        "u_id": change_user,
        "permission_id": permission_id,
    }

    payload = requests.post(url + "/admin/userpermission/change",
                            json=perm_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>Please enter a valid user id</p>")

def test_server_admin_permission_invalid_permission_id(url, _USER_1, _USER_2):
    """
    Test that Error 400 (InputError) is raised when an invalid
    permission_id is passed
    """

    user_token = _USER_1['token']
    change_user = _USER_2['u_id']
    permission_id = 1000

    perm_params = {
        "token": user_token,
        "u_id": change_user,
        "permission_id": permission_id,
    }

    payload = requests.post(url + "/admin/userpermission/change",
                            json=perm_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>Please enter a valid permission id</p>")

def test_server_admin_userpermission_change_success(url, _USER_1, _USER_2):
    """
    Testing that admin_userpermission_change works successfully
    """

    user_token = _USER_1['token']
    change_user = _USER_2['u_id']
    permission_id = 1

    perm_params = {
        "token": user_token,
        "u_id": change_user,
        "permission_id": permission_id,
    }

    payload = requests.post(url + "/admin/userpermission/change",
                            json=perm_params).json()

    assert payload == {}

def test_server_admin_userpermission_change_multiple(url, _USER_1, _USER_2):
    """
    Testing that admin_userpermission_change works successfully
    by performing multiple permission changes until an AccessError
    is called from a previous admin
    """

    # set user_2 to be admin
    user_token = _USER_1['token']
    change_user = _USER_2['u_id']
    permission_id = 1

    perm_1_params = {
        "token": user_token,
        "u_id": change_user,
        "permission_id": permission_id,
    }

    payload = requests.post(url + "/admin/userpermission/change",
                            json=perm_1_params).json()

    assert payload == {}

    # set user_1 to be non admin
    user_token = _USER_2['token']
    change_user = _USER_1['u_id']
    permission_id = 2

    perm_2_params = {
        "token": user_token,
        "u_id": change_user,
        "permission_id": permission_id,
    }

    payload = requests.post(url + "/admin/userpermission/change",
                            json=perm_2_params).json()

    assert payload == {}

    # try to get user_1 to change permissions
    payload = requests.post(url + "/admin/userpermission/change",
                            json=perm_1_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>User is not authorised</p>")

################## HTTP Tests for search #####################

def test_server_search_error(url, _USER_1, _USER_3, channel_1):
    """
    Test that search returns an error when an invalid token is passed
    """
    token = _USER_3['token']
    requests.post(url + "/auth/logout", json=token).json()

    invalid_user_token = _USER_3['token']
    query_string = "hello"

    search = {
        "token": invalid_user_token,
        "query_str": query_string,
    }

    payload = requests.get(url + "/search",
                           params=search).json()
    print(payload)
    #assert payload["code"] == 400
    #assert payload["message"] == ("<p>User is not authorised</p>")
    


def test_server_search_no_messages(url, _USER_1, channel_1):
    """
    Test that search returns an empty list when no messages exist
    """

    user_token = _USER_1['token']
    query_string = "hello"

    search = {
        "token": user_token,
        "query_str": query_string,
    }

    payload = requests.get(url + "/search",
                           params=search).json()

    assert len(payload['messages']) == 0

def test_server_search_no_match(url, _USER_1, channel_1, send_messages):
    """
    Test that search returns an empty list when no messages match the
    query string
    """

    user_token = _USER_1['token']
    query_string = "this should not match anything"

    search = {
        "token": user_token,
        "query_str": query_string,
    }

    payload = requests.get(url + "/search",
                           params=search).json()

    assert len(payload['messages']) == 0

def test_server_search_match(url, _USER_1, channel_1, send_messages):
    """
    Test that search returns an messages when they exactly
    match the query string
    """

    user_token = _USER_1['token']
    query_string = "hello world"

    search = {
        "token": user_token,
        "query_str": query_string,
    }

    payload = requests.get(url + "/search",
                           params=search).json()

    assert len(payload['messages']) == 1
    assert payload['messages'][0]['message'] == "hello world"

def test_server_search_multiple_matches(url, _USER_1, channel_1, channel_2, send_messages):
    """
    Test that search returns multiple messages from multiple channels
    """

    user_token = _USER_1['token']
    query_string = "hello"

    search = {
        "token": user_token,
        "query_str": query_string,
    }

    payload = requests.get(url + "/search",
                           params=search).json()

    assert len(payload['messages']) == 4

def test_server_search_not_all_channels(url, _USER_1, _USER_2, channel_1, channel_2, send_messages):
    """
    Test that search only returns messages from channels user
    is a part of
    """
    user_token = _USER_2['token']
    query_string = "hello"

    search = {
        "token": user_token,
        "query_str": query_string,
    }

    payload = requests.get(url + "/search",
                           params=search).json()

    assert len(payload['messages']) == 2



################## HTTP Tests for clear #####################

def test_server_clear(url, _USER_1, _USER_2):
    """
    Test that clear function works in server
    """

    create_channel = {
        "token": _USER_1["token"],
        "name": "temporary",
        "ispublic": True,
    }

    requests.post(url + "/channels/create", json=create_channel).json()

    payload = requests.delete(url + "/clear").json()

    assert payload == {}

    new_user = {
        'email': 'mikkel@gmail.com',
        'password': 'mypassword2',
        'name_first': 'Mikkel',
        'name_last': 'Endresen'
    }

    login = {
        'email': 'mikkel@gmail.com',
        'password': 'mypassword2'
    }

    requests.post(url + "/auth/register", json=new_user)
    payload = requests.post(url + "/auth/login",
                            json=login).json()


    user_list = requests.get(url + "/users/all",
                             params={'token':payload['token']}).json()

    # only user should now be Mikkel
    assert len(user_list['users']) == 1
    assert user_list['users'][0]['u_id'] == payload['u_id']
    assert user_list['users'][0]['email'] == "mikkel@gmail.com"
    assert user_list['users'][0]['name_first'] == "Mikkel"
    assert user_list['users'][0]['name_last'] == "Endresen"

    channel_list = requests.get(url + "/channels/listall",
                                params={'token':payload['token']}).json()
    assert channel_list['channels'] == []
