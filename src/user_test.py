""" TESTS FOR USER.PY """

import pytest
import user
from PIL import Image
from auth import auth_login, auth_register, encode_token, hash_password
from error import InputError, AccessError
from other import clear
from pathlib import Path

##################### FIXTURES FOR CREATING USERS ########################
@pytest.fixture
def _USER_1():
    """
    Registers and logs in a user returning a dictionary containing the
    token and u_id.

    Returns:
        dictionary: {
            'token':
            'u_id:
            }
    """
    clear()
    auth_register('test@gmail.com', 'password', 'Oliver', 'Xu')
    return {
        'token': auth_login('test@gmail.com', 'password')['token'],
        'u_id': auth_login('test@gmail.com', 'password')['u_id']
    }

@pytest.fixture
def _USER_2():
    """
    Registers and logs in another user returning a dictionary containing the
    token and u_id.

    Returns:
        dictionary: {
            'token':
            'u_id:
            }
    """

    auth_register('hello@gmail.com', '12345678', 'John', 'Smith')
    return {
        'token': auth_login('hello@gmail.com', '12345678')['token'],
        'u_id': auth_login('hello@gmail.com', '12345678')['u_id']
    }



##################### TESTS FOR user_profile #############################

def test_sanity(_USER_1):
    """
    Sanity test to make sure user_profile returns a dictionary.
    """
    profile = user.user_profile(_USER_1['token'], _USER_1['u_id'])
    assert isinstance(profile, dict) is True
    clear()


def test_spec_profile(_USER_1):
    """
    Test that user_profile returns a matching u_id.
    """
    profile = user.user_profile(_USER_1['token'], _USER_1['u_id'])
    assert profile['user']['u_id'] == _USER_1['u_id']
    clear()


def test_multiple_users(_USER_1, _USER_2):
    """
    Test that user_profile returns the correct u_id when there are
    multiple users.
    """
    profile_1 = user.user_profile(_USER_1['token'], _USER_1['u_id'])
    profile_2 = user.user_profile(_USER_2['token'], _USER_2['u_id'])
    assert profile_1['user']['u_id'] == _USER_1['u_id']
    assert profile_2['user']['u_id'] == _USER_2['u_id']
    clear()


def test_invalid_u_id(_USER_1, _USER_2):
    """
    Test that InputError is raised when the u_id is not valid.
    """
    with pytest.raises(InputError):
        user.user_profile(_USER_1['token'], "42")
    clear()


def test_invalid_token_profile(_USER_1):
    """
    Test that AccessError is raised when an invalid token is passed.
    """
    with pytest.raises(AccessError):
        user.user_profile(encode_token('thisisaninvalidtoken'), _USER_1['u_id'])
    clear()



################### TESTS FOR user_profile_setname #######################


def test_return_val(_USER_1):
    """
    Sanity test just to check the return value.
    """
    return_val = user.user_profile_setname(_USER_1['token'],
                                           'testfirstname', 'testlastname')
    assert return_val == {}
    clear()


def test_spec_setname(_USER_1):
    """
    Test that user_profile_setname does in fact change the name.
    """

    f_name_before = user.user_profile(_USER_1['token'],
                                      _USER_1['u_id'])['user']['name_first']
    l_name_before = user.user_profile(_USER_1['token'],
                                      _USER_1['u_id'])['user']['name_last']

    user.user_profile_setname(_USER_1['token'],
                              'testfirstname', 'testlastname')

    f_name_after = user.user_profile(_USER_1['token'],
                                     _USER_1['u_id'])['user']['name_first']

    l_name_after = user.user_profile(_USER_1['token'],
                                     _USER_1['u_id'])['user']['name_last']

    assert f_name_before != f_name_after
    assert l_name_before != l_name_after
    clear()


def test_invalid_token(_USER_1):
    """
    Test that AccessError is raised when an invalid token is used.
    """
    with pytest.raises(AccessError):
        user.user_profile_setname(encode_token('invalidtoken!!!!!!!!!'),
                                  'testfirstname', 'testlastname')
    clear()


def test_invalid_first_name_1(_USER_1):
    """
    Testing a first name that is 0 characters long.
    """
    with pytest.raises(InputError):
        user.user_profile_setname(_USER_1['token'], '', 'testlastname')
    clear()


def test_invalid_first_name_2(_USER_1):
    """
    Testing a first name that is longer than 50 characters.
    """
    with pytest.raises(InputError):
        user.user_profile_setname(_USER_1['token'],
                                  'thisisareallyreallyreallyyylongfirstnamethatisinvalid',
                                  'testlastname')
    clear()


def test_invalid_last_name_1(_USER_1):
    """
    Testing a last name that is 0 characters long.
    """
    with pytest.raises(InputError):
        user.user_profile_setname(_USER_1['token'], 'testfirstname', '')
    clear()


def test_invalid_last_name_2(_USER_1):
    """
    Testing a last name that is longer than 50 characters.
    """
    with pytest.raises(InputError):
        user.user_profile_setname(_USER_1['token'], 'testfirstname',
                                  'thisisareallyreallyreallyyylonglastnamethatisinvalid')
    clear()


def test_inclusive_names(_USER_1):
    """
    Test that no errors are raised when the first and last names are exactly
    1 and 50 characters long.
    """

    f_name_before = user.user_profile(_USER_1['token'],
                                      _USER_1['u_id'])['user']['name_first']

    user.user_profile_setname(_USER_1['token'],
                              'x', 'u')

    user.user_profile_setname(_USER_1['token'],
                              'okaywowthisisanamethatisexactlyfiftycharacterslong',
                              'wowthisisalastnamethatisexactlyfiftycharacterslong')

    f_name_after = user.user_profile(_USER_1['token'],
                                     _USER_1['u_id'])['user']['name_first']

    assert f_name_before != f_name_after
    clear()



##################### TESTS FOR user_profile_setemail ####################


def test_return_val_email(_USER_1):
    """
    Sanity test to check the return value.
    """

    returns = user.user_profile_setemail(_USER_1['token'],
                                         'testnewemail@gmail.com')
    assert returns == {}
    clear()


def test_spec_setemail(_USER_1):
    """
    Test the user_profile_setemail actually changes the email.
    """

    email_before = user.user_profile(_USER_1['token'],
                                     _USER_1['u_id'])['user']['email']

    user.user_profile_setemail(_USER_1['token'], 'testnewemail@gmail.com')

    email_after = user.user_profile(_USER_1['token'],
                                    _USER_1['u_id'])['user']['email']

    assert email_before != email_after
    clear()


def test_invalid_token_setemail(_USER_1):
    """
    Test that AccessError is raised with an invalid token
    """

    with pytest.raises(AccessError):
        user.user_profile_setemail(encode_token('thisisaninvalidtoken'), 'test@gmail.com')
    clear()


def test_invalid_email(_USER_1):
    """
    Test that InputError is raised when the email is invalid.
    """

    with pytest.raises(InputError):
        user.user_profile_setemail(_USER_1['token'], 'invalidemail')
    clear()


def test_email_aleady_used(_USER_1, _USER_2):
    """
    Test that InputError is raised when the email address is already
    being used by another user.
    """

    email_2 = user.user_profile(_USER_2['token'], _USER_2['u_id'])['user']['email']

    with pytest.raises(InputError):
        user.user_profile_setemail(_USER_1['token'], email_2)
    clear()


##################### TESTS FOR user_profile_sethandle ####################
def test_set_handle(_USER_1):
    """
    Testing that a handle is changed for a valid user
    """
    handle_before = user.user_profile(_USER_1['token'],
                                      _USER_1['u_id'])['user']['handle_str']

    user.user_profile_sethandle(_USER_1['token'], 'iamallamabahaha')

    handle_after = user.user_profile(_USER_1['token'],
                                     _USER_1['u_id'])['user']['handle_str']

    assert handle_before != handle_after
    assert handle_after == 'iamallamabahaha'
    clear()

def test_long_handle(_USER_1):
    """
    testing that error is rasied when handle is too long
    """
    with pytest.raises(InputError):
        user.user_profile_sethandle(_USER_1['token'], 'thisisaveryverylonghandle')
    clear()

def test_short_handle(_USER_1):
    """
    testing that error is rasied when handle is too short
    """
    with pytest.raises(InputError):
        user.user_profile_sethandle(_USER_1['token'], 'hi')
    clear()

def test_invalid_token_sethandle(_USER_1):
    """
    Test that AccessError is raised with an invalid token
    """

    with pytest.raises(AccessError):
        user.user_profile_sethandle(encode_token('badtoken'), 'handle123')
    clear()

def test_handle_aleady_used(_USER_1, _USER_2):
    """
    Test that InputError is raised when the handle is already
    being used by another user.
    """

    handle_2 = user.user_profile(_USER_2['token'], _USER_2['u_id'])['user']['handle_str']

    with pytest.raises(InputError):
        user.user_profile_sethandle(_USER_1['token'], handle_2)
    clear()



################### TESTS FOR user_profile_uploadphoto ###################


# Just a random image off the internet (Note: Dimensions = 860 x 600)
img_url = "https://cdn.broadsheet.com.au/cache/00/af/00af554d122dd2fe2dcce93d26fd309e.jpg"


def test_return_val_upload(_USER_1):
    """
    Just checking that uploadphoto returns {}
    """
    return_val = user.user_profile_uploadphoto(_USER_1['token'], img_url, 
                                                0,0,300,300)
    assert return_val == {}
    clear()


def test_uploadphoto_spec(_USER_1):
    """ 
    Check that the image has been cropped and saved locally.
    """

    user.user_profile_uploadphoto(_USER_1['token'], img_url, 0,0,300,300)

    # Try to find the image locally.
    f = str(Path().absolute()) + "/src/static/00af554d122dd2fe2dcce93d26fd309e.jpg"
    
    error = False
    try:
        image = Image.open(f)
    except FileNotFoundError:
        error = True
    
    # Check that image has been saved locally
    assert error is False

    # Check that image has been cropped.
    x,y = image.size
    assert x == 300
    assert y == 300 
    

def test_invalid_url(_USER_1):
    """ 
    Check InputError is raised with an invalid url.
    """

    invalid_url = "blahblahblahhhnotaurl"
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(_USER_1['token'], invalid_url, 0,0,10,30)


def test_invalid_token_photo(_USER_1):
    """ 
    Check AccessError is raised with an invalid token.
    """

    token = encode_token("invalidtoken")
    with pytest.raises(AccessError):
        user.user_profile_uploadphoto(token, img_url, 0,0,10,30)


def test_img_not_jpg(_USER_1):
    """ 
    Check InputError is raised with an image that is NOT a jpg.
    """

    png = "https://memeguy.com/photos/images/my-brother-is-getting-his-bs-in-computer-science-249943.png"

    with pytest.raises(InputError):
        user.user_profile_uploadphoto(_USER_1['token'], png, 0,0,100,300)


def test_invalid_crop_dimensions(_USER_1):
    """ 
    Check InputError is raised with invalid crop dimensions.
    """

    with pytest.raises(InputError):
        user.user_profile_uploadphoto(_USER_1['token'], img_url, -1,2,-5,1)
        user.user_profile_uploadphoto(_USER_1['token'], img_url, 0,0,5000,20)
        user.user_profile_uploadphoto(_USER_1['token'], img_url, 120,100,0,2)

    clear()

##################### TESTS FOR HELPER FUNCTIONS #########################


def test_check_valid_name():
    assert user.check_valid_name("Oliver") is True
    assert user.check_valid_name("") is False
    assert user.check_valid_name("Namethatiswayyyyyyyyyyyyytoooooooo"
                                    "longggggggggggggggggg") is False

def test_check_valid_email():
    assert user.check_valid_email("valid@gmail.com") is True
    assert user.check_valid_email("hellothere") is False
    assert user.check_valid_email("invalid@") is False

def test_check_valid_handle():
    assert user.check_valid_handle("iliketrains") is True
    assert user.check_valid_handle("lol") is True
    assert user.check_valid_handle("twentycharacterslong") is True
    assert user.check_valid_handle("TOOOOOOOOOOOLONGGGGGGGGGGGGG") is False
    assert user.check_valid_handle("ok") is False
