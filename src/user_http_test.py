'''running tests for user functions'''

import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import pytest
from auth import decode_token, encode_token, auth_register,auth_login
from data import data
from user import user_profile
from other import clear

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


################### HTTP TESTS FOR user_profile ##########################

def test_url(url):
    """
    Sanity check to test that server is setup properly.
    """    
    assert url.startswith("http")

def test_user_profile_spec(url, _USER_1):
    """
    Test that user_profile returns a dict with a matching u_id.
    """
    token = _USER_1['token']
    u_id = _USER_1['u_id']
    payload = requests.get(url + "/user/profile", 
                            params={'token': token, 'u_id':u_id}).json()

    assert isinstance(payload, dict) is True
    assert len(payload) == 1
    assert payload['user']['u_id'] == u_id

    # A few white-box tests just to make sure
    assert payload['user']['email'] == 'test@gmail.com'
    assert payload['user']['name_first'] == 'Oliver'
    assert payload['user']['name_last'] == 'Xu'


def test_server_multiple_users_profile(url, _USER_1, _USER_2):
    """
    Test that user_profile returns the correct u_id when there are
    multiple users.
    """
    token1 = _USER_1['token']
    token2 = _USER_2['token']

    u_id1 = _USER_1['u_id']
    u_id2 = _USER_2['u_id']

    payload1 = requests.get(url + "/user/profile", 
                            params={'token': token1, 'u_id':u_id1}).json()

    payload2 = requests.get(url + "/user/profile", 
                            params={'token': token2, 'u_id':u_id2}).json()

    assert payload1['user']['u_id'] == u_id1
    assert payload2['user']['u_id'] == u_id2
    assert payload1['user']['u_id'] != payload2['user']['u_id']


def test_server_profile_invalid_token(url, _USER_1):
    """
    Test that Error 400 (AccessError) is raised when an invalid token is
    passed.
    """
    u_id = _USER_1['u_id']

    invalid_token = encode_token("thisisaninvalidtoken")

    payload = requests.get(url + "/user/profile", 
                            params={'token': invalid_token,'u_id':u_id}).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>User is not authorised</p>")


def test_server_invalid_uid(url, _USER_1, _USER_2):
    """
    Test that Error 400 (InputError) is raised when an invalid u_id is
    passed.
    """
    
    token = _USER_1['token']
    u_id = "42"

    payload = requests.get(url + "/user/profile", 
                            params={'token': token, 'u_id':u_id}).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>u_id is not a valid user</p>")



################ HTTP TESTS FOR user_profile_setname #####################

def test_payload_setname(url, _USER_1):
    """
    A simple test just to check the return value.
    """
    token = _USER_1['token']
    name_change = {
        'token': token,
        'name_first': 'testnewfirstname',
        'name_last': 'testnewlastname'
    }

    assert (requests.put(url + 'user/profile/setname', 
            json=name_change)).json() == {}


def test_server_setname_spec(url, _USER_1):
    """
    Test that user_profile_setname does in fact change the name.
    """

    token = _USER_1['token']
    u_id = _USER_1['u_id']

    # Get the first and last names before the change.
    profile = requests.get(url + "/user/profile", 
                            params={'token': token, 'u_id':u_id}).json()
    f_name_before = profile['user']['name_first']
    l_name_before = profile['user']['name_last']

    name_change = {
        'token': token,
        'name_first': 'testnewfirstname',
        'name_last': 'testnewlastname'
    }

    # Change the name.
    requests.put(url + 'user/profile/setname', json=name_change)

    # Get the first and last names after the change.
    profile = requests.get(url + "/user/profile", 
                            params={'token': token, 'u_id':u_id}).json()
    f_name_after = profile['user']['name_first']
    l_name_after = profile['user']['name_last']

    assert f_name_before != f_name_after
    assert l_name_before != l_name_after

    # A few white-box tests just to make sure.
    assert f_name_before == 'Oliver'
    assert f_name_after == 'testnewfirstname'
    assert l_name_before == 'Xu'
    assert l_name_after == 'testnewlastname'


def test_server_setname_invalid_token(url):
    """
    Test that Error 400 (AccessError) is raised when an invalid token is
    passed.
    """

    name_change = {
        'token': encode_token("thisisaninvalidtoken"),
        'name_first': 'testnewfirstname',
        'name_last': 'testnewlastname'
    }

    payload = requests.put(url + 'user/profile/setname', 
                                json=name_change).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>User is not authorised</p>")


def test_server_invalid_first_names(url, _USER_1):
    """
    Test that Error 400 (InputError) is raised with invalid first names.
    """

    token = _USER_1['token']

    name_change1 = {
        'token': token,
        'name_first': '',
        'name_last': 'testnewlastname'
    }

    name_change2 = {
        'token': token,
        'name_first': 'thisisareallyreallyreallyyylongfirstnamethatisinvalid',
        'name_last': 'testnewlastname'
    }

    payload1 = requests.put(url + 'user/profile/setname', 
                                json=name_change1).json()

    payload2 = requests.put(url + 'user/profile/setname', 
                                json=name_change2).json()

    assert payload1['code'] == payload2['code'] == 400
    assert (payload1['message'] == payload2['message'] ==  
            ("<p>First name must be 1 to 50 characters inclusive</p>"))


def test_server_invalid_last_names(url, _USER_1):
    """
    Test that Error 400 (InputError) is raised with invalid last names.
    """
    token = _USER_1['token']

    name_change1 = {
        'token': token,
        'name_first': 'testfirstname',
        'name_last': ''
    }

    name_change2 = {
        'token': token,
        'name_first': 'testfirstname',
        'name_last': 'thisisareallyreallyreallyyylonglastnamethatisinvalid'
    }

    payload1 = requests.put(url + 'user/profile/setname', 
                                json=name_change1).json()

    payload2 = requests.put(url + 'user/profile/setname', 
                                json=name_change2).json()

    assert payload1['code'] == payload2['code'] == 400
    assert (payload1['message'] == payload2['message'] ==  
            ("<p>Last name must be 1 to 50 characters inclusive</p>"))



################ HTTP TESTS FOR user_profile_setemail #####################

def test_server_setemail_return(url, _USER_1):
    """
    Quick test just to check the return value.
    """

    token = _USER_1['token']
    email_change = {
        'token': token,
        'email': 'newemail@gmail.com'
    }

    assert (requests.put(url + 'user/profile/setemail', 
            json=email_change)).json() == {}


def test_server_setemail_spec(url, _USER_1):
    """
    Test the user_profile_setemail actually changes the email.
    """

    token = _USER_1['token']
    u_id = _USER_1['u_id']

    profile = requests.get(url + "/user/profile", 
                            params={'token': token, 'u_id':u_id}).json()

    # Get the email of the user before any change.
    email_before = profile['user']['email']

    email_change = {
        'token': token,
        'email': 'newemail@gmail.com'
    }

    # Change the email.
    requests.put(url + "/user/profile/setemail", json=email_change)

    profile = requests.get(url + "/user/profile", 
                            params={'token': token, 'u_id':u_id}).json()

    # Get the email of the user after it has been changed.
    email_after = profile['user']['email']

    assert email_before != email_after

    # A few white-box tests just to be sure.
    assert email_before == "test@gmail.com"
    assert email_after == "newemail@gmail.com"


def test_setemail_invalid_token(url):
    """
    Test that Error 400 (AccessError) is raised when an invalid token is
    passed.
    """

    email_change = {
        'token': encode_token("thisisaninvalidtoken"),
        'email': 'newemail@gmail.com'
    }

    payload = requests.put(url + "/user/profile/setemail", 
                            json=email_change).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>User is not authorised</p>")


def test_setemail_invalid_email(url, _USER_1):
    """
    Test that Error 400 (InputError) is raised with an invalid email.
    """

    token = _USER_1['token']

    email_change = {
        'token': token,
        'email': 'thisisnotavalidemail'
    }

    payload = requests.put(url + "/user/profile/setemail", 
                            json=email_change).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>The email you have entered is " 
                                    "not valid</p>")


def test_setemail_already_used(url, _USER_1, _USER_2):
    """
    Test that Error 400 (InputError) is raised when an email entered is
    already being used.
    """

    token = _USER_2['token']
    u_id = _USER_2['u_id']

    profile = requests.get(url + "/user/profile", 
                            params={'token': token, 'u_id':u_id}).json()

    # Getting _USER_2's email.
    email_user2 = profile['user']['email']

    token1 = _USER_1['token']

    # _USER_1 is trying to use _USER_2's email.
    email_change = {
        'token': token1,
        'email': email_user2
    }

    payload = requests.put(url + "/user/profile/setemail", 
                            json=email_change).json()

    assert payload["code"] == 400
    assert payload["message"] == ("<p>The email you are using already " 
                                    "has an account</p>")


################ testing change user/profile/sethandle ###################
def test_good_handle(url, _USER_1):
    """
    Test that a handle is successfully changed
    """

    token = _USER_1['token']
    u_id = _USER_1['u_id']

    old_handle = requests.get(url + "/user/profile", 
                            params={'token': token, 'u_id': u_id}).json()['user']['handle_str']

    
    handlechange = {
        'token': token,
        'handle_str': 'llamas'
    }
    requests.put(url + '/user/profile/sethandle', json=handlechange).json()
   
    new_handle = ''

    profile = requests.get(url + "/user/profile", 
                            params={'token': token, 'u_id': u_id}).json()

    new_handle = profile['user']['handle_str']
    
    assert old_handle != new_handle
    assert new_handle == 'llamas'
    

def test_try_existing_handle(url, _USER_1, _USER_2):
    """
    try set the handle of user 1 to handle of user 2 to test that error is returned
    """

    token1 = _USER_1['token']

    #finding handle of second user
    u_id2 = _USER_2['u_id']
    token2 = _USER_2['token']

    profile2 = requests.get(url + "/user/profile", 
                            params={'token': token2, 'u_id': u_id2}).json()

    handle2 = profile2['user']['handle_str']
    

    handlechange = {
        'token': token1,
        'handle_str': handle2
    }
    payload = requests.put(url + '/user/profile/sethandle', json=handlechange).json()

    assert payload["code"] == 400
    assert payload["message"] == "<p>This handle is already in use, please choose a different one.</p>"

def test_try_short_handle(url, _USER_1):
    """
    tessting that error is returned for handles that's too short
    """
    token = _USER_1['token']
    handle = 'hi'
    handlechange = {
        'token': token,
        'handle_str': handle
    }
    payload = requests.put(url + '/user/profile/sethandle', json=handlechange).json()

    assert payload["code"] == 400
    assert payload["message"] == "<p>Please enter a valid handle.</p>"

def test_try_long_handle(url, _USER_1):
    """
    tessting that error is returned for handles that's too long
    """
    token = _USER_1['token']
    handle = 'llamasalpacasandcamelstoo'
    handlechange = {
        'token': token,
        'handle_str': handle
    }
    payload = requests.put(url + '/user/profile/sethandle', json=handlechange).json()

    assert payload["code"] == 400
    assert payload["message"] == "<p>Please enter a valid handle.</p>"
    


############ HTTP TESTS FOR user_profile_uploadphoto #####################

# Just a random image off the internet (Note: Dimensions = 860 x 600)
img_url = "https://cdn.broadsheet.com.au/cache/00/af/00af554d122dd2fe2dcce93d26fd309e.jpg"

def test_server_return_photo(url, _USER_1):
    """
    Test that the server returns {}.
    """
    token = _USER_1['token']

    info = {
        'token': token,
        'img_url': img_url,
        'x_start': 0,
        'y_start': 0,
        'x_end': 800,
        'y_end': 500
    }

    payload = requests.post(url + '/user/profile/uploadphoto', json=info).json()
    assert payload == {}

def test_server_bad_img_url(url, _USER_1):
    """ 
    Test that InputError (400) is raised with an invalid url.
    """
    bad_url = "hellonotavalidurl"
    token = _USER_1['token']
    info = {
        'token': token,
        'img_url': bad_url,
        'x_start': 0,
        'y_start': 0,
        'x_end': 800,
        'y_end': 500
    }

    payload = requests.post(url + '/user/profile/uploadphoto', json=info).json()

    assert payload['code'] == 400

def test_server_photo_invalid_token(url, _USER_1):
    """ 
    Test that AccessError (400) is raised with an invalid token.
    """

    bad_token = encode_token("thisisaninvalidtoken")
    info = {
        'token': bad_token,
        'img_url': img_url,
        'x_start': 0,
        'y_start': 0,
        'x_end': 800,
        'y_end': 500
    }

    payload = requests.post(url + '/user/profile/uploadphoto', json=info).json()

    assert payload['code'] == 400
    assert payload['message'] == '<p>User is not authorised</p>'


def test_server_notjpg(url, _USER_1):
    """
    Test that InputError is raised when the image uploaded is not a jpg.
    """
    not_jpg = "https://memeguy.com/photos/images/my-brother-is-getting-his-bs-in-computer-science-249943.png"
    token = _USER_1['token']
    info = {
        'token': token,
        'img_url': not_jpg,
        'x_start': 0,
        'y_start': 0,
        'x_end': 800,
        'y_end': 500
    }

    payload = requests.post(url + '/user/profile/uploadphoto', json=info).json()

    assert payload['code'] == 400
    assert payload['message'] == "<p>Image uploaded is not a JPG</p>"


def test_server_bad_crop_dimensions(url, _USER_1):
    """
    Test that InputError is raised when the crop dimensions are not within
    the dimensions of the image.
    """

    token = _USER_1['token']
    info = {
        'token': token,
        'img_url': img_url,
        'x_start': 0,
        'y_start': 0,
        'x_end': 100000,
        'y_end': -120
    }

    payload = requests.post(url + '/user/profile/uploadphoto', json=info).json()

    assert payload['code'] == 400
    assert payload['message'] == "<p>Crop not within dimensions of image</p>"

    clear()