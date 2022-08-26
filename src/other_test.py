"""
Test file for functions in other.py
"""

# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

##################### importing files ####################

import pytest
import user
from auth import auth_login, auth_register, auth_logout, encode_token, hash_password
from error import InputError, AccessError
from other import clear, users_all
import other
import auth
import channel as ch
import channels as chs
import message as msg

#################### Pytest Fixtures #####################


@pytest.fixture
def clear_data():
    """
    Clears the previous data from the flockr
    """
    other.clear()

@pytest.fixture
def liam():
    """
    Set up a user called liam and login to the flockr
    """
    set_up_liam = auth.auth_register("liam.treavors@gmail.com", "mypassword1", "Liam", "Treavors")
    set_up_liam = auth.auth_login("liam.treavors@gmail.com", "mypassword1")
    return set_up_liam

@pytest.fixture
def oliver():
    """
    Set up a user called oliver
    """
    clear()
    auth.auth_register('test@gmail.com', 'password', 'Oliver', 'Xu')
    set_up_oliver = auth_login('test@gmail.com', 'password')
    return set_up_oliver

@pytest.fixture
def daniel():
    """
    Set up a user called daniel
    """
    set_up_daniel = auth.auth_register("daniel.steyn@gmail.com", "mypassword3", "Daniel", "Steyn")
    return set_up_daniel

@pytest.fixture
def mikkel():
    """
    Set up a user called mikkel
    """
    set_up_mikkel = auth.auth_register("mikkel@gmail.com", "mypassword2", "Mikkel", "Endresen")
    return set_up_mikkel

@pytest.fixture
def public_channel_1(liam):
    """
    Set up a public channel with liam as the owner
    """
    set_up_public_channel = chs.channels_create(liam['token'], "public_channel", True)
    return set_up_public_channel['channel_id']

@pytest.fixture
def public_channel_2(liam):
    """
    Set up a public channel with liam as the owner
    """
    set_up_public_channel = chs.channels_create(liam['token'], "public_channel", True)
    return set_up_public_channel['channel_id']

@pytest.fixture
def public_channel_3(liam):
    """
    Set up a public channel with liam as the owner
    """
    set_up_public_channel = chs.channels_create(liam['token'], "public_channel", True)
    return set_up_public_channel['channel_id']

@pytest.fixture
def private_channel(liam):
    """
    Set up a private channel with liam as the owner
    """
    set_up_private_channel = chs.channels_create(liam['token'], "private_channel", False)
    return set_up_private_channel['channel_id']

@pytest.fixture
def send_msg(liam, mikkel, public_channel_1):
    """
    Sends a single message to a channel
    """
    ch.channel_invite(liam["token"], public_channel_1, mikkel["u_id"])
    msg.message_send(liam["token"], public_channel_1, "hello world")

@pytest.fixture
def send_msg_multiple(liam, mikkel, daniel, public_channel_1, public_channel_2, public_channel_3):
    """
    Sends a single message to a channel
    """
    ch.channel_invite(liam["token"], public_channel_1, mikkel["u_id"])
    ch.channel_invite(liam["token"], public_channel_2, mikkel["u_id"])
    ch.channel_invite(liam["token"], public_channel_1, daniel["u_id"])

    # send messages to channel 1
    msg.message_send(liam["token"], public_channel_1, "hello world")
    msg.message_send(liam["token"], public_channel_1, "world")
    msg.message_send(liam["token"], public_channel_1, "hello")
    msg.message_send(liam["token"], public_channel_1, "hello wor")

    # send messages to channel 2
    msg.message_send(liam["token"], public_channel_2, "hello world")
    msg.message_send(liam["token"], public_channel_2, "hello wo")
    msg.message_send(liam["token"], public_channel_2, "hel")
    msg.message_send(liam["token"], public_channel_2, "hello")

    # send messages to channel 3
    msg.message_send(liam["token"], public_channel_3, "hello world")
    msg.message_send(liam["token"], public_channel_3, "hello")
    msg.message_send(liam["token"], public_channel_3, "hahaha")

    # send messages from mikkel
    auth.auth_logout(liam["token"])
    mikkel = auth.auth_login("mikkel@gmail.com", "mypassword2")

    # send messages to channel 1
    msg.message_send(mikkel["token"], public_channel_1, "hello")
    msg.message_send(mikkel["token"], public_channel_1, "hi")
    msg.message_send(mikkel["token"], public_channel_1, "hello world")

    # send messages to channel 2
    msg.message_send(mikkel["token"], public_channel_2, "how are you?")
    msg.message_send(mikkel["token"], public_channel_2, "howdy")

    auth.auth_logout(mikkel["token"])
    liam = auth.auth_login("liam.treavors@gmail.com", "mypassword1")

##################### TESTS FOR admin_userpermission_change ##########################

def test_admin_change_invalid_user(clear_data, liam):
    """
    Testing that an invalid user raises an Input Error
    """
    with pytest.raises(InputError):
        other.admin_userpermission_change(liam["token"], 1000, 2)

def test_admin_change_invalid_permission_id(clear_data, liam):
    """
    Testing that an invalid permission id raises an Input Error
    """
    with pytest.raises(InputError):
        other.admin_userpermission_change(liam['token'], 1, 3)

def test_admin_change_invalid_access(clear_data, liam, mikkel):
    """
    Testing that an invalid token raises an Access Error
    """
    auth.auth_logout(liam["token"])
    mikkel = auth.auth_login("mikkel@gmail.com", "mypassword2")
    with pytest.raises(AccessError):
        other.admin_userpermission_change(mikkel["token"], liam['u_id'], 2)

def test_admin_change_valid(clear_data, liam, mikkel):
    """
    Testing that a user's permission can actually be changed
    """

    assert not other.user_is_admin(mikkel["u_id"])
    other.admin_userpermission_change(liam['token'], mikkel['u_id'], 1)
    assert other.user_is_admin(mikkel["u_id"])

def test_admin_change_multiple(clear_data, liam, mikkel):
    """ Testing that a user that is made an owner can change permissions """
    other.admin_userpermission_change(liam['token'], mikkel['u_id'], 1)
    auth.auth_logout(liam['token'])
    mikkel = auth.auth_login("mikkel@gmail.com", "mypassword2")
    other.admin_userpermission_change(mikkel['token'], liam['u_id'], 2)

    assert not other.user_is_admin(liam["u_id"])


##################### TESTS FOR search ##########################

def test_search_invalid_token(clear_data, liam, mikkel):
    """
    Test search function with an invalid access token
    """
    auth.auth_logout(mikkel['token'])

    with pytest.raises(AccessError):
        other.search(mikkel["token"], "should fail")

def test_search_no_messages(clear_data, liam, public_channel_1):
    """
    Test search function when no messages exist
    """
    message_list = other.search(liam["token"], "no messages")
    assert len(message_list['messages']) == 0

def test_search_exact_match(clear_data, liam, public_channel_1, send_msg):
    """
    Test search function when the query string exactly matches a message
    """
    message_list = other.search(liam["token"], "hello world")
    assert len(message_list['messages']) == 1
    assert any(msg["message"] == "hello world" for msg in message_list['messages'])

def test_search_sender_searches(clear_data, liam, public_channel_1, send_msg):
    """
    Test search function returns correct message sender u_id
    when sender searches
    """
    message_list = other.search(liam["token"], "hello world")
    assert message_list['messages'][0]["u_id"] == liam['u_id']

def test_search_non_sender_searches(clear_data, liam, mikkel, public_channel_1, send_msg):
    """
    Test search function returns correct message sender u_id
    when a user who didn't send it searches
    """
    auth.auth_logout(liam["token"])
    mikkel = auth.auth_login("mikkel@gmail.com", "mypassword2")
    message_list = other.search(mikkel["token"], "hello world")
    assert message_list['messages'][0]["u_id"] == liam['u_id']

def test_search_front_match(clear_data, liam, public_channel_1, send_msg):
    """
    Test search function when the query string exactly matches a message
    """
    message_list = other.search(liam["token"], "hello")
    assert len(message_list['messages']) == 1
    assert any(msg["message"] == "hello world" for msg in message_list['messages'])

def test_search_back_match(clear_data, liam, public_channel_1, send_msg):
    """
    Test search function when the query string exactly matches a message
    """
    message_list = other.search(liam["token"], "world")
    assert len(message_list['messages']) == 1
    assert any(msg["message"] == "hello world" for msg in message_list['messages'])

def test_search_middle_match(clear_data, liam, public_channel_1, send_msg):
    """
    Test search function when the query string exactly matches a message
    """
    message_list = other.search(liam["token"], "lo wo")
    assert len(message_list['messages']) == 1
    assert any(msg["message"] == "hello world" for msg in message_list['messages'])

def test_search_not_sender(clear_data, liam, mikkel, public_channel_1, send_msg):
    """
    Test that a user who did not send the message can still find it in a search
    """
    auth.auth_logout(liam["token"])
    mikkel = auth.auth_login("mikkel@gmail.com", "mypassword2")
    message_list = other.search(mikkel["token"], "hello world")
    assert len(message_list['messages']) == 1
    assert any(msg["message"] == "hello world" for msg in message_list['messages'])

def test_search_not_in_channel(clear_data, liam, mikkel, daniel, public_channel_1, send_msg):
    """
    Test that a user who is not in a channel cannot see the message that is searched for
    """
    auth.auth_logout(liam["token"])
    daniel = auth.auth_login("daniel.steyn@gmail.com", "mypassword3")
    message_list = other.search(daniel["token"], "hello world")
    assert len(message_list['messages']) == 0
    assert not any(msg["message"] == "hello world" for msg in message_list['messages'])

def test_search_multiple_all_channels(clear_data, liam, mikkel, daniel,
                                      public_channel_1, send_msg_multiple):
    """
    Tests that messages sent in multiple channels are recorded in search
    """

    message_list_1 = other.search(liam["token"], "hello world")
    message_list_2 = other.search(liam["token"], "hello")
    message_list_3 = other.search(liam["token"], "wo")
    message_list_4 = other.search(liam["token"], "how")

    assert len(message_list_1['messages']) == 4
    assert len(message_list_2['messages']) == 10
    assert len(message_list_3['messages']) == 7
    assert len(message_list_4['messages']) == 2

def test_search_multiple_senders(clear_data, liam, mikkel, daniel,
                                 public_channel_1, send_msg_multiple):
    """
    Test search function correctly returns sender u_id when
    multiple users have sent similar messages
    """
    message_list = other.search(liam["token"], "hello")

    liam_count = 0
    mikkel_count = 0

    for message in message_list['messages']:
        if message["u_id"] == liam["u_id"]:
            liam_count += 1
        elif message["u_id"] == mikkel["u_id"]:
            mikkel_count += 1

    assert liam_count == 8
    assert mikkel_count == 2

def test_search_multiple_missing_channel(clear_data, liam, mikkel, daniel,
                                         public_channel_1, send_msg_multiple):
    """
    Tests that messages sent in multiple channels are recorded in search
    but user is not in one of the channels
    """
    auth.auth_logout(liam["token"])
    mikkel = auth.auth_login("mikkel@gmail.com", "mypassword2")
    message_list_1 = other.search(mikkel["token"], "hello world")
    message_list_2 = other.search(mikkel["token"], "hello")
    message_list_3 = other.search(mikkel["token"], "wo")
    message_list_4 = other.search(mikkel["token"], "how")

    assert len(message_list_1['messages']) == 3
    assert len(message_list_2['messages']) == 8
    assert len(message_list_3['messages']) == 6
    assert len(message_list_4['messages']) == 2


def test_search_multiple_missing_channels(clear_data, liam, mikkel, daniel,
                                          public_channel_1, send_msg_multiple):
    """
    Tests that messages sent in multiple channels are recorded in search
    but user is only in one channel
    """
    auth.auth_logout(liam["token"])
    daniel = auth.auth_login("daniel.steyn@gmail.com", "mypassword3")
    message_list_1 = other.search(daniel["token"], "hello world")
    message_list_2 = other.search(daniel["token"], "hello")
    message_list_3 = other.search(daniel["token"], "wo")
    message_list_4 = other.search(daniel["token"], "how")

    assert len(message_list_1['messages']) == 2
    assert len(message_list_2['messages']) == 5
    assert len(message_list_3['messages']) == 4
    assert len(message_list_4['messages']) == 0

def test_search_is_user_reacted(clear_data, liam, public_channel_1):
    '''
    Test to check that the function adds the react dictionary correctly
    '''
    message = msg.message_send(liam['token'], public_channel_1, 'Hey')
    message_list = other.search(liam["token"], "Hey")
    assert message_list['messages'][0]['reacts'][0]['is_this_user_reacted'] == False
    msg.message_react(liam['token'], message['message_id'], 1)
    message_list = other.search(liam["token"], "Hey")
    assert message_list['messages'][0]['reacts'][0]['is_this_user_reacted'] == True

##################### TESTS FOR users_all ########################

def test_one_user(oliver):
    """
    test when one user is registered
    """
    token = oliver['token']
    assert users_all(token)['users'] == [
                                {'u_id': 1,
                                 'email': 'test@gmail.com',
                                 'name_first': 'Oliver',
                                 'name_last': 'Xu',
                                 'handle_str': 'oliverxu0',
                                 'profile_img_url': None
                                }
                                ]
    clear()

def test_two_users(oliver, liam):
    """
    test when more than one user is registered
    """
    token = liam['token']
    assert users_all(token)['users'] == [{'u_id': 1,
                                 'email': 'test@gmail.com',
                                 'name_first': 'Oliver',
                                 'name_last': 'Xu',
                                 'handle_str': 'oliverxu0',
                                 'profile_img_url': None
                                },
                                {'u_id': 2,
                                 'email': 'liam.treavors@gmail.com',
                                 'name_first': 'Liam',
                                 'name_last': 'Treavors',
                                 'handle_str': 'liamtreavors0',
                                 'profile_img_url': None
                                }]
    clear()
