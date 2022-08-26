"""
Test file for the channel functions used in flockr.
"""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

import pytest
from error import InputError, AccessError
from other import clear
import channel as ch
import channels
import auth
from message import message_send, message_react

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
    set_up_daniel = auth.auth_login("daniel.steyn@gmail.com", "mypassword3")
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
def private_channel(liam):
    """
    Set up a private channel with liam as the owner
    """
    set_up_private_channel = channels.channels_create(liam['token'], "private_channel", False)
    return set_up_private_channel

@pytest.fixture
def valid_message():
    '''
    A valid message for message_send
    '''
    message = 'Hello! How is it going mate!?'

    return message

################ CHANNEL_DETAILS Tests ################

def test_channel_details_invalid_channel(clear_data, liam):
    """
    Testing channel details with invalid channel input
    """
    with pytest.raises(InputError):
        ch.channel_details(liam['token'], "invalid")

def test_channel_details_invalid_token(clear_data, liam, public_channel):
    """
    Testing channel details with invalid token input
    """
    with pytest.raises(AccessError):
        ch.channel_details(auth.encode_token('invalid@gmail.com_i'), public_channel['channel_id'])

def test_channel_details_valid(clear_data, liam, public_channel):
    """
    Testing channel details with all valid input
    """
    check_channel_details = ch.channel_details(liam['token'], public_channel['channel_id'])
    assert check_channel_details["name"] == "public_channel"
    assert len(check_channel_details["all_members"]) == 1
    assert len(check_channel_details["owner_members"]) == 1
    assert liam['u_id'] == check_channel_details["all_members"][0]['u_id']
    assert liam['u_id'] == check_channel_details["owner_members"][0]['u_id']

################ CHANNEL_INVITE Tests ################

def test_channel_invite_invalid_channel(clear_data, liam, mikkel):
    """
    Testing channel invite with an invalid channel id
    """
    with pytest.raises(InputError):
        ch.channel_invite(liam['token'], "invalid", mikkel['u_id'])

def test_channel_invite_invalid_user(clear_data, liam, mikkel, public_channel):
    """
    Testing channel invite with an invalid user id
    """
    with pytest.raises(InputError):
        ch.channel_invite(liam['token'], public_channel['channel_id'], "invalid")

def test_channel_invite_invalid_token(clear_data, liam, mikkel, daniel, public_channel):
    """
    Testing channel invite with an invalid access token
    """
    with pytest.raises(AccessError):
        ch.channel_invite(daniel['token'], public_channel['channel_id'], mikkel['u_id'])

def test_channel_invite_single(clear_data, liam, mikkel, public_channel):
    """
    Testing channel invite with a single user being invited
    """
    ch.channel_invite(liam['token'], public_channel['channel_id'], mikkel['u_id'])
    check_channel_details = ch.channel_details(liam['token'], public_channel['channel_id'])
    assert len(check_channel_details["all_members"]) == 2
    assert len(check_channel_details["owner_members"]) == 1

def test_channel_invite_multiple(clear_data, liam, mikkel, daniel, public_channel):
    """
    Testing channel invite with two users being invited
    """
    ch.channel_invite(liam['token'], public_channel['channel_id'], mikkel['u_id'])
    ch.channel_invite(liam['token'], public_channel['channel_id'], daniel['u_id'])
    check_channel_details = ch.channel_details(liam['token'], public_channel['channel_id'])
    assert len(check_channel_details['all_members']) == 3
    assert len(check_channel_details["owner_members"]) == 1

################ CHANNEL_MESSAGES Tests ################

def test_channel_messages_invalid_channel(clear_data, liam):
    """
    Testing invalid channel
    """
    with pytest.raises(InputError):
        ch.channel_messages(liam["token"], 9, 2)

def test_channel_messages_simple_messages(clear_data, valid_message, liam, public_channel):
    '''
    Simple success test
    Checks end = -1
    '''
    message_send(liam['token'], public_channel['channel_id'], valid_message)
    messages_data = ch.channel_messages(liam['token'], public_channel['channel_id'], 0)
    assert len(messages_data['messages']) == 1
    assert messages_data['messages'][0]['message'] == valid_message
    assert messages_data['end'] == -1

def test_channel_messages_invalid_start_value(clear_data, liam, public_channel):
    """
    Testing invalid start value for not a number, and number less than zero.
    """
    with pytest.raises(InputError):
        ch.channel_messages(liam["token"], public_channel['channel_id'], -2)
        ch.channel_messages(liam["token"], public_channel['channel_id'], "f")
        ch.channel_messages(liam["token"], public_channel['channel_id'], 2)

def test_channel_messages_invalid_token(clear_data, liam, mikkel, daniel, private_channel):
    """
    Testing raises for invalid token, access error
    """
    with pytest.raises(AccessError):
        ch.channel_messages(mikkel["token"], private_channel['channel_id'], 0)
        ch.channel_messages(daniel["token"], private_channel['channel_id'], 0)

def test_channel_messages_more_than_fifty(clear_data, liam, public_channel, valid_message):
    '''
    60 messages to test start value 9
    '''
    # Following single message should not be among the 50 returned
    message_send(liam['token'], public_channel['channel_id'], 'Nahnah')
    for _ in range(60):
        message_send(liam['token'], public_channel['channel_id'], valid_message)

    messages_data = ch.channel_messages(liam['token'], public_channel['channel_id'], 0)
    assert len(messages_data['messages']) == 50
    assert messages_data['messages'][0]['message'] == valid_message
    assert messages_data['messages'][49]['message'] == valid_message
    assert 'Nahnah' not in messages_data['messages']

def test_channel_messages_less_than_fifty(clear_data, liam, public_channel, valid_message):
    '''
    Test for a full 50 messages, one different message to see order
    '''
    for _ in range(49):
        message_send(liam['token'], public_channel['channel_id'], valid_message)

    message_send(liam['token'], public_channel['channel_id'], 'Hey!')
    messages_data = ch.channel_messages(liam['token'], public_channel['channel_id'], 0)
    assert len(messages_data['messages']) == 50
    assert messages_data['messages'][49]['message'] == valid_message
    assert messages_data['messages'][0]['message'] == 'Hey!'
    assert not messages_data['messages'][0]['reacts'][0]['is_this_user_reacted']

def test_channel_messages_react_true(clear_data, liam, public_channel, valid_message):
    '''
    Test to see if the is this_user_reacted attribute and helper function works
    '''
    message = message_send(liam['token'], public_channel['channel_id'], 'Hey!')
    message_react(liam['token'], message['message_id'], 1)
    messages_data = ch.channel_messages(liam['token'], public_channel['channel_id'], 0)
    assert messages_data['messages'][0]['reacts'][0]['is_this_user_reacted']

################ CHANNEL_LEAVE Tests ################

def test_channel_leave_invalid_channel(clear_data, liam):
    '''
    Test input eror when passing an invalid channel ID
    '''
    with pytest.raises(InputError):
        ch.channel_leave(liam["token"], "fake_channel")

def test_channel_leave_access_error(clear_data, daniel, public_channel):
    '''
    Test access error when attempting to leave a channel the authorised user
    is not a member of.
    '''
    with pytest.raises(AccessError):
        ch.channel_leave(daniel["token"], public_channel['channel_id'])

def test_channel_leave_success(clear_data, liam, public_channel):
    '''
    Test a valid channel leave instance.
    '''
    ch.channel_leave(liam["token"], public_channel['channel_id'])
    all_channels = channels.channels_list(liam["token"])

    assert not public_channel in all_channels['channels']

################ CHANNEL_JOIN Tests ################

def test_channel_join_invalid_channel(clear_data, liam):
    """
    Test input error when invalid channel ID is passed.
    """
    with pytest.raises(InputError):
        ch.channel_join(liam["token"], "fake_channel")

def test_channel_join_private_channel(clear_data, liam, daniel, private_channel):
    '''
    Test access error when channel is private
    '''
    with pytest.raises(AccessError):
        ch.channel_join(daniel["token"], private_channel['channel_id'])

def test_channel_join_success(clear_data, liam, daniel, public_channel):
    '''
    Test a valid channel_join instance.
    '''
    daniel = auth.auth_login("daniel.steyn@gmail.com", "mypassword3")
    ch.channel_join(daniel["token"], public_channel['channel_id'])

    check_channel_details = ch.channel_details(daniel['token'], public_channel['channel_id'])
    assert len(check_channel_details['all_members']) == 2
    assert daniel['u_id'] == check_channel_details['all_members'][1]['u_id']

################ CHANNEL_ADDOWNER Tests ################

def test_channel_addowner_invalid_id(clear_data, liam, public_channel):
    '''
    Test an input error when the user ID passed is invalid.
    '''
    with pytest.raises(InputError):
        ch.channel_addowner(liam["token"], public_channel['channel_id'], "bad id")

def test_channel_addowner_invalid_channel(clear_data, liam, daniel):
    '''
    Test an input error when the channel ID passed is invalid.
    '''
    with pytest.raises(InputError):
        ch.channel_addowner(liam["token"], "fake channel", daniel["u_id"])

def test_channel_addowner_access_error(clear_data, public_channel, liam, daniel, mikkel):
    '''
    Test an access error when the authorised user is not an owner of the
    channel nor a global owner.
    '''
    with pytest.raises(AccessError):
        ch.channel_addowner(daniel["token"], public_channel['channel_id'], mikkel["u_id"])

def test_channel_addowner_user_already_owner(clear_data, liam, public_channel):
    '''
    Test an access error when the u_id belongs to a user who is already an
    owner of the channel
    '''
    with pytest.raises(InputError):
        ch.channel_addowner(liam["token"], public_channel['channel_id'], liam["u_id"])

def test_channel_addowner_success(clear_data, liam, mikkel, public_channel):
    '''
    Test a valid instance of add owner.
    '''
    ch.channel_addowner(liam["token"], public_channel['channel_id'], mikkel["u_id"])
    pubchannel_details = ch.channel_details(liam["token"], public_channel['channel_id'])

    assert mikkel["u_id"] == pubchannel_details["owner_members"][1]['u_id']

################ CHANNEL_REMOVEOWNER Tests ################

def test_channel_removeowner_invalid_channel(clear_data, liam):
    """
    Testing invalid channel, input error
    """
    with pytest.raises(InputError):
        ch.channel_removeowner(liam["token"], 9, liam["u_id"])

def test_channel_removeowner_invalid_owner(clear_data, liam, mikkel, private_channel):
    """
    Testing invalid owner, input error
    """
    with pytest.raises(AccessError):
        ch.channel_removeowner(mikkel["token"], private_channel['channel_id'], liam["u_id"])


def test_channel_removeowner_invalid_token(clear_data, liam, public_channel, mikkel):
    """
    Testing that the token holder is authorized, access error
    """
    with pytest.raises(AccessError):
        ch.channel_removeowner(mikkel["token"], public_channel['channel_id'], liam["u_id"])

def test_channel_removeowner_success_flockr_owner(clear_data, daniel, liam, mikkel, public_channel):
    '''
    Testing that flockr owner is authorized to remove owner
    Daniel is the flockr owner
    '''
    ch.channel_addowner(daniel["token"], public_channel['channel_id'], mikkel["u_id"])
    details = ch.channel_details(liam["token"], public_channel['channel_id'])
    assert len(details['owner_members']) == 2
    ch.channel_removeowner(daniel["token"], public_channel['channel_id'], mikkel["u_id"])
    details = ch.channel_details(liam["token"], public_channel['channel_id'])
    assert len(details['owner_members']) == 1
    assert details['owner_members'][0]['u_id'] == liam['u_id']

def test_channel_removeowner_success(clear_data, liam, mikkel, public_channel, private_channel):
    """
    Tests to check that the function removes given u_id.
    Everything given is valid, no exceptions should be raised.
    Liam is the owner of the channel and is therefore authorized
    """
    ch.channel_addowner(liam["token"], public_channel['channel_id'], mikkel["u_id"])
    details = ch.channel_details(liam["token"], public_channel['channel_id'])
    assert len(details['owner_members']) == 2
    ch.channel_removeowner(liam["token"], public_channel['channel_id'], mikkel["u_id"])
    details = ch.channel_details(liam["token"], public_channel['channel_id'])
    assert len(details['owner_members']) == 1
    assert details['owner_members'][0]['u_id'] == liam['u_id']
