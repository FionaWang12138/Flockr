''' SERVER TESTS FOR MESSAGE FUNCTIONS '''

import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
import random
import string
import time
import datetime as dt
from datetime import datetime
from datetime import timedelta

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
    token and u_id.

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
def _CHANNEL_pub(url, _USER_2):
    '''
    Creates a public channel

    Returns a channel_id in a dictionary
    '''
    user_token = _USER_2['token']

    channel = {
        'token': user_token,
        'name': 'channel_1',
        'is_public': True,
    }

    payload = requests.post(url + '/channels/create', json=channel).json()
    return payload

@pytest.fixture
def _CHANNEL_priv(url, _USER_2):
    '''
    Creates a private channel

    Returns a channel_id in a dictionary
    '''
    user_token = _USER_2['token']

    channel = {
        'token': user_token,
        'name': 'channel_1',
        'is_public': False,
    }

    payload = requests.post(url + '/channels/create', json=channel).json()
    return payload

@pytest.fixture
def valid_messages():
    '''
    Returns a list of two valid messages
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

@pytest.fixture
def add_to_channel(url, _USER_2, _CHANNEL_pub, _USER_3):
    '''
    Adds _USER_3 to the public channel

    Returns nothing
    '''
    channel = {
        'token': _USER_2['token'],
        'channel_id': _CHANNEL_pub['channel_id'],
        'u_id': _USER_3['u_id']
    }
    requests.post(url + '/channel/invite', json=channel).json()


################### HTTP TESTS FOR MESSAGE_SEND ###################

# Successful case
def test_server_send_success(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test valid message_send instances
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    requests.post(url + '/message/send', json=send).json()

    owner_token = _USER_2['token']
    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert messages_payload['messages'][0]['message'] == valid_messages[0]
    assert len(messages_payload['messages']) == 1

    for i in range(1, 5):
        message = valid_messages[i]

        send = {
            'token': sender_token,
            'channel_id': channel_id,
            'message': message,
        }
        requests.post(url + '/message/send', json=send).json()

    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert messages_payload['messages'][2]['message'] == valid_messages[2]
    assert len(messages_payload['messages']) == 5


# Flockr owner attempting to send message to a channel they are not a member of
def test_server_send_owner(url, _USER_1, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test flockr owner send message to a channel they aren't in
    '''
    sender_token = _USER_1['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    requests.post(url + '/message/send', json=send).json()

    owner_token = _USER_2['token']
    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert messages_payload['messages'][0]['message'] == valid_messages[0]
    assert len(messages_payload['messages']) == 1

# Non-member attempting to send message
def test_server_send_non_member(url, _USER_1, _USER_3, _CHANNEL_pub, _CHANNEL_priv, valid_messages):
    '''
    Test where the user sending the message is not a member of the channel
    Error code expected: 400
    '''
    # Sending to a public channel
    sender_token = _USER_3['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    assert message_payload['code'] == 400
    assert message_payload['message'] == ('<p>User not in given channel</p>')

    # Sending to a private channel
    channel_id = _CHANNEL_priv['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    assert message_payload['code'] == 400
    assert message_payload['message'] == ('<p>User not in given channel</p>')

# Message length equal to 999
def test_server_send_message_length_999(url, _USER_2, _CHANNEL_pub):
    '''
    Test edge case for length of message.
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = ''.join(random.choice(string.ascii_letters) for _ in range(999))

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    requests.post(url + '/message/send', json=send)

    owner_token = _USER_2['token']
    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert message == messages_payload['messages'][0]['message']
    assert len(messages_payload['messages']) == 1

# Message length equal to 1000
def test_server_send_message_length_1000(url, _USER_2, _CHANNEL_pub):
    '''
    Test edge case for length of message.
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = ''.join(random.choice(string.ascii_letters) for _ in range(1000))

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    requests.post(url + '/message/send', json=send)

    owner_token = _USER_2['token']
    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert message == messages_payload['messages'][0]['message']
    assert len(messages_payload['messages']) == 1

# Message length greater than 1000 characters
def test_server_send_message_too_long(url, _USER_2, _CHANNEL_pub, invalid_message):
    '''
    Test for a message too long
    Error code expected: 400
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = invalid_message

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    assert message_payload['code'] == 400
    assert message_payload['message'] == ('<p>Message longer than 1000 characters</p>')

# Check that message_send generates a new id for each message
def test_server_send_message_new_id(url, _CHANNEL_pub, _USER_2, valid_messages):
    '''
    Test to check that message_send creates a different id for each message
    '''
    # Message 1
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload1 = requests.post(url + '/message/send', json=send).json()

    # Message 2
    message = valid_messages[1]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload2 = requests.post(url + '/message/send', json=send).json()

    assert message_payload1['message_id'] is not message_payload2['message_id']

################### HTTP TESTS FOR MESSAGE_REMOVE #################

# Successful case (user sent the message)
def test_server_remove_sender(url, _USER_2, _CHANNEL_pub, valid_messages, add_to_channel, _USER_3):
    '''
    Test to see if messaged is removed with success when the sender
    is the one that removes it
    '''
    sender_token = _USER_3['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    message_id = message_payload['message_id']
    remove = {
        'token': sender_token,
        'message_id': message_id,
    }
    requests.delete(url + '/message/remove', json=remove).json()

    owner_token = _USER_2['token']
    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert valid_messages[0] not in messages_payload['messages']
    assert len(messages_payload['messages']) == 0

# Successful case (user is owner of the channel but not the sender)
def test_server_remove_owner(url, _USER_2, _CHANNEL_pub,
                             valid_messages, add_to_channel, _USER_3):
    '''
    Test a valid message_remove instance, user removing the message
    is the channel owner, not the sender nor the flockr owner.
    '''
    sender_token = _USER_3['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    owner_token = _USER_2['token']
    message_id = message_payload['message_id']
    remove = {
        'token': owner_token,
        'message_id': message_id,
    }
    requests.delete(url + '/message/remove', json=remove).json()

    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert valid_messages[0] not in messages_payload['messages']
    assert len(messages_payload['messages']) == 0

# Successful case (user is owner of the flockr but not the sender)
def test_server_remove_success_flockr(url, _USER_1, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test a valid message_remove instance, user removing the message
    is the flockr owner, not the sender nor the channel owner.
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    owner_token = _USER_1['token']
    message_id = message_payload['message_id']
    remove = {
        'token': owner_token,
        'message_id': message_id,
    }
    requests.delete(url + '/message/remove', json=remove).json()

    messages = {
        'token': sender_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert valid_messages[0] not in messages_payload['messages']
    assert len(messages_payload['messages']) == 0

# Non-owner attempting to remove a message they didn't send
def test_server_remove_invalid_user_removing(url, _USER_2, _CHANNEL_pub, valid_messages, _USER_3):
    '''
    Test where the user attempting to remove the message did not
    originally send the message and is not an owner of the flockr
    nor the channel
    Error code expected: 400
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    message_id = message_payload['message_id']
    invalid_token = _USER_3['token']
    remove = {
        'token': invalid_token,
        'message_id': message_id,
    }
    payload = requests.delete(url + '/message/remove', json=remove).json()

    assert payload['code'] == 400
    assert payload['message'] == ('<p>User not authorized</p>')

# Message (based on ID) no longer exists
def test_server_remove_invalid_message_id(url, _USER_2, _CHANNEL_pub, valid_messages, _USER_1):
    '''
    Test where the message (based on message_id) no longer exists
    Error code expected: 400
    '''

    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    message_id = message_payload
    remove = {
        'token': sender_token,
        'message_id': message_id,
    }
    requests.delete(url + '/message/remove', json=remove).json()

    remove = {
        'token': sender_token,
        'message_id': message_id,
    }
    payload = requests.delete(url + '/message/remove', json=remove).json()

    assert payload['code'] == 400
    assert payload['message'] == ('<p>Message does not exist</p>')

################### HTTP TESTS FOR MESSAGE_EDIT ###################

# Successful case (user sent the message)
def test_server_edit_success_sender(url, _USER_2, _CHANNEL_pub,
                                     _USER_3, add_to_channel, valid_messages):
    '''
    Test a valid message_edit instance, user editing the message is the
    original sender
    '''
    sender_token = _USER_3['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    message_id = message_payload['message_id']
    message = valid_messages[2]

    edit = {
        'token': sender_token,
        'message_id': message_id,
        'message': message,
    }
    requests.put(url + '/message/edit', json=edit)

    owner_token = _USER_2['token']
    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert valid_messages[0] not in messages_payload['messages']
    assert valid_messages[2] == messages_payload['messages'][0]['message']
    assert len(messages_payload['messages']) == 1

# Successful case (user is owner of the channel but not the sender)
def test_server_edit_owner(url, _USER_2, _USER_3, _CHANNEL_pub, valid_messages, add_to_channel):
    '''
    Test a valid message_edit instance, user editing the message is the
    owner of the channel but not the sender nor flockr owner
    '''
    sender_token = _USER_3['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    owner_token = _USER_2['token']
    message_id = message_payload['message_id']
    message = valid_messages[2]

    edit = {
        'token': owner_token,
        'message_id': message_id,
        'message': message,
    }
    requests.put(url + '/message/edit', json=edit)

    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert valid_messages[0] not in messages_payload['messages']
    assert valid_messages[2] == messages_payload['messages'][0]['message']
    assert len(messages_payload['messages']) == 1

# Successful case (user is owner of the flockr but not the sender)
def test_server_edit_success_flockr(url, _USER_1, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test a valid message_edit instance, user editing the message is the
    owner of the flockr but not the sender nor channel owner
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    owner_token = _USER_1['token']
    message_id = message_payload['message_id']
    message = valid_messages[2]

    edit = {
        'token': owner_token,
        'message_id': message_id,
        'message': message,
    }
    requests.put(url + '/message/edit', json=edit)

    messages = {
        'token': sender_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert valid_messages[0] not in messages_payload['messages']
    assert valid_messages[2] == messages_payload['messages'][0]['message']
    assert len(messages_payload['messages']) == 1

# Message string passed to edit is empty, so message must be removed
def test_server_edit_empty_message(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test an empty string being passed to edit (message should be removed)
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    sender_token = _USER_2['token']
    message_id = message_payload['message_id']
    message = ''

    edit = {
        'token': sender_token,
        'message_id': message_id,
        'message': message,
    }
    requests.put(url + '/message/edit', json=edit)

    owner_token = _USER_2['token']
    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert not any(valid_messages[0] == msg['message'] for msg in messages_payload['messages'])
    assert len(messages_payload['messages']) == 0

# Non-owner attempting to remove a message they didn't send
def test_server_edit_invalid_user_editing(url, _USER_1, _CHANNEL_pub, _USER_3, valid_messages):
    '''
    Test where the user attempting to edit the message did not originally send
    the message and is not an owner of the flockr nor the channel
    Error code expected: 400
    '''
    sender_token = _USER_1['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    edit_token = _USER_3['token']
    message_id = message_payload['message_id']
    message = valid_messages[2]

    edit = {
        'token': edit_token,
        'message_id': message_id,
        'message': message,
    }
    edit_payload = requests.put(url + '/message/edit', json=edit).json()

    assert edit_payload['code'] == 400
    assert edit_payload['message'] == ('<p>User not authorized</p>')

# Test for invalid message
def test_server_edit_invalid_message(url, _USER_2, _CHANNEL_pub, valid_messages, invalid_message):
    '''
    Test to see if the edited message is valid, that is less than 1000 characters
    Error code expected: 400
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    message_id = message_payload['message_id']
    message = invalid_message

    edit = {
        'token': sender_token,
        'message_id': message_id,
        'message': message,
    }
    edit_payload = requests.put(url + '/message/edit', json=edit).json()

    assert edit_payload['code'] == 400
    assert edit_payload['message'] == ('<p>Message longer than 1000 characters</p>')

################### HTTP TESTS FOR MESSAGE_SENDLATER ###################

# Test succsesful case of message sendlater
def test_server_message_sendlater(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test to check a succsesful case of message sendlater
    Takes in (token, channel_id, message, time_sent)
    Returns message_id
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    curr_time = dt.datetime.now() - timedelta(hours=11)
    timestamp = curr_time.replace(tzinfo=dt.timezone.utc).timestamp()
    send_time = timestamp + 5

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': send_time,
    }
    sendlater_payload = requests.post(url + '/message/sendlater', json=send).json()

    messages = {
        'token': sender_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert messages_payload['messages'][0]['message_id'] == sendlater_payload['message_id']

    query_string = valid_messages[0]

    search = {
        "token": sender_token,
        "query_str": query_string,
    }

    search_payload = requests.get(url + "/search",
                           params=search).json()

    search = {
        "token": sender_token,
        "query_str": query_string,
    }

    search_payload = requests.get(url + "/search",
                           params=search).json()

    assert len(search_payload['messages']) == 1


# Not a valid  channel id
def test_server_message_sendlater_invalid_channel_id(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test for when the channel_id is invalid
    Error code 400
    Expected error message: ADD A MESSAGE HERE
    '''
    sender_token = _USER_2['token']
    message = valid_messages[0]

    curr_time = dt.datetime.now() - timedelta(hours=11)
    timestamp = curr_time.replace(tzinfo=dt.timezone.utc).timestamp()
    send_time = timestamp + 5

    send = {
        'token': sender_token,
        'channel_id': 456,
        'message': message,
        'time_sent': send_time,
    }
    sendlater_payload = requests.post(url + '/message/sendlater', json=send).json()

    assert sendlater_payload['code'] == 400
    assert sendlater_payload['message'] == ('<p>Channel ID is invalid</p>')

# Message is too long
def test_server_message_sendlater_message_too_long(url, _USER_2, _CHANNEL_pub, invalid_message):
    '''
    Test for invalid message, that is message longer than 1000 characters
    Error code 400
    Error message: ADD MESSAGE HERE
    '''
    channel_id = _CHANNEL_pub['channel_id']
    sender_token = _USER_2['token']
    message = invalid_message

    curr_time = dt.datetime.now() - timedelta(hours=11)
    timestamp = curr_time.replace(tzinfo=dt.timezone.utc).timestamp()
    send_time = timestamp + 5

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': send_time,
    }
    sendlater_payload = requests.post(url + '/message/sendlater', json=send).json()

    assert sendlater_payload['code'] == 400
    assert sendlater_payload['message'] == ('<p>Message longer than 1000 characters</p>')

# Time sent is in the past
def test_server_message_sent_time_in_past(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test for a message sent in the past
    Error code 400
    Error message: ADD MESSAGE HERE
    '''
    channel_id = _CHANNEL_pub['channel_id']
    sender_token = _USER_2['token']
    message = valid_messages[0]

    curr_time = dt.datetime.now() - timedelta(hours=11)
    timestamp = curr_time.replace(tzinfo=dt.timezone.utc).timestamp()
    send_time = timestamp - 5

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': send_time,
    }
    sendlater_payload = requests.post(url + '/message/sendlater', json=send).json()

    assert sendlater_payload['code'] == 400
    assert sendlater_payload['message'] == ('<p>Specified time has already passed</p>')

# Authorised user has not joined channel
def test_server_message_sendlater_user_not_channel(url, _USER_2, _CHANNEL_pub, valid_messages, _USER_3):
    '''
    Test for an authoirsed user not in channel
    Error code 400
    Error message: ADD MESSAGE HERE
    '''
    channel_id = _CHANNEL_pub['channel_id']
    sender_token = _USER_3['token']
    message = valid_messages[0]

    curr_time = dt.datetime.now() - timedelta(hours=11)
    timestamp = curr_time.replace(tzinfo=dt.timezone.utc).timestamp()
    send_time = timestamp + 5

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': send_time,
    }
    sendlater_payload = requests.post(url + '/message/sendlater', json=send).json()

    assert sendlater_payload['code'] == 400
    assert sendlater_payload['message'] == ('<p>User not in given channel</p>')

################### HTTP Tests for MESSAGE_PIN ###################
# message_pin(token, message_id)

def test_server_pin_success_flockr_owner(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test valid cases of message_pin
    Authorised user pinning is an owner of the flockr
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    pin = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
    }
    requests.post(url + '/message/pin', json=pin)

    owner_token = _USER_2['token']
    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert messages_payload['messages'][0]['is_pinned'] == True
    assert len(messages_payload['messages']) == 1

    for i in range(1, 5):
        message = valid_messages[i]

        send = {
            'token': sender_token,
            'channel_id': channel_id,
            'message': message,
        }
        message_payload = requests.post(url + '/message/send', json=send).json()

        pin = {
            'token': sender_token,
            'message_id': message_payload['message_id'],
        }
        requests.post(url + '/message/pin', json=pin)

    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert messages_payload['messages'][2]['is_pinned'] == True
    assert len(messages_payload['messages']) == 5

def test_server_pin_success_channel_owner(url, _USER_1, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test valid cases of message_unpin
    Authorised user unpinning is an owner of the channel but not the flockr
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    pin = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
    }
    requests.post(url + '/message/pin', json=pin)

    owner_token = _USER_2['token']
    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert messages_payload['messages'][0]['is_pinned'] == True
    assert len(messages_payload['messages']) == 1

    for i in range(1, 5):
        message = valid_messages[i]

        send = {
            'token': sender_token,
            'channel_id': channel_id,
            'message': message,
        }
        message_payload = requests.post(url + '/message/send', json=send).json()

        pin = {
            'token': sender_token,
            'message_id': message_payload['message_id'],
        }
        requests.post(url + '/message/pin', json=pin)

    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert messages_payload['messages'][2]['is_pinned'] == True
    assert len(messages_payload['messages']) == 5

def test_server_pin_invalid_mid(url, _USER_2):
    '''
    Test a case of passing an invalid message id
    Error code expected: 400
    '''
    sender_token = _USER_2['token']

    pin = {
        'token': sender_token,
        'message_id': 'Fake ID',
    }
    payload = requests.post(url + '/message/pin', json=pin).json()

    assert payload['code'] == 400
    assert payload['message'] == ('<p>Message does not exist</p>')

def test_server_pin_message_already_pinned(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test a case of passing a message that is already pinned
    Error code expected: 400
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    pin = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
    }
    requests.post(url + '/message/pin', json=pin)

    pin = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
    }
    payload = requests.post(url + '/message/pin', json=pin).json()

    assert payload['code'] == 400
    assert payload['message'] == ('<p>Message already pinned</p>')

def test_server_pin_user_not_member(url, _USER_2, _USER_3, _CHANNEL_pub, valid_messages):
    '''
    Test a case of passing a user who is not a member of the channel the
    message is in
    Error code expected: 400
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    non_member_token = _USER_3['token']
    pin = {
        'token': non_member_token,
        'message_id': message_payload['message_id'],
    }
    payload = requests.post(url + '/message/pin', json=pin).json()

    assert payload['code'] == 400
    assert payload['message'] == ('<p>User is not a member of the channel</p>')

def test_server_pin_member_not_owner(url, _USER_2, _USER_3, _CHANNEL_pub, add_to_channel, valid_messages):
    '''
    Test a case of passing a user who is not an owner
    Error code expected: 400
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    non_member_token = _USER_3['token']
    pin = {
        'token': non_member_token,
        'message_id': message_payload['message_id'],
    }
    payload = requests.post(url + '/message/pin', json=pin).json()

    assert payload['code'] == 400
    assert payload['message'] == ('<p>User not authorized</p>')

################### HTTP Tests for MESSAGE_UNPIN ###################
# message_unpin(token, message_id)

def test_unpin_success_flockr_owner(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test valid cases of message_pin
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    pin = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
    }
    requests.post(url + '/message/pin', json=pin)

    unpin = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
    }
    requests.post(url + '/message/unpin', json=unpin)

    owner_token = _USER_2['token']
    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert messages_payload['messages'][0]['is_pinned'] == False
    assert len(messages_payload['messages']) == 1

    for i in range(1, 5):
        message = valid_messages[i]

        send = {
            'token': sender_token,
            'channel_id': channel_id,
            'message': message,
        }
        message_payload = requests.post(url + '/message/send', json=send).json()

        pin = {
            'token': sender_token,
            'message_id': message_payload['message_id'],
        }
        requests.post(url + '/message/pin', json=pin)

        unpin = {
            'token': sender_token,
            'message_id': message_payload['message_id'],
        }

        requests.post(url + '/message/unpin', json=unpin)

    messages = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert messages_payload['messages'][2]['is_pinned'] == False
    assert len(messages_payload['messages']) == 5

def test_unpin_invalid_mid(url, _USER_2):
    '''
    Test a case of passing an invalid message id
    Error code expected: 400
    '''
    sender_token = _USER_2['token']

    unpin = {
        'token': sender_token,
        'message_id': 'Fake ID',
    }
    payload = requests.post(url + '/message/unpin', json=unpin).json()

    assert payload['code'] == 400
    assert payload['message'] == ('<p>Message does not exist</p>')

def test_unpin_message_not_pinned(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test a case of passing a message that is already pinned
    Error code expected: 400
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    pin = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
    }
    requests.post(url + '/message/pin', json=pin)

    unpin = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
    }
    requests.post(url + '/message/unpin', json=unpin)

    unpin = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
    }
    payload = requests.post(url + '/message/unpin', json=unpin).json()

    assert payload['code'] == 400
    assert payload['message'] == ('<p>Message is not pinned</p>')

def test_unpin_user_not_member(url, _USER_2, _USER_3, _CHANNEL_pub, valid_messages):
    '''
    Test a case of passing a user who is not a member of the channel the
    message is in
    Error code expected: 400
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    pin = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
    }
    requests.post(url + '/message/pin', json=pin)

    non_member_token = _USER_3['token']
    unpin = {
        'token': non_member_token,
        'message_id': message_payload['message_id'],
    }
    payload = requests.post(url + '/message/unpin', json=unpin).json()

    assert payload['code'] == 400
    assert payload['message'] == ('<p>User is not a member of the channel</p>')

def test_unpin_member_not_owner(url, _USER_2, _USER_3, _CHANNEL_pub, add_to_channel, valid_messages):
    '''
    Test a case of passing a user who is not an owner
    Error code expected: 400
    '''
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    pin = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
    }
    requests.post(url + '/message/pin', json=pin)

    non_member_token = _USER_3['token']
    unpin = {
        'token': non_member_token,
        'message_id': message_payload['message_id'],
    }
    payload = requests.post(url + '/message/unpin', json=unpin).json()

    assert payload['code'] == 400
    assert payload['message'] == ('<p>User not authorized</p>')

################### HTTP TESTS FOR MESSAGE_REACT ###################

# Test valid case
def test_server_message_react(url, _USER_2, _CHANNEL_pub, _USER_3, valid_messages, add_to_channel):
    '''
    Test a valid case of message react
    Use channel_messages to check
    '''
    # Send message
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    # React to message
    react = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
        'react_id': 1,
    }
    requests.post(url + '/message/react', json=react)

    # React to message
    react = {
        'token': _USER_3['token'],
        'message_id': message_payload['message_id'],
        'react_id': 1,
    }
    requests.post(url + '/message/react', json=react)

    # Use channel_messages to get info on the message
    messages = {
        'token': sender_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert messages_payload['messages'][0]['reacts'][0]['react_id'] == 1
    assert len(messages_payload['messages'][0]['reacts'][0]['u_ids']) == 2
    assert messages_payload['messages'][0]['reacts'][0]['is_this_user_reacted'] == True

# Test for invalid message with user not in channel
def test_server_message_react_invalid_message(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test to check that the message_id is valid. Meaning it belongs to the user in a certain channel.
    Error code expected: 400
    Error message: 'Invalid message_id'
    '''
    # Send message
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    requests.post(url + '/message/send', json=send).json()

    # React to message
    react = {
        'token': sender_token,
        'message_id': 1234,
        'react_id': 1,
    }
    react_payload = requests.post(url + '/message/react', json=react).json()

    assert react_payload['code'] == 400
    assert react_payload['message'] == ('<p>Invalid message_id</p>')

# Test for invalid react_id
def test_server_message_react_reac_id(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test to check that the react_id is valid, meaning it is equal to one.
    Error code expected: 400
    Error message: 'Invalid react id'
    '''
    # Send message
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    # React to message
    react = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
        'react_id': 0,
    }
    react_payload = requests.post(url + '/message/react', json=react).json()

    assert react_payload['code'] == 400
    assert react_payload['message'] == ('<p>Invalid react id</p>')

    # React to message
    react = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
        'react_id': -3,
    }
    react_payload = requests.post(url + '/message/react', json=react).json()

    assert react_payload['code'] == 400
    assert react_payload['message'] == ('<p>Invalid react id</p>')

# Test too see if message already contains a react from user
def test_server_message_react_active_react(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test for message_id to see if it already contains an active react from the authorised user.
    Error code expected: 400
    Error message: 'User already reacted to message'
    '''
    # Send message
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    # React to message
    react = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
        'react_id': 1,
    }
    requests.post(url + '/message/react', json=react)

    # React to message
    react = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
        'react_id': 1,
    }
    react_payload = requests.post(url + '/message/react', json=react).json()

    assert react_payload['code'] == 400
    assert react_payload['message'] == ('<p>User already reacted to message</p>')

################### HTTP TESTS FOR MESSAGE_UNREACT ###################

# Test valid case
def test_server_unreact_success(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test a succsesful case of unreact
    Uses channel_messages to check
    '''
    # Send message
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    # React to message
    react = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
        'react_id': 1,
    }
    requests.post(url + '/message/react', json=react)

    # Unreact to message
    unreact = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
        'react_id': 1,
    }
    requests.post(url + '/message/unreact', json=unreact)

    # Use channel_messages to get info on the message
    messages = {
        'token': sender_token,
        'channel_id': channel_id,
        'start': 0,
    }
    messages_payload = requests.get(url + '/channel/messages', params=messages).json()

    assert messages_payload['messages'][0]['reacts'][0]['react_id'] == 1
    assert len(messages_payload['messages'][0]['reacts'][0]['u_ids']) == 0
    assert messages_payload['messages'][0]['reacts'][0]['is_this_user_reacted'] == False

# Test that message_id is valid within one of the users channels
def test_server_unreact_invalid_message(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test to check that the message_id is valid. Meaning it belongs to the user in a certain channel.
    Error code expected: 400
    Error message: 'Invalid message_id'
    '''
    # Send message
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    # React to message
    react = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
        'react_id': 1,
    }
    requests.post(url + '/message/react', json=react).json()

    # Unreact to message
    unreact = {
        'token': sender_token,
        'message_id': 1234,
        'react_id': 1,
    }
    unreact_payload = requests.post(url + '/message/unreact', json=unreact).json()
    
    assert unreact_payload['code'] == 400
    assert unreact_payload['message'] == ('<p>Invalid message_id</p>')

# Test for invalid react_id
def test_server_message_unreact_reac_id(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test to check that the react_id is valid, meaning it is equal to one.
    Error code expected: 400
    Error message: 'Invalid react id'
    '''
    # Send message
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    # React to message
    react = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
        'react_id': 1,
    }
    requests.post(url + '/message/react', json=react).json()

    # Unreact to message
    unreact = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
        'react_id': 0,
    }
    unreact_payload = requests.post(url + '/message/unreact', json=unreact).json()

    assert unreact_payload['code'] == 400
    assert unreact_payload['message'] == ('<p>Invalid react id</p>')

    # Unreact to message
    unreact = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
        'react_id': -3,
    }
    unreact_payload = requests.post(url + '/message/unreact', json=unreact).json()

    assert unreact_payload['code'] == 400
    assert unreact_payload['message'] == ('<p>Invalid react id</p>')

# Test too see if message_id does not contain an active react
def test_server_message_react_active_unreact(url, _USER_2, _CHANNEL_pub, valid_messages):
    '''
    Test for message_id to see if it does not already contains an active react from the authorised user.
    Error code expected: 400
    Error message: 'User has not reacted to message'
    '''
    # Send message
    sender_token = _USER_2['token']
    channel_id = _CHANNEL_pub['channel_id']
    message = valid_messages[0]

    send = {
        'token': sender_token,
        'channel_id': channel_id,
        'message': message,
    }
    message_payload = requests.post(url + '/message/send', json=send).json()

    # Unreact to message
    unreact = {
        'token': sender_token,
        'message_id': message_payload['message_id'],
        'react_id': 1,
    }
    unreact_payload = requests.post(url + '/message/unreact', json=unreact).json()

    assert unreact_payload['code'] == 400
    assert unreact_payload['message'] == ('<p>User has not reacted to message</p>')
