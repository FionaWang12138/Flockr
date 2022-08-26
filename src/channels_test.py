""" TESTS FOR CHANNELS.PY """

import pytest
from error import InputError, AccessError
from channels import channels_list, channels_listall, channels_create, check_token
from channel import channel_join, channel_leave
from auth import auth_register, auth_login, encode_token, decode_token
from other import clear

##################### FIXTURES FOR CREATING USERS ########################
@pytest.fixture
def _token_1():
    """
    Registers and logs in a user returning a token.

    Returns:
        string: token
    """
    clear()
    auth_register('test@gmail.com', 'password', 'Oliver', 'Xu')
    token = auth_login('test@gmail.com', 'password')['token']
    return token

@pytest.fixture
def _token_2():
    """
    Registers and logs in an another user returning a token.

    Returns:
        string: token
    """
    auth_register('hello@gmail.com', '12345678', 'John', 'Smith')
    token = auth_login('hello@gmail.com', '12345678')['token']
    return token

@pytest.fixture
def _token_3():
    """
    Registers and logs in an another user returning a token.

    Returns:
        string: token
    """
    auth_register('mango@gmail.com', 'iliketrains', 'Monty', 'Python')
    token = auth_login('mango@gmail.com', 'iliketrains')['token']
    return token


###################### TESTS FOR channels_list ###########################

def test_list_empty(_token_1):
    """
    Test that a user who is part of NO channels returns an empty list.
    """
    assert channels_list(_token_1) == {'channels': []}
    clear()

def test_list_spec(_token_1):
    """
    Testing channels_list after the user has created a channel.
    """
    channels_create(_token_1, 'channel1', True)
    assert len(channels_list(_token_1)) == 1
    clear()

def test_list_after_joining(_token_1, _token_2, _token_3):
    """
    Test channels_list on a user who is part of multiple channels.
    """
    channels_create(_token_1, 'channel1', True)
    id_2 = channels_create(_token_2, 'channel2', True)['channel_id']
    id_3 = channels_create(_token_3, 'channel3', True)['channel_id']
    channel_join(_token_1, id_2)
    channel_join(_token_1, id_3)
    assert len(channels_list(_token_1)['channels']) == 3
    clear()

def test_list_after_leaving(_token_1, _token_2):
    """
    Test channels_list on a user who is part of multiple channels and
    decides to leave a channel.
    """
    channels_create(_token_1, 'channel1', True)
    id_2 = channels_create(_token_2, 'channel2', True)['channel_id']
    channel_join(_token_1, id_2)
    assert len(channels_list(_token_1)['channels']) == 2
    channel_leave(_token_1, id_2)
    assert len(channels_list(_token_1)['channels']) == 1
    clear()

def test_list_invalid_token(_token_1):
    """
    Test channels_list on a an invalid user.
    """
    channels_create(_token_1, 'channel1', True)
    with pytest.raises(AccessError):
        channels_list(encode_token('invalid@gmail.com'))
    clear()

###################### TESTS FOR channels_listall ###########################

def test_listall_empty(_token_1):
    """
    Test that channels_listall returns an empty list when no channels have
    been created.
    """
    assert channels_listall(_token_1) == {'channels': []}
    clear()

def test_listall_single(_token_1):
    """
    Testing channels_listall after one channel has been created.
    """
    channels_create(_token_1, 'channel1', True)
    assert len(channels_listall(_token_1)['channels']) == 1
    clear()

def test_list_all_multiple(_token_1, _token_2):
    """
    Testing channels_listall after multiple channels have been created.
    """
    channels_create(_token_1, 'channel1', True)
    channels_create(_token_2, 'channel2', True)
    channels_create(_token_2, 'channel3', True)
    assert len(channels_listall(_token_1)['channels']) == 3
    clear()

def test_listall_invalid_token():
    """
    Testing channels_listall with an invalid user.
    """
    with pytest.raises(AccessError):
        channels_listall(encode_token("invalid@gmail.com"))
    clear()

##################### TESTS FOR channels_create ##########################

def test_channels_create(_token_1):
    """
    Test for creating a single channel.
    """
    id_1 = channels_create(_token_1, 'channel1', True)['channel_id']
    assert isinstance(id_1, int) is True
    clear()

def test_channels_create_multiple(_token_1, _token_2, _token_3):
    """
    Test for creating multiple channels.
    """
    id_1 = channels_create(_token_1, 'channel1', True)['channel_id']
    id_2 = channels_create(_token_2, 'channel2', True)['channel_id']
    id_3 = channels_create(_token_3, 'privatechannel', False)['channel_id']
    assert (isinstance(id_1, int) == isinstance(id_2, int)
            == isinstance(id_3, int)) is True
    assert id_1 != id_2 != id_3
    clear()

def test_create_name_too_long(_token_2):
    """
    Test channels_create when the name is longer than 20 characters.
    """
    with pytest.raises(InputError):
        channels_create(_token_2, 'channelthatiswayyytooolong', True)
    clear()

def test_create_invalid_token():
    """
    Test channels_create with an invalid user.
    """
    with pytest.raises(AccessError):
        channels_create(encode_token('invalid@gmail.com'), 'channel1', True)
    clear()


#################### TESTS FOR HELPER FUNCTION ###########################

def test_check_token(_token_1):
    assert type(check_token(decode_token(_token_1))) == int
    assert check_token("") is False
    assert check_token("invalidtoken") is False
