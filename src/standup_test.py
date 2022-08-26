"""
File for testing standup functions
"""

import pytest
import random
import string
from error import InputError, AccessError
from other import clear
import channel
import channels
import auth
from message import message_send
from standup import standup_start, standup_active, standup_send, u_id_to_handle
from time import sleep

@pytest.fixture
def clear_data():
    """
    Clears the previous data from the flockr
    """
    clear()

@pytest.fixture
def daniel():
    """
    Set up a user called daniel and login to the flockr
    """
    set_up_daniel = auth.auth_register("daniel.steyn@gmail.com", "mypassword3", "Daniel", "Steyn")
    return set_up_daniel

@pytest.fixture
def liam():
    """
    Set up a user called liam and login to the flockr
    """
    set_up_liam = auth.auth_register("liam.treavors@gmail.com", "mypassword1", "Liam", "Treavors")
    set_up_liam = auth.auth_login("liam.treavors@gmail.com", "mypassword1")
    return set_up_liam

@pytest.fixture
def mikkel():
    """
    Set up a user called mikkel and login to the flockr
    """
    set_up_mikkel = auth.auth_register("mikkel@gmail.com", "mypassword2", "Mikkel", "Endresen")
    return set_up_mikkel

@pytest.fixture
def public_channel(liam):
    """
    Set up a public channel with liam as the owner
    """
    set_up_public_channel = channels.channels_create(liam['token'], "public_channel", True)
    return set_up_public_channel

@pytest.fixture
def public_channel_2(liam):
    """
    Set up another public channel with liam as the owner
    """
    set_up_public_channel = channels.channels_create(liam['token'], "public_channel_2", True)
    return set_up_public_channel

@pytest.fixture
def valid_message():
    '''
    A valid message for message_send
    '''
    message = 'Hello! How is it going mate!?'

    return message

@pytest.fixture
def invalid_message():
    '''
    Invalid message for message_send
    1001 characters long to test edge case
    '''
    message = ''.join(random.choice(string.ascii_letters) for _ in range(0, 1001))
    return message


################ STANDUP_ACTIVE Basic Tests ################

def test_standup_active_invalid_token(clear_data, public_channel):
    """
    Test that standup active correctly raises access error with invalid
    token
    """
    with pytest.raises(AccessError):
        standup_active(auth.encode_token('invalid@gmail.com_i'),
                       public_channel['channel_id'])

def test_standup_active_invalid_channel(clear_data, liam):
    """
    Test that standup active correctly raises input error with invalid
    channel id
    """
    with pytest.raises(InputError):
        standup_active(liam['token'], 10)

def test_standup_active_user_not_in_channel(clear_data, liam, mikkel, public_channel):
    """
    Test that standup active correctly raises access error when user
    is not in channel
    """
    with pytest.raises(AccessError):
        standup_active(mikkel['token'], public_channel['channel_id'])

def test_standup_active_never_active(clear_data, liam, public_channel):
    """
    Testing that a channel that has never had a standup correctly
    returns that the standup is inactive
    """
    details = standup_active(liam['token'], public_channel['channel_id'])
    assert details['is_active'] is False
    assert details['time_finish'] is None


################ STANDUP_START Tests ################

def test_standup_start_invalid_token(clear_data, public_channel):
    """
    Test that standup start correctly raises access error with invalid
    token
    """
    with pytest.raises(AccessError):
        standup_start(auth.encode_token('invalid@gmail.com_i'), 
                      public_channel['channel_id'], 5)

def test_standup_start_user_not_in_channel(clear_data, liam, mikkel, public_channel):
    """
    Test that standup start correctly raises access error when user
    is not in channel
    """
    with pytest.raises(AccessError):
        standup_start(mikkel['token'], public_channel['channel_id'], 2)
    
def test_standup_start_invalid_channel(clear_data, liam):
    """
    Test that standup start correctly raises input error with invalid
    channel id
    """
    with pytest.raises(InputError):
        standup_start(liam['token'], 10, 5)

def test_standup_start_invalid_length(clear_data, liam, public_channel):
    """
    Testing that standup_start correctly raises an error if a standup
    is already active
    """

    with pytest.raises(InputError):
        standup_start(liam['token'], public_channel['channel_id'], -3)


def test_standup_start(clear_data, liam, public_channel_2, public_channel):
    """
    Testing that standup_start correctly starts a standup in the desired channel
    """

    standup = standup_start(liam['token'], public_channel['channel_id'], 3)
    assert standup['is_active'] is True

def test_standup_start_already_active(clear_data, liam, public_channel_2, public_channel):
    """
    Testing that standup_start correctly raises an error if a standup
    is already active
    """

    standup_start(liam['token'], public_channel['channel_id'], 3)
    with pytest.raises(InputError):
        standup_start(liam['token'], public_channel['channel_id'], 3)


################ STANDUP_ACTIVE Tests ################

def test_standup_active_is_active(clear_data, liam, public_channel):
    """
    Testing that standup_start correctly starts a standup in the desired channel
    and that standup_active correctly identifies it is active
    """

    standup = standup_start(liam['token'], public_channel['channel_id'], 5)
    assert standup['is_active'] is True

    active = standup_active(liam['token'], public_channel['channel_id'])
    assert active['is_active'] is True
    assert active['time_finish'] is not None

def test_standup_inactive_after_being_active(clear_data, liam, public_channel):
    """
    Testing that standup_start correctly starts a standup in the desired channel
    and that standup_active correctly identifies it is active, and that the standup
    is stopped after the correct amount of time
    """

    standup = standup_start(liam['token'], public_channel['channel_id'], 2)
    assert standup['is_active'] is True

    active = standup_active(liam['token'], public_channel['channel_id'])
    assert active['is_active'] is True
    assert active['time_finish'] is not None

    sleep(3)
    inactive = standup_active(liam['token'], public_channel['channel_id'])
    assert inactive['is_active'] is False
    assert inactive['time_finish'] is None


################ STANDUP_SEND Tests ################

def test_standup_send_invalid_token(clear_data, public_channel):
    """
    Test that standup send correctly raises access error with invalid
    token
    """
    with pytest.raises(AccessError):
        standup_send(auth.encode_token('invalid@gmail.com_i'), 
                     public_channel['channel_id'], "failing")

def test_standup_send_invalid_channel(clear_data, liam):
    """
    Test that standup send correctly raises input error with invalid
    channel id
    """
    with pytest.raises(InputError):
        standup_send(liam['token'], 1000, "failing")


def test_standup_send_user_not_in_channel(clear_data, liam, mikkel, public_channel):
    """
    Test that standup send correctly raises access error when user is not a
    member of the channel
    """
    with pytest.raises(AccessError):
        standup_send(mikkel['token'], public_channel['channel_id'], "failing")

def test_standup_send_invalid_message(clear_data, liam, public_channel, invalid_message):
    """
    Test that standup send correctly raises input error with invalid
    message
    """
    with pytest.raises(InputError):
        standup_send(liam['token'], public_channel['channel_id'], invalid_message)


def test_standup_send_not_active(clear_data, liam, public_channel):
    """
    Test that standup send correctly raises input error when no
    standup is active in the desired channel
    """
    with pytest.raises(InputError):
        standup_send(liam['token'], public_channel['channel_id'], "failing")

def test_standup_send_success(clear_data, liam, public_channel_2, public_channel, valid_message):
    """
    Test that standup send correctly sends a message
    """
    standup_start(liam['token'], public_channel['channel_id'], 3)
    sent = standup_send(liam['token'], public_channel['channel_id'], valid_message)

    assert sent == {}

def test_standup_send_success_message_exists(clear_data, liam, public_channel, valid_message):
    """
    Test that standup send correctly sends a message
    """
    channel_id = public_channel['channel_id']
    standup_start(liam['token'], channel_id, 3)
    standup_send(liam['token'], channel_id, valid_message)

    sleep(4)
    messages = channel.channel_messages(liam['token'], channel_id, 0)
    assert any(valid_message in msg["message"] for msg in messages['messages'])


################ HELPER FUNCTION Tests ################

def test_u_id_to_handle(clear_data, liam, mikkel):
    """
    Testing helper function works
    """
    assert u_id_to_handle(1000) == False

    assert u_id_to_handle(liam['u_id']) == "liamtreavors0"
