'''running tests for auth functions'''
import pytest
from other import clear
from error import InputError
from auth import auth_register, auth_login, auth_logout, hash_password
from auth import encode_token, decode_token, check_decoded_token_validity, auth_passwordreset_request, auth_passwordreset_reset

def test_register_user():
    '''test return type for register function'''
    clear()
    value = auth_register('fionawang@gmail.com', 'password', 'Fiona', 'Wang')
    assert isinstance(value, dict) is True

def test_register_different_uid():
    '''tests that u_id is returned, and that its different for different users'''
    clear()
    u_id_1 = auth_register('bob@gmail.com', 'password', 'Fiona', 'Wang')['u_id']
    u_id_2 = auth_register('123@gmail.com', 'password', 'Fiona', 'Wang')['u_id']
    assert u_id_1 != u_id_2

def test_register_different_token():
    '''tests that token is returned, and that its different for different users'''
    clear()
    token_1 = auth_register('bob@gmail.com', '123456', 'Bob', 'Wang')['token']
    token_2 = auth_register('123@gmail.com', '123456', 'Bob', 'Wang')['token']
    assert token_1 != token_2

def test_name_length_1():
    '''testing name length of 1'''
    clear()
    value = auth_register('fionawang@gmail.com', 'password', 'F', 'W')
    assert isinstance(value, dict) is True

def test_name_length_2():
    '''testing name length of 50'''
    clear()
    value = auth_register('fionawang@gmail.com', 'password',
                          'qwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiop',
                          'qwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiop')
    assert isinstance(value, dict) is True

def test_password_length_1():
    '''testing password of length 6'''
    clear()
    value = auth_register('fionawang@gmail.com', 'passwo', 'Fiona', 'Wang')
    assert isinstance(value, dict) is True

def test_register_invalid_email():
    '''testing registration with bad email'''
    clear()
    with pytest.raises(InputError):
        auth_register('fionawang12138', 'password', 'Fiona', 'Wang')
    with pytest.raises(InputError):
        auth_register('fionawang12138.com', 'password', 'Fiona', 'Wang')

def test_register_email_taken():
    '''testing registration with taken email'''
    clear()
    auth_register('fionawang12138@gmail.com', 'password', 'Fiona', 'Wang')
    with pytest.raises(InputError):
        auth_register('fionawang12138@gmail.com', 'password', 'Bob', 'Smith')

def test_register_short_password():
    '''testing short password'''
    clear()
    with pytest.raises(InputError):
        auth_register('fionawang12138@gmail.com', 'llama', 'Fiona', 'Wang')
    with pytest.raises(InputError):
        auth_register('fionawang1@gmail.com', '123', 'Fiona', 'Wang')

def test_register_bad_first_name():
    '''testing long and shor first name'''
    clear()
    with pytest.raises(InputError):
        auth_register('fionawang12138@gmail.com', 'password', '', 'Wang')
    with pytest.raises(InputError):
        auth_register('fionawang1@gmail.com', 'password',
                      'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz', 'Wang')

def test_register_bad_last_name():
    '''testing long and short last name'''
    clear()
    with pytest.raises(InputError):
        auth_register('fionawang12138@gmail.com', 'password', 'Fiona', '')
    with pytest.raises(InputError):
        auth_register('fionawang1@gmail.com', 'password', 'Fiona',
                      'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz')

def test_login_this_should_work():
    '''testing return type for register function'''
    clear()
    auth_register('fionawang12138@gmail.com', 'password', 'Fiona', 'Wang')
    value = auth_login('fionawang12138@gmail.com', 'password')
    assert isinstance(value, dict) is True

def test_login_name_length_1():
    '''testing name length of 1'''
    clear()
    auth_register('fionawang@gmail.com', 'password', 'F', 'W')
    value = auth_login('fionawang@gmail.com', 'password')
    assert isinstance(value, dict) is True

def test_login_name_length_2():
    '''testing name length of 50'''
    clear()
    auth_register('fionawang@gmail.com', 'password',
                  'qwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiop',
                  'qwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiop')
    value = auth_login('fionawang@gmail.com', 'password')
    assert isinstance(value, dict) is True

def test_login_password_length_1():
    '''testing password of length 6'''
    clear()
    auth_register('fionawang@gmail.com', 'passwo', 'Fiona', 'Wang')
    value = auth_login('fionawang@gmail.com', 'passwo')
    assert isinstance(value, dict) is True

def test_login_wrong_email():
    '''testing loging in with wrong email'''
    clear()
    auth_register('fionawang12138@gmail.com', 'password', 'Fiona', 'Wang')
    with pytest.raises(InputError):
        auth_login('fionawang1213@gmail.com', 'password')

def test_login_no_account():
    '''logging in with no account should be a fail'''
    clear()
    with pytest.raises(InputError):
        auth_login('fionawang1213@gmail.com', 'password')

def test_login_wrong_password():
    '''testing loging in with existing account with wrong password'''
    clear()
    auth_register('fionawang12138@gmail.com', 'password', 'Fiona', 'Wang')
    with pytest.raises(InputError):
        auth_login('fionawang12138@gmail.com', 'password123')

def test_logout_success():
    '''testing successsful logout'''
    clear()
    auth_register('fionawang12138@gmail.com', 'password', 'Fiona', 'Wang')
    user_info = {}
    user_info = auth_login('fionawang12138@gmail.com', 'password')
    assert auth_logout(user_info.get('token')) == {
        'is_success': True,
    }

######################### test hash_password helper funciton ##################
def test_hash_password():
    """
    test that a hashed password is different from what it was before
    """
    password = 'iloveshrek!!!'
    hashed_password = hash_password(password)
    assert password != hashed_password

    hashed_password2 = hash_password(password)
    assert hashed_password == hashed_password2

def test_hash_password2():
    """
    Testing another hashed password
    """
    password = '123!!)0fwdjkW!'
    hashed_password = hash_password(password)
    assert password != hashed_password

    hashed_password2 = hash_password(password)
    assert hashed_password == hashed_password2

######################### test encode_token and decode_token helper funciton ##################
def test_encode_token():
    """
    tests that a decoded token is different from an unencoded token
    """
    token = 'fionawang12138@gmail.com_a'
    encoded_token = encode_token(token)
    assert encoded_token != token

def test_decode_token():
    """
    Tests that a decode_token function can work to decoded an encoded token
    """
    token = 'bobiscool@gmail.com_a'
    encoded_token = encode_token(token)
    assert encoded_token != token

    decoded_token = decode_token(encoded_token)
    assert token == decoded_token

######################### test check_decoded_token_validity ##################

def test_validity_active_check():
    """
    check that when a user is logged in, their token is valid
    """
    auth_register('fionawang@gmail.com', 'password', 'Fiona', 'Wang')
    token = auth_login('fionawang@gmail.com', 'password')['token']
    decoded_token = decode_token(token)
    assert check_decoded_token_validity(decoded_token) is True
    clear()

def test_valitidy_userdoesntexise_check():
    """
    test that a token that has not been registed is not valid
    """
    assert check_decoded_token_validity('idontexist@gmail.com_a') is False
    clear()

############################test password reset########################
def test_successful_reset_request():
    """
    test that when a registered user requests password reset, 
    the request is successful
    """
    auth_register('fionawang@gmail.com', 'password', 'Fiona', 'Wang')
    assert auth_passwordreset_request('fionawang@gmail.com') is not False
    clear()

def test_unsuccessful_reset_request():
    """
    test that when an unregistered user requests password reset, 
    the request is unsuccessful
    """
    assert auth_passwordreset_request('fionawang@gmail.com') is False
    clear()

def test_successful_reset():
    '''
    registering a new user, then reseting the password,
    testing that user can sign in with new password
    '''
    auth_register('fionawang@gmail.com', 'password', 'Fiona', 'Wang')
    reset_code = auth_passwordreset_request('fionawang@gmail.com')
    assert auth_passwordreset_reset(reset_code, 'bobsmith123') == {}
    value = auth_login ('fionawang@gmail.com', 'bobsmith123')
    assert isinstance(value, dict) is True
    clear()

def test_fail_reset_wrong_code():
    """
    test that when a wrong reset code is used, an error is raised
    """
    auth_register('bob@gmail.com', 'password', 'Fiona', 'Wang')
    auth_passwordreset_request('bob@gmail@gmail.com')
    with pytest.raises(InputError):
        auth_passwordreset_reset('bad_code', 'bobsmith123')
    clear()

def test_fail_rest_wrong_password():
    """
    test that when a bad password is used, an error is raised
    """
    auth_register('fionawang@gmail.com', 'password', 'Fiona', 'Wang')
    reset_code = auth_passwordreset_request('fionawang@gmail.com')
    with pytest.raises(InputError):
        auth_passwordreset_reset(reset_code, '123')
    clear()
