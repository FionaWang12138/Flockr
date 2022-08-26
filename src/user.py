""" FUNCTIONS FOR USER.PY """

import re
import urllib.request
from flask import request,url_for
from urllib.parse import urlparse
from pathlib import Path
from PIL import Image
from data import data
from error import AccessError, InputError
from auth import encode_token, decode_token, auth_register, auth_login


# Function decorator to check that a user is authorised.
def check_authorised_user(function):
    def wrapper(*args, **kwargs):
        if not check_token(decode_token(args[0])):
            raise AccessError("User is not authorised")
        else:
            return function(*args, **kwargs)
    return wrapper


@check_authorised_user
def user_profile(token, u_id):
    """
    For a valid user, returns information about their user_id, email,
    first name, last name, and handle.

    Args:
        token (string):
        u_id (int):

    Raises:
        InputError: When user with u_id is not a valid user.
        AccessError: When an invalid token is passed.

    Returns:
        dictionary: { user }

    """
    
    # Find the u_id of the authorised user.
    valid_user = None
    for users in data['users']:
        if u_id == users['u_id']:
            valid_user = users
            break
    if valid_user is None:
        raise InputError("u_id is not a valid user")

    # Return information for a valid user.
    user_info = {
        'u_id': valid_user['u_id'],
        'email': valid_user['email'],
        'name_first': valid_user['name_first'],
        'name_last': valid_user['name_last'],
        'handle_str': valid_user['handle'],
        'profile_img_url': valid_user['profile_img_url']
        }

    return {'user': user_info}


@check_authorised_user
def user_profile_setname(token, name_first, name_last):
    """
    Update the authorised user's first and last name.

    Args:
        token (string):
        name_first (string):
        name_last (string):

    Raises:
        InputError:
        - When name_first is not between 1 and 50 characters
            inclusively in length.
        - When name_last is not between 1 and 50 characters
            inclusively in length

        AccessError: When an invalid token is passed.

    Returns:
        {}

    """

    # Check that name_first and name_last are valid.
    if not check_valid_name(name_first):
        raise InputError("First name must be 1 to 50 characters inclusive")
    if not check_valid_name(name_last):
        raise InputError("Last name must be 1 to 50 characters inclusive")

    # Update the user's first and last name.
    for user in data['users']:
        if decode_token(token) == user['token']:
            user['name_first'] = name_first
            user['name_last'] = name_last
            break
    return {
    }

@check_authorised_user
def user_profile_setemail(token, email):
    """
    Update the authorised user's email address

    Args:
        token (string):
        email (string):

    Raises:
        InputError:
        - When the email entered is not a valid
        - When the email address is already being used by another user

        AccessError: When an invalid token is passed.

    Returns:
        {}

    """
    
    # Check that the email is valid.
    if not check_valid_email(email):
        raise InputError("The email you have entered is not valid")

    # Check that email has not been used by another user.
    for user in data['users']:
        if user['email'] == email:
            raise InputError("The email you are using already has an account")

    # Update the user's email
    for user in data['users']:
        if user['token'] == decode_token(token):
            user['email'] = email
            break
    return {
    }

@check_authorised_user
def user_profile_sethandle(token, handle_str):
    """a function that changes the handle of an authorised user

    Args:
        token (string):
        handle_str (string):

    Returns:
        nothing
    """
    
    if not check_valid_handle(handle_str):
        raise InputError("Please enter a valid handle.")

    for user in data['users']:
        if user['handle'] == handle_str:
            raise InputError("This handle is already in use, please choose a different one.")

    for user in data['users']:
        if user['token'] == decode_token(token):
            user['handle'] = handle_str
            break
    return {
    }

@check_authorised_user
def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    
    # Get the file name from the url.
    url = urlparse(img_url)
    file_name = Path(url.path).name

    # Check that image uploaded is a JPG.
    if not check_img_format(file_name):
        raise InputError("Image uploaded is not a JPG")

    # Download image to local directory.
    path_name = str(Path().absolute()) + "/src/static/" + file_name
    urllib.request.urlretrieve(img_url, path_name)

    profile_photo = Image.open(path_name)
    
    # Check that crop dimensions is within the image.
    if not check_crop_dimensions(profile_photo, x_start, y_start, x_end, y_end):
        raise InputError("Crop not within dimensions of image")
    
    # Crop the image.
    crop_img(profile_photo, path_name, x_start, y_start, x_end, y_end)

    return {}


########################### HELPER FUNCTIONS #############################

def check_valid_name(name):
    """
    Checks whether a given name is valid i.e. between 1 and 50 characters
    inclusively in length.

    Args:
        name (string):

    Returns:
        bool: True if name is valid, false if otherwise.

    """
    if 1 <= len(name) <= 50:
        return True
    return False

def check_valid_email(email):
    """
    Checks that an entered email is valid.

    Args:
        email (string):

    Returns:
        bool: True if email is valid, false if otherwise.
    """

    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if not re.search(regex, email):
        return False
    return True

def check_valid_handle(handle_str):
    """
    Checks whether a handle is between 3 and 20 characters long
    Args:
        handle_str (string):

    Returns:
        bool: True if handle_str is valid, false if otherwise.

    """
    if 3 <= len(handle_str) <= 20:
        return True
    return False

def check_token(token):
    """
    Checks whether the token is valid and returns true if so.

    Args:
        token (string):

    Returns:
        int: u_id
        bool:

    """
    for user in data['users']:
        if token == user['token'] and token.endswith('_a'):
            return True
    return False

def check_img_format(image):
    """
    Check that the img uploaded is a jpg.
    """
    return image.endswith(".jpg")

def check_crop_dimensions(image, x_start, y_start, x_end, y_end):
    """ 
    Check that the crop dimensions are valid given the dimensions of 
    the original image.
    """

    max_width, max_height = image.size
    if x_start < 0 or x_end > max_width or y_start < 0 or y_end > max_height:
        return False
    if x_start >= x_end or y_start >= y_end:
        return False
    return True

def crop_img(image, file_name, x_start, y_start, x_end, y_end):
    """ 
    Crop the image and save.
    """
    cropped = image.crop((x_start, y_start, x_end, y_end))
    cropped.save(file_name)
    return cropped


