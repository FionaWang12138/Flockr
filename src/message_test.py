'''
Test file for message.py
'''

# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

import string
import random
import pytest
import datetime as dt
from datetime import datetime
from datetime import timedelta
import time
from message import message_send, message_remove, message_edit, message_pin, message_unpin, message_sendlater, message_react, message_unreact
from channel import channel_join
from error import InputError, AccessError
from other import clear
from channel import channel_messages, channel_invite
import channels
import auth

################### Pytest Fixtures ###################

@pytest.fixture
def clear_data():
    '''
    Clears the previous data from the flockr
    '''
    clear()

@pytest.fixture
def daniel():
    '''
    Set up a user called daniel and login to the flockr
    '''
    set_up_daniel = auth.auth_register("daniel.steyn@gmail.com", "mypassword3", "Daniel", "Steyn")
    return set_up_daniel

@pytest.fixture
def liam():
    '''
    Set up a user called liam and login to the flockr
    '''
    set_up_liam = auth.auth_register("liam.treavors@gmail.com", "mypassword1", "Liam", "Treavors")
    set_up_liam = auth.auth_login("liam.treavors@gmail.com", "mypassword1")
    return set_up_liam

@pytest.fixture
def mikkel():
    '''
    Set up a user called mikkel and login to the flockr
    '''
    set_up_mikkel = auth.auth_register("mikkel@gmail.com", "mypassword2", "Mikkel", "Endresen")
    return set_up_mikkel

@pytest.fixture
def public_channel(liam):
    '''
    Set up a public channel with liam as the owner
    '''
    set_up_public_channel = channels.channels_create(liam['token'], "public_channel", True)
    return set_up_public_channel

@pytest.fixture
def private_channel(liam):
    '''
    Set up a private channel with daniel as the owner
    '''
    set_up_private_channel = channels.channels_create(liam['token'], "private_channel", False)
    return set_up_private_channel

@pytest.fixture
def daniel_channel(daniel):
    '''
    Logs Daniel in and creates a public channel with Daniel as the owner
    This is used to test cases where the authorised user is a channel owner but not
    the flockr owner
    '''
    auth.auth_login("daniel.steyn@gmail.com", "mypassword3")

    set_up_daniel_channel = channels.channels_create(daniel['token'], "daniel_channel", True)
    return set_up_daniel_channel

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

################### MESSAGE_SEND Tests ###################
# message_send(token, channel_id, message)

# Successful case
def test_send_success(clear_data, liam, public_channel, private_channel, valid_messages):
    '''
    Test valid message_send instances
    '''
    message_send(liam['token'], public_channel['channel_id'], valid_messages[0])

    message_check = channel_messages(liam['token'], public_channel['channel_id'], 0)

    assert len(message_check['messages']) == 1
    assert message_check['messages'][0]['message'] == valid_messages[0]

    for i in range(1, 5):
        message_send(liam['token'], public_channel['channel_id'], valid_messages[i])

    message_check = channel_messages(liam['token'], public_channel['channel_id'], 0)
    assert len(message_check['messages']) == 5
    # Pick a random message to see that its right
    assert message_check['messages'][2]['message'] == valid_messages[2]

# Non-member attempting to send message
def test_send_non_member(clear_data, liam, public_channel, daniel, valid_messages):
    '''
    Test where the user sending the message is not a member of the channel
    Error expected: access error
    '''
    # user Daniel is not a member of either channel
    # Non-members cannot send messages to public nor private channels
    with pytest.raises(AccessError):
        message_send(daniel['token'], private_channel, valid_messages[0])
        message_send(daniel['token'], public_channel, valid_messages[1])

# Message length equal to 999
def test_send_message_length_999(clear_data, liam, public_channel):
    '''
    Test edge case for length of message.
    '''
    # Message length == 999

    channel_id = public_channel['channel_id']
    body = ''.join(random.choice(string.ascii_letters) for _ in range(999))
    message_send(liam['token'], channel_id, body)
    message_check = channel_messages(liam['token'], channel_id, 0)
    assert len(message_check['messages']) == 1
    assert message_check['messages'][0]['message'] == body

# Message length equal to 1000
def test_send_message_length_1000(clear_data, liam, public_channel):
    '''
    Test edge case for length of message.
    '''
    # Message length == 1000
    channel_id = public_channel['channel_id']
    body = ''.join(random.choice(string.ascii_letters) for _ in range(1000))
    message_send(liam['token'], channel_id, body)
    message_check = channel_messages(liam['token'], channel_id, 0)
    assert len(message_check['messages']) == 1
    assert message_check['messages'][0]['message'] == body

def test_send_message_too_long(clear_data, liam, public_channel, valid_messages):
    '''
    Test for a message too long
    Expects input error
    '''
    # Succsessful message_send
    channel_id = public_channel['channel_id']
    message_send(liam['token'], channel_id, valid_messages[0])

    # Message length == 1001
    body = ''.join(random.choice(string.ascii_letters) for _ in range(1001))
    with pytest.raises(InputError):
        message_send(liam['token'], channel_id, body)

    # the message above shouldn't have sent, so the channel's messages should be
    # unchanged
    message_check = channel_messages(liam['token'], channel_id, 0)
    assert len(message_check['messages']) == 1
    assert message_check['messages'][0]['message'] == valid_messages[0]

# Check that message_send generates a new id for each message
def test_send_message_new_id(clear_data, liam, public_channel, valid_messages):
    '''
    Test to check that message_send creates a different id for each message
    '''
    channel_id = public_channel['channel_id']
    first_message_id = message_send(liam['token'], channel_id, valid_messages[0])
    second_message_id = message_send(liam['token'], channel_id, valid_messages[1])
    assert first_message_id['message_id'] is not second_message_id['message_id']

################### MESSAGE_REMOVE Tests ###################
# message_remove(token, message_id)

# Successful case (user sent the message)
def test_remove_success_sender(clear_data, liam, public_channel, mikkel, valid_messages):
    '''
    Test a valid message_remove instance, user removing the message is the
    original sender
    '''
    channel_id = public_channel['channel_id']
    channel_invite(liam['token'], channel_id, mikkel['u_id'])
    message_id = message_send(mikkel['token'], channel_id, valid_messages[0])
    message_remove(mikkel['token'], message_id['message_id'])
    assert valid_messages[0] not in channel_messages(liam['token'], channel_id, 0)['messages']

# Successful case (user is owner of the channel but not the sender)
def test_remove_success_owner(clear_data, liam, public_channel, mikkel, valid_messages):
    '''
    Test a valid message_remove instance, user removing the message is the
    channel owner, but not the sender
    '''
    channel_id = public_channel['channel_id']
    channel_invite(liam['token'], channel_id, mikkel['u_id'])
    message_id = message_send(mikkel['token'], channel_id, valid_messages[0])
    message_remove(liam['token'], message_id['message_id'])
    assert valid_messages[0] not in channel_messages(liam['token'], channel_id, 0)['messages']

# Successful case (user is owner of the flockr but not the sender)
def test_remove_success_flockr(clear_data, daniel, liam, private_channel, valid_messages):
    '''
    Test a valid message_remove instance, user removing the message is the
    flockr owner, but not the sender nor the channel owner
    '''
    channel_id = private_channel['channel_id']
    message_id = message_send(liam['token'], channel_id, valid_messages[0])
    message_remove(daniel['token'], message_id['message_id'])
    assert valid_messages[0] not in channel_messages(liam['token'], channel_id, 0)['messages']

# Non-owner attempting to remove a message they didn't send
def test_remove_invalid_user_removing(clear_data, liam, public_channel, mikkel, valid_messages):
    '''
    Test where the user attempting to remove the message did not originally send
    the message and is not an owner of the flockr nor the channel
    Error expected: access error
    '''
    channel_id = public_channel['channel_id']
    message_id = message_send(liam['token'], channel_id, valid_messages[0])
    with pytest.raises(AccessError):
        message_remove(mikkel['token'], message_id['message_id'])

# Message (based on ID) no longer exists
def test_remove_invalid_message_id(clear_data, liam, public_channel, mikkel, valid_messages):
    '''
    Test where the message (based on ID) no longer exists
    Error expected: input error
    '''
    message_id = message_send(liam['token'], public_channel['channel_id'], valid_messages[0])
    message_remove(liam['token'], message_id['message_id'])
    with pytest.raises(InputError):
        message_remove(liam['token'], message_id['message_id'])

################### MESSAGE_EDIT Tests ###################
# message_edit(token, message_id, message)

# Successful case (user sent the message)
def test_edit_success_sender(clear_data, liam, public_channel, mikkel, valid_messages):
    '''
    Test a valid message_edit instance, user editing the message is the
    original sender
    '''
    channel_id = public_channel['channel_id']
    channel_invite(liam['token'], channel_id, mikkel['u_id'])
    message_id = message_send(mikkel['token'], channel_id, valid_messages[0])
    message_edit(mikkel['token'], message_id['message_id'], valid_messages[1])
    messages = channel_messages(mikkel['token'], channel_id, 0)
    assert valid_messages[1] == messages['messages'][0]['message']

# Successful case (user is owner of the channel but not the sender)
def test_edit_success_owner(clear_data, liam, public_channel, mikkel, valid_messages):
    '''
    Test a valid message_edit instance, user editing the message is the
    owner of the channel but not the sender
    '''
    channel_id = public_channel['channel_id']
    channel_invite(liam['token'], channel_id, mikkel['u_id'])
    message_id = message_send(mikkel['token'], channel_id, valid_messages[0])
    message_edit(liam['token'], message_id['message_id'], valid_messages[1])
    messages = channel_messages(liam['token'], channel_id, 0)
    assert valid_messages[1] == messages['messages'][0]['message']

# Successful case (user is owner of the flockr but not the sender)
def test_edit_success_flockr(clear_data, daniel, public_channel, liam, valid_messages):
    '''
    Test a valid message_edit instance, user editing the message is the
    owner of the flockr but not the sender nor channel owner
    '''
    channel_id = public_channel['channel_id']
    message_id = message_send(liam['token'], channel_id, valid_messages[0])
    message_edit(daniel['token'], message_id['message_id'], valid_messages[1])
    messages = channel_messages(liam['token'], channel_id, 0)
    assert valid_messages[1] == messages['messages'][0]['message']

# Non-owner attempting to remove a message they didn't send
def test_edit_invalid_user_editing(clear_data, liam, public_channel, mikkel, valid_messages):
    '''
    Test where the user attempting to edit the message did not originally send
    the message and is not an owner of the flockr nor the channel
    Error expected: access error
    '''
    channel_id = public_channel['channel_id']
    message_id = message_send(liam['token'], channel_id, valid_messages[0])
    with pytest.raises(AccessError):
        message_edit(mikkel['token'], message_id['message_id'], valid_messages[1])

# Test for invalid message
def test_edit_invalid_message(clear_data, liam, public_channel, valid_messages, invalid_message):
    '''
    Test to see if the edited message is valid, that is less than 1000 characters
    '''
    channel_id = public_channel['channel_id']
    message_id = message_send(liam['token'], channel_id, valid_messages[0])
    with pytest.raises(InputError):
        message_edit(liam['token'], message_id['message_id'], invalid_message)

################### MESSAGE_SENDLATER Tests ###################
# message_sendlater(token, channel_id, message, time_sent)

def test_sendlater_success(clear_data, liam, public_channel, valid_messages):
    '''
    Test a successful case of sendlater
    '''
    
    curr_time = dt.datetime.now() - timedelta(hours=11)
    timestamp = curr_time.replace(tzinfo=dt.timezone.utc).timestamp()
    send_time = timestamp + 1
    
    sender_token = liam['token']
    channel_id = public_channel['channel_id']
    message = valid_messages[0]

    sendlater = message_sendlater(sender_token, channel_id, message, send_time)
    message_check = channel_messages(liam['token'], channel_id, 0)
    assert valid_messages[0] == message_check['messages'][0]['message']
    assert sendlater['message_id'] == message_check['messages'][0]['message_id']


def test_sendlater_invalid_channel(clear_data, liam, valid_messages):
    '''
    Test a case of passing an invalid channel_id
    Error expected: input error
    '''
    curr_time = dt.datetime.now() - timedelta(hours=11)
    timestamp = curr_time.replace(tzinfo=dt.timezone.utc).timestamp()
    send_time = timestamp + 1

    sender_token = liam['token']
    message = valid_messages[0]

    with pytest.raises(InputError):
        message_sendlater(sender_token, 'Fake Channel', message, send_time)


def test_sendlater_invalid_message(clear_data, liam, public_channel, invalid_message):
    '''
    Test a case of passing an invalid message
    Error expected: input error
    '''
    curr_time = dt.datetime.now() - timedelta(hours=11)
    timestamp = curr_time.replace(tzinfo=dt.timezone.utc).timestamp()
    send_time = timestamp + 5

    sender_token = liam['token']
    channel_id = public_channel['channel_id']
    message = invalid_message

    with pytest.raises(InputError):
        message_sendlater(sender_token, channel_id, message, send_time)

def test_sendlater_time_sent_in_past(clear_data, liam, public_channel, valid_messages):
    '''
    Test a case of passing an invalid time (a time that has already passed)
    Error expected: input error
    '''
    curr_time = dt.datetime.now() - timedelta(hours=11)
    timestamp = curr_time.replace(tzinfo=dt.timezone.utc).timestamp()
    send_time = int(timestamp - 60)

    sender_token = liam['token']
    channel_id = public_channel['channel_id']
    message = valid_messages[0]

    with pytest.raises(InputError):
        message_sendlater(sender_token, channel_id, message, send_time)

def test_sendlater_non_member(clear_data, liam, mikkel, public_channel, valid_messages):
    '''
    Test a case of a non member attempting to send a message in a channel
    Error expected: access error
    '''
    curr_time = dt.datetime.now() - timedelta(hours=11)
    timestamp = curr_time.replace(tzinfo=dt.timezone.utc).timestamp()
    send_time = timestamp + 5

    sender_token = mikkel['token']
    channel_id = public_channel['channel_id']
    message = valid_messages[0]

    with pytest.raises(AccessError):
        message_sendlater(sender_token, channel_id, message, send_time)

################### MESSAGE_PIN Tests ###################
# message_pin(token, message_id)

def test_pin_success_flockr_owner(clear_data, liam, public_channel, valid_messages):
    '''
    Test valid cases of message_pin
    Authorised user pinning is an owner of the flockr
    '''
    channel_id = public_channel['channel_id']
    message_id = message_send(liam['token'], channel_id, valid_messages[0])
    message_pin(liam['token'], message_id['message_id'])
    message_check = channel_messages(liam['token'], channel_id, 0)

    assert len(message_check['messages']) == 1
    assert message_check['messages'][0]['is_pinned']

    for i in range(1, 5):
        message_id = message_send(liam['token'], channel_id, valid_messages[i])
        message_pin(liam['token'], message_id['message_id'])

    message_check = channel_messages(liam['token'], channel_id, 0)
    assert len(message_check['messages']) == 5
    # Pick a random message to see that its right
    assert message_check['messages'][2]['is_pinned']

def test_pin_success_channel_owner(clear_data, liam, daniel, daniel_channel, valid_messages):
    '''
    Test valid cases of message_pin
    Authorised user pinning is an owner of the channel but not the flockr
    '''
    channel_id = daniel_channel['channel_id']
    message_id = message_send(daniel['token'], channel_id, valid_messages[0])
    message_pin(daniel['token'], message_id['message_id'])
    message_check = channel_messages(daniel['token'], channel_id, 0)

    assert len(message_check['messages']) == 1
    assert message_check['messages'][0]['is_pinned']

    for i in range(1, 5):
        message_id = message_send(daniel['token'], channel_id, valid_messages[i])
        message_pin(daniel['token'], message_id['message_id'])

    message_check = channel_messages(daniel['token'], channel_id, 0)
    assert len(message_check['messages']) == 5
    # Pick a random message to see that its right
    assert message_check['messages'][2]['is_pinned']

def test_pin_invalid_mid(clear_data, liam):
    '''
    Test a case of passing an invalid message id
    Error expected: input error
    '''
    with pytest.raises(InputError):
        message_pin(liam['token'], 'Fake ID')

def test_pin_message_already_pinned(clear_data, liam, public_channel, valid_messages):
    '''
    Test a case of passing a message that is already pinned
    Error expected: input error
    '''
    channel_id = public_channel['channel_id']
    message_id = message_send(liam['token'], channel_id, valid_messages[0])
    message_pin(liam['token'], message_id['message_id'])

    with pytest.raises(InputError):
        message_pin(liam['token'], message_id['message_id'])

def test_pin_user_non_member(clear_data, liam, daniel, public_channel, valid_messages):
    '''
    Test a case of passing a user who is not a member of the channel the
    message is in
    Error expected: access error
    '''
    channel_id = public_channel['channel_id']
    message_id = message_send(liam['token'], channel_id, valid_messages[0])

    with pytest.raises(AccessError):
        message_pin(daniel['token'], message_id['message_id'])

def test_pin_user_member_but_not_owner(clear_data, liam, daniel, public_channel, valid_messages):
    '''
    Test a case of passing a user who is not an owner
    Error expected: access error
    '''
    channel_id = public_channel['channel_id']

    # Add Daniel to a channel he is not an owner of
    channel_join(daniel['token'], channel_id)

    message_id = message_send(liam['token'], channel_id, valid_messages[0])

    with pytest.raises(AccessError):
        message_pin(daniel['token'], message_id['message_id'])

################### MESSAGE_UNPIN Tests ###################
# message_unpin(token, message_id)

def test_unpin_success_flockr_owner(clear_data, liam, public_channel, valid_messages):
    '''
    Test valid cases of message_pin
    Authorised user pinning is an owner of the flockr
    '''
    channel_id = public_channel['channel_id']
    message_id = message_send(liam['token'], channel_id, valid_messages[0])
    message_pin(liam['token'], message_id['message_id'])
    message_unpin(liam['token'], message_id['message_id'])
    message_check = channel_messages(liam['token'], channel_id, 0)

    assert len(message_check['messages']) == 1
    assert message_check['messages'][0]['is_pinned'] == False

    for i in range(1, 5):
        message_id = message_send(liam['token'], channel_id, valid_messages[i])
        message_pin(liam['token'], message_id['message_id'])
        message_unpin(liam['token'], message_id['message_id'])

    message_check = channel_messages(liam['token'], channel_id, 0)
    assert len(message_check['messages']) == 5
    # Pick a random message to see that it's unpinned
    assert message_check['messages'][2]['is_pinned'] == False

def test_unpin_success_channel_owner(clear_data, liam, daniel, daniel_channel, valid_messages):
    '''
    Test valid cases of message_unpin
    Authorised user unpinning is an owner of the channel but not the flockr
    '''
    channel_id = daniel_channel['channel_id']
    message_id = message_send(daniel['token'], channel_id, valid_messages[0])
    message_pin(daniel['token'], message_id['message_id'])
    message_unpin(daniel['token'], message_id['message_id'])
    message_check = channel_messages(daniel['token'], channel_id, 0)

    assert len(message_check['messages']) == 1
    assert message_check['messages'][0]['is_pinned'] == False

    for i in range(1, 5):
        message_id = message_send(daniel['token'], channel_id, valid_messages[i])
        message_pin(daniel['token'], message_id['message_id'])
        message_unpin(daniel['token'], message_id['message_id'])

    message_check = channel_messages(daniel['token'], channel_id, 0)
    assert len(message_check['messages']) == 5
    # Pick a random message to see that its right
    assert message_check['messages'][2]['is_pinned'] == False

def test_unpin_invalid_mid(clear_data, liam):
    '''
    Test a case of passing an invalid message id
    Error expected: input error
    '''
    with pytest.raises(InputError):
        message_unpin(liam['token'], 'Fake ID')

def test_unpin_message_not_pinned(clear_data, liam, public_channel, valid_messages):
    '''
    Test a case of passing a message that is not pinned
    Error expected: input error
    '''
    channel_id = public_channel['channel_id']
    message_id = message_send(liam['token'], channel_id, valid_messages[0])

    with pytest.raises(InputError):
        message_unpin(liam['token'], message_id['message_id'])

def test_unpin_user_non_member(clear_data, liam, daniel, public_channel, valid_messages):
    '''
    Test a case of passing a user who is not a member of the channel the
    message is in
    Error expected: access error
    '''
    channel_id = public_channel['channel_id']
    message_id = message_send(liam['token'], channel_id, valid_messages[0])
    message_pin(liam['token'], message_id['message_id'])

    with pytest.raises(AccessError):
        message_unpin(daniel['token'], message_id['message_id'])

def test_unpin_user_member_but_not_owner(clear_data, liam, daniel, public_channel, valid_messages):
    '''
    Test a case of passing a user who is not an owner
    Error expected: access error
    '''
    channel_id = public_channel['channel_id']

    # Add Daniel to a channel he is not an owner of
    channel_join(daniel['token'], channel_id)

    message_id = message_send(liam['token'], channel_id, valid_messages[0])
    message_pin(liam['token'], message_id['message_id'])

    with pytest.raises(AccessError):
        message_unpin(daniel['token'], message_id['message_id'])

################### MESSAGE_REACT Tests ###################
# message_react(token, message_id, react_id)

# Test that message_id is valid within one of the users channels
def test_message_react_valid_message_id(clear_data, liam, public_channel, valid_messages):
    '''
    Test to check that the message_id is valid. Meaning it belongs to the user in a certain channel.
    Input Error
    '''
    message_send(liam['token'], public_channel['channel_id'], valid_messages[0])
    with pytest.raises(InputError):
        message_react(liam['token'], 234, 1)

    messages_data = channel_messages(liam['token'], public_channel['channel_id'], 0)
    assert not messages_data['messages'][0]['reacts'][0]['is_this_user_reacted']

# Test for invalid react_id
def test_message_react_react_id(clear_data, liam, public_channel, valid_messages):
    '''
    Test to check that the react_id is valid, meaning it is equal to one.
    Input Error
    '''
    message = message_send(liam['token'], public_channel['channel_id'], valid_messages[0])
    with pytest.raises(InputError):
        message_react(liam['token'], message['message_id'], 0)
        message_react(liam['token'], message['message_id'], 3)
        message_react(liam['token'], message['message_id'], -1)

    messages_data = channel_messages(liam['token'], public_channel['channel_id'], 0)
    assert not messages_data['messages'][0]['reacts'][0]['is_this_user_reacted']

# Test too see if message already contains a react from user
def test_message_react_already_react(clear_data, liam, public_channel, valid_messages):
    '''
    Test for message_id to see if it already contains an active react from the authorised user.
    Input Error
    '''
    message = message_send(liam['token'], public_channel['channel_id'], valid_messages[0])
    message_react(liam['token'], message['message_id'], 1)
    with pytest.raises(InputError):
        message_react(liam['token'], message['message_id'], 1)


# Check for a valid case
def test_message_react_valid_case(clear_data, liam, public_channel, valid_messages, mikkel):
    '''
    Test a valid case
    Should leave the react key in message equal to one
    '''
    channel_invite(liam['token'], public_channel['channel_id'], mikkel['u_id'])
    message_id = message_send(liam['token'], public_channel['channel_id'], valid_messages[0])
    message_react(liam['token'], message_id['message_id'], 1)
    message_react(mikkel['token'], message_id['message_id'], 1)
    messages_data = channel_messages(liam['token'], public_channel['channel_id'], 0)

    assert messages_data['messages'][0]['reacts'][0]['react_id'] == 1
    assert len(messages_data['messages'][0]['reacts'][0]['u_ids']) == 2


################### MESSAGE_UNREACT Tests ###################
# message_unreact(token, message_id, react_id)

# Test that message_id is valid within one of the users channels
def test_message_unreact_invalid_message(clear_data, liam, public_channel, mikkel, valid_messages):
    '''
    Test to check that the message_id is valid. Meaning it belongs to the user in a certain channel.
    Input Error
    '''
    channel_invite(liam['token'], public_channel['channel_id'], mikkel['u_id'])
    message = message_send(liam['token'], public_channel['channel_id'], valid_messages[0])
    message_react(liam['token'], message['message_id'], 1)
    with pytest.raises(InputError):
        message_unreact(mikkel['token'], message['message_id'], 1)

    messages_data = channel_messages(liam['token'], public_channel['channel_id'], 0)
    assert messages_data['messages'][0]['reacts'][0]['react_id'] == 1

# React_id is not a valid React ID
def test_message_unreact_invalid_react_id(clear_data, liam, public_channel, valid_messages):
    '''
    Test to check that the react_id is valid, meaning it is equal to zero.
    Input Error
    '''
    message = message_send(liam['token'], public_channel['channel_id'], valid_messages[0])
    message_react(liam['token'], message['message_id'], 1)
    with pytest.raises(InputError):
        message_unreact(liam['token'], message['message_id'], 3)
        message_unreact(liam['token'], message['message_id'], -1)

    messages_data = channel_messages(liam['token'], public_channel['channel_id'], 0)
    assert messages_data['messages'][0]['reacts'][0]['react_id'] == 1

# Test too see if message_id does not contain an active react
def test_message_unreact_active_react(clear_data, liam, public_channel, valid_messages):
    '''
    Test for message_id to see if it does not contain an active react from the authorised user.
    Input Error
    '''
    message = message_send(liam['token'], public_channel['channel_id'], valid_messages[0])
    with pytest.raises(InputError):
        message_unreact(liam['token'], message['message_id'], 0)

# Test valid case
def test_message_unreact_valid_case(clear_data, liam, public_channel, valid_messages):
    '''
    Test a valid case
    '''
    message = message_send(liam['token'], public_channel['channel_id'], valid_messages[0])
    message_react(liam['token'], message['message_id'], 1)
    messages_data = channel_messages(liam['token'], public_channel['channel_id'], 0)
    assert liam['u_id'] in messages_data['messages'][0]['reacts'][0]['u_ids']
    message_unreact(liam['token'], message['message_id'], 1)
    messages_data = channel_messages(liam['token'], public_channel['channel_id'], 0)

    assert messages_data['messages'][0]['reacts'][0]['react_id'] == 1
    assert liam['u_id'] not in messages_data['messages'][0]['reacts'][0]['u_ids']
