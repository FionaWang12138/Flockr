'''running tests for auth functions'''
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import pytest
from auth import decode_token, encode_token

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

@pytest.fixture
def register_user_bob(url):
    '''
    a fixture to register a user named bob
    '''
    data = {'email': 'bobsmith@gmail.com',
            'password': 'iloveshrek',
            'name_first': 'Bob',
            'name_last': 'Smith'}

    payload = requests.post(url + "/auth/register", json=data) .json()
    return payload

@pytest.fixture
def register_user_fiona(url):
    '''
    a fixture to register a user named fiona
    '''
    data = {'email': 'fionawang@gmail.com',
            'password': 'iloveshrek',
            'name_first': 'Fiona',
            'name_last': 'Wang'}

    payload = requests.post(url + "/auth/register", json=data) .json()
    return payload

@pytest.fixture
def login_bob(url, register_user_bob):
    '''
    A fixture to login a user bob
    '''
    data = {'email': 'bobsmith@gmail.com',
            'password': 'iloveshrek'}

    payload = requests.post(url + "/auth/login", json=data).json()
    return payload

def test_url(url):
    '''
    # is my url a url?
    '''
    assert url.startswith("http")

def test_flask_register(url, register_user_bob):
    '''
    testing flask server for register
    '''
    data = {'email': 'annasmith@gmail.com',
            'password': 'iloveshrek',
            'name_first': 'Anna',
            'name_last': 'Smith'}

    payload = requests.post(url + "/auth/register", json=data).json()

    assert payload == {'u_id': 2,
                       'token': encode_token('annasmith@gmail.com_a')}

def test_flask_register_error_email(url):
    '''
    testing flask server for raising error give invalid email
    '''
    data = {'email': 'bobsmith',
            'password': 'iloveshrek',
            'name_first': 'Bob',
            'name_last': 'Smith'}
    payload = requests.post(url + "/auth/register", json=data).json()

    assert payload["code"] == 400
    assert payload["message"] == "<p>Please enter a valid email adress.</p>"

def test_flask_register_error_paasword(url):
    '''
    testing flask server for raising error give invalid password
    '''
    data = {'email': 'johnsmith@gmail.com',
            'password': 'shrek',
            'name_first': 'John',
            'name_last': 'Smith'}

    payload = requests.post(url + "/auth/register", json=data).json()

    assert payload["code"] == 400
    assert payload["message"] == "<p>Please enter a password with 6 or more characters.</p>"


def test_flask_login(url, register_user_bob, register_user_fiona):
    '''test login function with correct input'''
    data = {'email': 'bobsmith@gmail.com',
            'password': 'iloveshrek'}

    payload = requests.post(url + "/auth/login", json=data).json()

    assert payload == {'u_id': 1,
                       'token': encode_token('bobsmith@gmail.com_a')}

    data = {'email': 'fionawang@gmail.com',
            'password': 'iloveshrek'}

    payload = requests.post(url + "/auth/login", json=data).json()

    assert payload == {'u_id': 2,
                       'token': encode_token('fionawang@gmail.com_a')}

def test_flask_login_wrong_password(url, register_user_bob):
    '''test login function with wrong password'''
    data = {'email': 'bobsmith@gmail.com',
            'password': 'ilovershre'}

    payload = requests.post(url + "/auth/login", json=data).json()

    assert payload["code"] == 400
    assert payload["message"] == "<p>The password you entered doesn't match your email.</p>"

def test_flask_logout(url, register_user_bob):
    '''
    logging out dear bob given then hes already logged in
    '''
    data = {'email': 'bobsmith@gmail.com',
            'password': 'iloveshrek'}

    payload = requests.post(url + "/auth/login", json=data).json()
    token = {'token': payload["token"]}

    payload2 = requests.post(url + "/auth/logout", json=token).json()

    assert payload2["is_success"] is True

def test_flask_fail_logout(url):
    '''
    testing failed logout when already logged out
    '''
    data = {'email': 'bobsmith@gmail.com',
            'password': 'iloveshrek',
            'name_first': 'Bob',
            'name_last': 'Smith'}

    payload = requests.post(url + "/auth/register", json=data) .json()

    token = {'token': payload["token"]}
    requests.post(url + "/auth/logout", json=token).json()

    payload2 = requests.post(url + "/auth/logout", json=token).json()

    assert payload2["is_success"] is False

###################################TESTING request password reset##########################
def test_request_code(url, register_user_bob):
    """
    testing that the auth/passwordreset/request route returns an empty dictionary
    """
    email = {'email': 'bobsmith@gmail.com'}
    payload = requests.post(url + "auth/passwordreset/request", json=email).json()

    assert payload == {}

#############################Testing passwordreset reset######################
def test_wrong_code(url, register_user_bob):
    """
    Tests that error is raised for wrong reset code
    """
    email = {'email': 'bobsmith@gmail.com'}
    requests.post(url + "auth/passwordreset/request", json=email).json()
    reset_detail = {'reset_code': 'wrong_code',
                    'new_password': 'bobiscool'}
    payload = requests.post(url + "auth/passwordreset/reset", json=reset_detail).json()

    assert payload["code"] == 400
    assert payload["message"] == "<p>The code you've entered is invalid.</p>"

def test_bad_password(url, register_user_bob):
    """
    Test that error is raised for bad password
    """
    email = {'email': 'bobsmith@gmail.com'}
    requests.post(url + "auth/passwordreset/request", json=email).json()
    reset_detail = {'reset_code': 'wrong_code',
                    'new_password': '123'}
    payload = requests.post(url + "auth/passwordreset/reset", json=reset_detail).json()

    assert payload["code"] == 400
    assert payload["message"] == "<p>Please enter a password with 6 or more characters.</p>"
    
