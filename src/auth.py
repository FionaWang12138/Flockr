'''users registering, logging in and looing out'''
import re
import json
import hashlib
import jwt
from flask import Flask, request
from data import data
from error import InputError
import random
import string

def auth_login(email, password):
    '''
    a function which allows user to login given that they have an account and have corret email
    '''
    #check that the email is within data, and that email and password matches
    has_email = False
    password_match = False
    for user in data['users']:
        if user['email'] == email:
            has_email = True
            #if there's a match, get u_id and token
            if user['password'] == hash_password(password):
                password_match = True
                u_id = user['u_id']
                token = user['email'] + '_a'
                user['token'] = token #adding _a for activated token #change inactive token to active token

    if has_email is False:
        raise InputError("The email you have entered doesn't have an account.")
    if password_match is False:
        raise InputError("The password you entered doesn't match your email.")

    return {
        'u_id': u_id,
        'token': encode_token(token),
    }

def auth_logout(token):
    '''a function that lets user log out given an active token'''
    token = decode_token(token)
    is_valid_user = check_decoded_token_validity(token)
    if is_valid_user is True:

        for user in data['users']:
            if user['token'] == token:
                #making it an inactive token
                user['token'] = user['email'] + 'i'
        return {'is_success': True}

    return {'is_success': False}


def auth_register(email, password, name_first, name_last):
    '''allows user to regester for flockr'''
    #validating email address
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if not re.search(regex, email):
        raise InputError("Please enter a valid email adress.")

    #rejecting email that's already used
    for user in data['users']:
        if user['email'] == email:
            raise InputError("The email you are using already has an account")

    #rejecting invalid password
    if len(password) < 6:
        raise InputError("Please enter a password with 6 or more characters.")

    #rejecting names that are not between 1 and 50 characters
    if not (1 <= len(name_first) <= 50 and 1 <= len(name_last) <= 50):
        raise InputError("Please enter a first and last name between 1 and 50 characters each.")

    #creating a token, for iteration 1, the token is just the email
    #since the user hasn't logged in, '_i' means that the toke is not active
    token = email + '_a'

    #creating a handle
    handle = name_first.lower() + name_last.lower()

    #if handle is too long, only use the first 17 characters
    #since a max of 20 characters are allowed, this gives us 3 spaces to add
    #random numbers to make the handle unique if people have the same name
    if len(handle) > 17:
        handle = handle[0:17]

    #goes through all the users to see how many have the same name
    i = 0
    for user in data['users']:
        if user['handle'] == handle or user['handle'] == handle + str(i):
            i += 1

    #assign a number after the handle to make it unique
    handle = handle + str(i)

    #give user a unique id in order of registration
    u_id = 1
    for user in data['users']:
        if user['u_id'] == u_id:
            u_id += 1

    permission_id = 2
    if u_id == 1:
        permission_id = 1

    #hashing password to store securely
    hashed_password = hash_password(password)

    #create a dictionary with all the information about new user in it
    user = {'email' :email,
            'password' :hashed_password,
            'name_first' :name_first,
            'name_last' :name_last,
            'handle' :handle,
            'u_id' :u_id,
            'token' :token,
            'permission_id' :permission_id,
            'profile_img_url': None,
            'password_reset_code' : None
            }

    #append the new dictionary to the list of users inside the data dictionary
    data['users'].append(user)

    return {
        'u_id': u_id,
        'token': encode_token(token),
    }

def hash_password(password):
    """
    a funtion that hashes password for secure storing

    Args:
        password (str)

    Returns:
        hashed_password(str)
    """
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

def encode_token(uncoded_token):
    """
    a function that takes in an unencoded token and encodes

    Args:
        uncoded_token (str)

    Returns:
        encoded_jwt(str)
    """
    SECRET = 'hierODVRUVmCcBkl2qNE7Tk2Mkn7Tkl61nmQYzTz'

    encoded_jwt = jwt.encode({'token': uncoded_token}, SECRET, algorithm='HS256').decode('utf-8')
    return encoded_jwt

def decode_token(encoded_jwt):
    """
    a function that decodes an encoded token

    Args:
        encoded_jwt (str)

    Returns:
        token(str)
    """
    SECRET = 'hierODVRUVmCcBkl2qNE7Tk2Mkn7Tkl61nmQYzTz'
    decoded_jwt = jwt.decode(encoded_jwt.encode('utf-8'), SECRET, algorithms=['HS256'])
    token = decoded_jwt['token']
    return token

def check_decoded_token_validity(decoded_token):
    """
    checking the validity of a decoded token passed on
    to a function to make sure a user is logged in
    Args:
        encoded_token(str)

    Returns:
        is_valid_user (bool)
    """
    is_valid_user = False

    for user in data['users']:
        if user['token'] == decoded_token and user['token'].endswith('_a'):
            is_valid_user = True

    return is_valid_user

def auth_passwordreset_request(email):
    '''
    generate a random string to use for password reset only if user exists, and store it in the data dictionary
    returns reture reset_code is user's email is in use, return False otherwise
    '''

    letters = string.ascii_lowercase + string.ascii_uppercase
    reset_code = ''.join(random.choice(letters) for i in range(8))

    
    #making sure that the reset_code is unique
    while (reset_code in data['password_reset_codes']):
        reset_code = ''.join(random.choice(letters) for i in range(8))
    
    data['password_reset_codes'].append(reset_code)

    for user in data['users']:
        if user['email'] == email:
            user['password_reset_code'] = reset_code
            return reset_code
    return False

def auth_passwordreset_reset(reset_code, password):
    """
    Resets password if correct reset_code is given

    Args:
        reset_code (str)
        password ([str)

    Returns:
        empty dictionary
    """
    if len(password) < 6:
        raise InputError("Please enter a password with 6 or more characters.")
    
    valid_code = False

    for user in data['users']:
        if user['password_reset_code'] == reset_code:
            user['password_reset_code'] = None
            data['password_reset_codes'].remove(reset_code)
            user['password'] = hash_password(password)
            valid_code = True
            break

    if valid_code is False:
        raise InputError("The code you've entered is invalid.")
            
    return {}