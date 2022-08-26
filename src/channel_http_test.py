""" SERVER TESTS FOR CHANNEL FUNCTIONS """

from subprocess import Popen, PIPE
from time import sleep
from auth import encode_token
import re
import signal
import json
import requests
import pytest

# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
@pytest.fixture
def url():
    """
    Fixture to set up the url
    """
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
    Registers and logs in a user returning a dictionary
    containing the token and u_id.

    Returns:
        dictionary: {
            'token':
            'u_id:
            }
    """
    user_1 = {
        'email': 'liam.treavors@gmail.com',
        'password': 'mypassword1',
        'name_first': 'Liam',
        'name_last': 'Treavors'
    }

    login_1 = {
        'email': 'liam.treavors@gmail.com',
        'password': 'mypassword1'
    }

    requests.post(url + "/auth/register", json=user_1)
    payload = requests.post(url + "/auth/login", json=login_1).json()
    return payload

@pytest.fixture
def _USER_2(url):
    """
    Registers and logs in a user returning a dictionary
    containing the token and u_id.

    Returns:
        dictionary: {
            'token':
            'u_id:
            }
    """
    user_2 = {
        'email': 'daniel.steyn@gmail.com',
        'password': 'mypassword2',
        'name_first': 'Daniel',
        'name_last': 'Steyn'
    }

    login_2 = {
        'email': 'daniel.steyn@gmail.com',
        'password': 'mypassword2'
    }

    requests.post(url + "/auth/register", json=user_2)
    payload = requests.post(url + "/auth/login", json=login_2).json()
    return payload

@pytest.fixture
def _USER_3(url):
    """
    Registers and logs in a user returning a dictionary
    containing the token and u_id.

    Returns:
        dictionary: {
            'token':
            'u_id:
            }
    """
    user_3 = {
        'email': 'mikkel@gmail.com',
        'password': 'mypassword3',
        'name_first': 'Mikkel',
        'name_last': 'Endresen'
    }

    login_3 = {
        'email': 'mikkel@gmail.com',
        'password': 'mypassword3'
    }

    requests.post(url + "/auth/register", json=user_3)
    payload = requests.post(url + "/auth/login", json=login_3).json()
    return payload

@pytest.fixture
def _CHANNEL_1(url, _USER_1):
    """
    Creates a public channel
    """
    user_token = _USER_1["token"]

    ch_params = {
        'token': user_token,
        'name': 'channel_1',
        'is_public': True,
    }

    payload = requests.post(url + "/channels/create", json=ch_params).json()

    return payload

@pytest.fixture
def _CHANNEL_2(url, _USER_1):
    """
    Creates a private channel
    """
    user_token = _USER_1["token"]

    ch_params = {
        'token': user_token,
        'name': 'channel_2',
        'is_public': False,
    }

    payload = requests.post(url + "/channels/create", json=ch_params).json()

    return payload

################### HTTP TESTS FOR channel_details #########################

def test_url(url):
    """
    Sanity check to test that server is setup properly.
    """
    assert url.startswith("http")

def test_server_channel_details_invalid_token(url, _USER_2, _CHANNEL_1):
    """
    Test that Error 400 (AccessError) is raised when an invalid
    token is passed
    """

    channel_id = _CHANNEL_1["channel_id"]

    ch_params = {
        "token": encode_token("thisisaninvalidtoken"),
        "channel_id": channel_id
    }

    payload = requests.get(url + "/channel/details",
                           params=ch_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>User is not a member of this channel</p>")


def test_server_channel_details_invalid_channel(url, _USER_1):
    """
    Test that Error 400 (InputError) is raised when an invalid
    channel_id is entered
    """

    user_token = _USER_1['token']

    ch_params = {
        "token": user_token,
        "channel_id": 1000
    }

    payload = requests.get(url + "/channel/details",
                           params=ch_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>Please enter a valid channel id</p>")

def test_server_channel_details_success(url, _USER_1, _CHANNEL_1):
    """
    Test that an authorised user can successfully check the details
    of a channel they are a member of
    """

    user_token = _USER_1['token']
    channel_id = _CHANNEL_1["channel_id"]

    ch_params = {
        "token": user_token,
        "channel_id": channel_id
    }

    payload = requests.get(url + "/channel/details",
                           params=ch_params).json()

    assert payload['name'] == "channel_1"
    assert len(payload['owner_members']) == 1 
    assert len(payload['all_members']) == 1

################### HTTP TESTS FOR channel_invite #########################


def test_server_channel_invite_invalid_token(url, _USER_1, _USER_2, _USER_3, _CHANNEL_1):
    """
    Test that Error 400 (AccessError) is raised when an invalid
    token is passed
    """

    invalid_user_token = _USER_2['token']
    channel_id = _CHANNEL_1['channel_id']
    invite_user = _USER_3['u_id']

    ch_params = {
        "token": invalid_user_token,
        "channel_id": channel_id,
        "u_id": invite_user
    }

    payload = requests.post(url + "/channel/invite",
                            json=ch_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>User is not authorised</p>")


def test_server_channel_invite_invalid_channel(url, _USER_1, _USER_2):
    """
    Test that Error 400 (InputError) is raised when an invalid
    channel is passed
    """

    user_token = _USER_1['token']
    invite_user = _USER_2['u_id']

    ch_params = {
        "token": user_token,
        "channel_id": 1000,
        "u_id": invite_user,
    }

    payload = requests.post(url + "/channel/invite",
                            json=ch_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>Please enter a valid channel id</p>")


def test_server_channel_invite_invalid_user_id(url, _USER_1, _CHANNEL_1):
    """
    Test that Error 400 (InputError) is raised when an invalid
    user is passed
    """

    user_token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']

    ch_params = {
        "token": user_token,
        "channel_id": channel_id,
        "u_id": 1000
    }

    payload = requests.post(url + "/channel/invite",
                            json=ch_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>Please enter a valid user id</p>")


def test_server_channel_invite_single(url, _USER_1, _USER_2, _CHANNEL_1):
    """
    Testing that channel invite works successfully
    """

    user_token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    invite_user = _USER_2['u_id']

    ch_params = {
        "token": user_token,
        "channel_id": channel_id,
        "u_id": invite_user,
    }

    requests.post(url + "/channel/invite", json=ch_params).json()

    ch_det_params = {
        "token": user_token,
        "channel_id": channel_id,
    }

    payload = requests.get(url + "/channel/details",
                           params=ch_det_params).json()

    assert len(payload["all_members"]) == 2
    assert len(payload["owner_members"]) == 1

def test_server_channel_invite_multiple(url, _USER_1, _USER_2, _USER_3, _CHANNEL_1):
    """
    Testing that channel invite works successfully
    """

    user_token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    invite_user_2 = _USER_2["u_id"]
    invite_user_3 = _USER_3["u_id"]

    ch_params_2 = {
        "token": user_token,
        "channel_id": channel_id,
        "u_id": invite_user_2,
    }

    ch_params_3 = {
        "token": user_token,
        "channel_id": channel_id,
        "u_id": invite_user_3,
    }

    requests.post(url + "/channel/invite", json=ch_params_2).json()
    requests.post(url + "/channel/invite", json=ch_params_3).json()

    ch_det_params = {
        "token": user_token,
        "channel_id": channel_id,
    }

    payload = requests.get(url + "/channel/details",
                           params=ch_det_params).json()

    assert len(payload["all_members"]) == 3
    assert len(payload["owner_members"]) == 1
    
    
################### HTTP TESTS FOR channel_messages #########################

def test_server_channel_messages_invalid_channel(url, _USER_1, _USER_2, _CHANNEL_1):
    '''
    Testing invalid channel
    Expected error code: 400
    '''
    user_token = _USER_2['token']
    invalid_channel = 0

    messages = {
        'token': user_token,
        'channel_id': invalid_channel,
        'start': 0,
    }
    payload = requests.get(url + '/channel/messages', params=messages).json()

    assert payload['code'] == 400
    assert payload['message'] == ('<p>Invalid Channel ID</p>')

def test_server_channel_messages_simple_messages(url, _USER_1, _CHANNEL_1):
    '''
    Simple success test
    Checks that length is 2 and last element of ['messages'] is -1
    '''
    sender_token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    message = 'Hello, You reckon this works?'

    message_send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    requests.post(url + '/message/send', json=message_send).json()

    messages = {
        'token': sender_token,
        'channel_id': channel_id,
        'start': 0,
    }
    payload = requests.get(url + '/channel/messages', params=messages).json()
    assert len(payload['messages']) == 1
    assert payload['messages'][0]['message'] == message
    assert payload['end'] == -1

def test_server_channel_messages_invalid_start(url, _USER_1, _CHANNEL_1):
    '''
    Testing invalid start value, for start value greater than total messages
    Expected errror code: 400
    '''
    user_token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    messages = {
        'token': user_token,
        'channel_id': channel_id,
        'start': 3,
    }
    payload = requests.get(url + '/channel/messages', params=messages).json()
    
    assert payload['code'] == 400
    assert payload['message'] == ('<p>Invalid start value</p>')

def test_server_channel_messages_invalid_token(url, _USER_1, _CHANNEL_1, _USER_3):
    '''
    Testing for invalid token
    Expected error code 400
    '''
    user_token = _USER_3['token']
    channel_id = _CHANNEL_1['channel_id']
    messages = {
        'token': user_token,
        'channel_id': channel_id,
        'start': 0,
    }
    payload = requests.get(url + '/channel/messages', params=messages).json()

    assert payload['code'] == 400
    assert payload['message'] == ('<p>User is not authorised</p>')

### THESE TESTS CAUSES THE PIPELINE TO GET STUCK!!! PLEASE FIX!!!

def test_server_channel_messages_more_than_fifty(url, _USER_1, _USER_3, _CHANNEL_1):
    '''
    51 messages to check the edge case
    Make sure last element is not -1 and that the length of
    ['messages'] is 50
    Message sent outside for loop should be the first element of ['messages']
    '''
    user_token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    message_one = 'Ahh yeaah mate'
    send = {
        'token': user_token,
        'channel_id': channel_id,
        'message': message_one,
    }
    for _ in range(51):
        requests.post(url + '/message/send', json=send)

    message_two = 'This is the most recent message'
    send = {
        'token': user_token,
        'channel_id': channel_id,
        'message': message_two,
    }
    requests.post(url + '/message/send', json=send)

    parameters = {
        'token': user_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_data = requests.get(url + '/channel/messages', params=parameters).json()

    assert len(messages_data['messages']) == 50
    assert messages_data['messages'][0]['message'] == message_two
    assert messages_data['messages'][49]['message'] == message_one

def test_server_channel_messages_less_than_fifty(url, _USER_1, _USER_3, _CHANNEL_1):
    '''
    Testing for 49 messeges for edge case
    Make sure last element is -1
    '''
    user_token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    message_one = 'Ahh yeaah mate'
    send = {
        'token': user_token,
        'channel_id': channel_id,
        'message': message_one,
    }
    for _ in range(49):
        requests.post(url + '/message/send', json=send)

    parameters = {
        'token': user_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_data = requests.get(url + '/channel/messages', params=parameters).json()

    assert len(messages_data['messages']) == 49
    assert messages_data['messages'][0]['message'] == message_one
    assert messages_data['end'] == -1

################### HTTP TESTS FOR channel_leave #########################

def test_server_channel_leave_invalid_channel(url, _USER_1):
    '''
    Test input error (Error 400) when passing an invalid channel ID
    '''
    user_token = _USER_1['token']
    invalid_channel_id = 1000

    ch_params = {
        "token": user_token,
        "channel_id": invalid_channel_id,
    }

    payload = requests.post(url + "/channel/leave", json=ch_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>Invalid Channel ID</p>")


def test_server_channel_leave_access_error(url, _USER_2, _CHANNEL_1):
    '''
    Test access error (Error 400) when attempting to leave a channel the
    authorised user is not a member of.
    '''
    invalid_user_token = _USER_2['token']
    channel_id = _CHANNEL_1['channel_id']

    ch_params = {
        "token": invalid_user_token,
        "channel_id": channel_id,
    }

    payload = requests.post(url + "/channel/leave", json=ch_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>Current user is not a member of channel</p>")


def test_server_channel_leave_success(url, _USER_1, _CHANNEL_1, _USER_2):
    '''
    Test a valid channel leave instance.
    '''
    # Invite single user so channel is not empty
    user_token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    invite_user = _USER_2['u_id']

    ch_params = {
        "token": user_token,
        "channel_id": channel_id,
        "u_id": invite_user,
    }

    requests.post(url + "/channel/invite", json=ch_params).json()

    # Leave
    user_token = _USER_2['token']
    channel_id = _CHANNEL_1['channel_id']

    ch_params = {
        "token": user_token,
        "channel_id": channel_id,
    }

    requests.post(url + "/channel/leave", json=ch_params).json()

    # Retrieve channel details
    owner_token = _USER_1['token']
    ch_det_params = {
        "token": owner_token,
        "channel_id": channel_id,
    }

    payload = requests.get(url + "/channel/details", params=ch_det_params).json()

    assert len(payload["all_members"]) == 1
    assert len(payload["owner_members"]) == 1

################### HTTP TESTS FOR channel_join #########################

def test_server_channel_join_invalid_channel(url, _USER_2):
    '''
    Test input error (Error 400) when invalid channel ID is passed.
    '''
    user_token = _USER_2['token']
    invalid_channel_id = 1000

    ch_params = {
        "token": user_token,
        "channel_id": invalid_channel_id,
    }

    payload = requests.post(url + "/channel/join", json=ch_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>Invalid Channel ID</p>")

def test_server_channel_join_private_channel(url, _USER_1, _USER_3, _CHANNEL_2):
    '''
    Test access error (Error 400) when channel is private
    '''
    user_token = _USER_3['token']
    channel_id = _CHANNEL_2['channel_id']

    ch_params = {
        "token": user_token,
        "channel_id": channel_id,
    }

    payload = requests.post(url + "/channel/join", json=ch_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>Channel is private</p>")

def test_server_channel_join_success(url, _USER_1, _USER_2, _CHANNEL_1):
    '''
    Test a valid channel_join instance.
    '''
    user_token = _USER_2['token']
    channel_id = _CHANNEL_1['channel_id']

    ch_params = {
        "token": user_token,
        "channel_id": channel_id,
    }

    requests.post(url + "/channel/join", json=ch_params).json()

    owner_token = _USER_1['token']

    # Retrieve channel details
    ch_det_params = {
        "token": owner_token,
        "channel_id": channel_id,
    }

    payload = requests.get(url + "/channel/details", params=ch_det_params).json()

    user_id = _USER_2['u_id']
    assert len(payload["all_members"]) == 2
    assert user_id == payload["all_members"][1]['u_id']
    assert len(payload["owner_members"]) == 1

################### HTTP TESTS FOR channel_addowner #########################


def test_server_channel_addowner_invalid_id(url, _USER_1, _CHANNEL_1):
    '''
    Test an input error (Error 400) when the user ID passed is invalid.
    '''
    user_token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    invalid_u_id = 1000

    ch_params = {
        "token": user_token,
        "channel_id": channel_id,
        "u_id": invalid_u_id,
    }

    payload = requests.post(url + "/channel/addowner", json=ch_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>Invalid u_id</p>")

def test_server_channel_addowner_invalid_channel(url, _USER_1, _USER_2):
    '''
    Test an input error (Error 400) when the channel ID passed is invalid.
    '''
    user_token = _USER_1['token']
    invalid_channel_id = 1000
    u_id = _USER_2['u_id']

    ch_params = {
        "token": user_token,
        "channel_id": invalid_channel_id,
        "u_id": u_id,
    }

    payload = requests.post(url + "/channel/addowner", json=ch_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>Invalid Channel ID</p>")

def test_server_channel_addowner_access_error(url, _USER_1, _USER_2, _USER_3, _CHANNEL_2):
    '''
    Test an access error (Error 400) when the authorised user is not an
    owner of the channel nor a global owner.
    '''
    user_token = _USER_2['token']
    channel_id = _CHANNEL_2['channel_id']
    u_id = _USER_3['u_id']

    ch_params = {
        "token": user_token,
        "channel_id": channel_id,
        "u_id": u_id,
    }

    payload = requests.post(url + "/channel/addowner", json=ch_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>Current user is not a flockr nor channel owner</p>")

def test_server_channel_addowner_user_already_owner(url, _USER_1, _CHANNEL_1):
    '''
    Test an access error (Error 400) when the u_id belongs to a user who is already an
    owner of the channel
    '''
    user_token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    user_id = _USER_1['u_id']

    ch_params = {
        "token": user_token,
        "channel_id": channel_id,
        "u_id": user_id,
    }

    payload = requests.post(url + "/channel/addowner", json=ch_params).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>User is already an owner of the channel</p>")

def test_server_channel_addowner_success(url, _USER_1, _USER_2, _CHANNEL_1):
    '''
    Test a valid instance of add owner.
    '''
    user_token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    user_id = _USER_2['u_id']

    ch_params = {
        "token": user_token,
        "channel_id": channel_id,
        "u_id": user_id,
    }

    requests.post(url + "/channel/addowner", json=ch_params).json()

    # Retrieve channel details
    ch_det_params = {
        "token": user_token,
        "channel_id": channel_id,
    }

    payload = requests.get(url + "/channel/details", params=ch_det_params).json()

    assert len(payload["all_members"]) == 2
    assert user_id == payload["all_members"][1]['u_id']
    assert len(payload["owner_members"]) == 2
    assert user_id == payload["owner_members"][1]['u_id']

################### HTTP TESTS FOR channel_removeowner #########################

def test_server_channel_removeowner_invalid_channel(url, _USER_1, _USER_3):
    '''
    Testing for invalid channel
    Expected error code: 400
    '''
    user_token = _USER_1['token']
    invalid_channel = 2
    user_id = _USER_3['u_id']
    parameters = {
        'token': user_token,
        'channel_id': invalid_channel,
        'u_id': user_id,
    }
    payload = requests.post(url + '/channel/removeowner', json=parameters).json()

    assert payload['code'] == 400
    assert payload['message'] == ('<p>Invalid Channel ID</p>')

def test_server_channel_removeowner_invalid_owner(url, _USER_1, _CHANNEL_1, _USER_3):
    '''
    Invalid owner, u_id to be removed not an owner of channel
    Error code expected: 400
    '''
    user_token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    user_id = _USER_3['u_id']
    parameters = {
        'token': user_token,
        'channel_id': channel_id,
        'u_id': user_id,
    }
    payload = requests.post(url + '/channel/removeowner', json=parameters).json()

    assert payload['code'] == 400
    assert payload['message'] == ('<p>User is not owner of channel</p>')

def test_server_channel_removeowner_invalid_token(url, _USER_1, _CHANNEL_1, _USER_3):
    '''
    Check that the user is authorized, owner of the channel
    '''
    user_token = _USER_3['token']
    channel_id = _CHANNEL_1['channel_id']
    user_id = _USER_1['u_id']
    parameters = {
        'token': user_token,
        'channel_id': channel_id,
        'u_id': user_id,
    }
    payload = requests.post(url + '/channel/removeowner', json=parameters).json()

    assert payload['code'] == 400
    assert payload['message'] == ('<p>Access Error</p>')

def test_server_channel_removeowner_flockr_owner(url, _USER_2, _USER_1, _CHANNEL_1, _USER_3):
    '''
    Check that the flockr owner can succsessfully remove an owner
    _USER_2 is flockr owner
    '''
    user_token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    user_id = _USER_3['u_id']
    addowner = {
        'token': user_token,
        'channel_id': channel_id,
        'u_id': user_id,
    }
    requests.post(url + '/channel/addowner', json=addowner)

    flockr_owner = _USER_2['token']
    removeowner = {
        'token': flockr_owner,
        'channel_id': channel_id,
        'u_id': user_id,
    }
    requests.post(url + '/channel/removeowner', json=removeowner)

    details = {
        'token': user_token,
        'channel_id': channel_id,
    }
    payload = requests.get(url + '/channel/details', params=details).json()

    assert len(payload['owner_members']) == 1

def test_server_channel_removeowner_channel_owner(url, _USER_2, _USER_1, _CHANNEL_1, _USER_3):
    '''
    Check a successful case where the channel owner removes an owner
    '''
    user_token = _USER_1['token']
    channel_id = _CHANNEL_1['channel_id']
    user_id = _USER_3['u_id']
    addowner = {
        'token': user_token,
        'channel_id': channel_id,
        'u_id': user_id,
    }
    requests.post(url + '/channel/addowner', json=addowner)

    removeowner = {
        'token': user_token,
        'channel_id': channel_id,
        'u_id': user_id,
    }
    requests.post(url + '/channel/removeowner', json=removeowner)

    details = {
        'token': user_token,
        'channel_id': channel_id,
    }
    payload = requests.get(url + '/channel/details', params=details).json()

    assert len(payload['owner_members']) == 1
