"""
Functions that don't fit into certain categories
"""

from data import data
from error import InputError, AccessError
from auth import decode_token, check_decoded_token_validity
from channel import is_flockr_owner, user_reacted
import os
from pathlib import Path

def clear():
    """
    Clears the users and channels list within the dictionary, as well as
    deleting all the images saved in static.
    """

    data['users'].clear()
    data['channels'].clear()

    # Delete all images in the static folder.
    path = str(Path().absolute()) + "/src/static/"
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))

    return {}

def users_all(token):
    """
    Returns a list with all the users

    Args:
        token (str)

    Raises:
        AccessError: when the token given is invalid

    Returns:
        list containing all users
    """
    token = decode_token(token)

    if check_token(token) is False:
        raise AccessError("User is not authorised")

    list_of_users = []
    for user in data['users']:
        user_to_add = {'u_id': user['u_id'],
                       'email': user['email'],
                       'name_first': user['name_first'],
                       'name_last': user['name_last'],
                       'handle_str': user['handle'],
                       'profile_img_url': user['profile_img_url']
                       }
        list_of_users.append(user_to_add)

    return {'users': list_of_users}

def admin_userpermission_change(token, u_id, permission_id):
    """
    Changes the global permissions for a given user if the token correlates
    to a user with admin privileges

    Args:
        token (string):
        u_id integer:
        permission_id integer:

    Raises:
        InputError: When u_id does not correspond to a valid user
        InputError: When permission_id is not a valid value (either 1 or 2)
        AccessError: When the token passed in is not a valid token

    Returns:
        Empty dictionary: {}
    """

    # check for an authorised user
    auth_user = decode_token(token)
    auth_user_id = token_to_u_id(auth_user)

    if not check_decoded_token_validity(auth_user) or not is_flockr_owner(auth_user_id):
        raise AccessError("User is not authorised")

    # check for a valid user id
    if not valid_user_id(u_id):
        raise InputError("Please enter a valid user id")

    # check for a valid permission id
    if not valid_permission_id(permission_id):
        raise InputError("Please enter a valid permission id")

    # can now change the user's permissions
    for user in data["users"]:
        if user["u_id"] == u_id:
            user["permission_id"] = permission_id

    return {}

def search(token, query_str):
    """
    Given a query string, returns a list of messages that contain the
    query string from all of the channels that the user is a member of

    Args:
        token (string):
        query_str (string):

    Raises:
        AccessError: When the token passed in is not a valid token

    Returns:
        List: { messages }
    """

    # check for an authorised user
    new_token = decode_token(token)

    if not check_decoded_token_validity(new_token):
        raise AccessError("User is not authorised")

    user_id = token_to_u_id(new_token)

    message_list = []

    for channel in data["channels"]:
        if any(user_id == user['u_id'] for user in channel['all_members']):
            for message in channel["messages"]:
                if query_str in message["message"]:
                    message_id = message["message_id"]
                    sender_id = message["u_id"]
                    message_content = message["message"]
                    time_created = message["time_created"]
                    message_list.append({
                        'message_id': message_id,
                        'u_id': sender_id,
                        'message': message_content,
                        'time_created': time_created,
                        'reacts': user_reacted(message, user_id),
                    })

    return {'messages': message_list}


######################### Helper functions ############################

def valid_user_id(user_id):
    """
    Takes in a user id and determines if that user exists or not

    Args:
        user_id (integer):

    Returns:
        bool:

    """

    for user in data['users']:
        if user['u_id'] == user_id:
            return True
    return False

def user_is_admin(user_id):
    """
    Takes in a user id and determines if they are an admin or not

    Args:
        user_id (integer):

    Returns:
        bool:

    """

    for user in data["users"]:
        if user["u_id"] == user_id and user["permission_id"] == 1:
            return True
    return False

def valid_permission_id(permission_id):
    """
    Determines whether a permission id is valid or not

    Args:
        permission_id (integer):

    Returns:
        valid_id (bool):

    """
    if permission_id in (1, 2):
        return True
    return False

def token_to_u_id(token):
    """
    Given a token, return the user id of the owner of the token

    Args:
        token (string):

    Returns:
        u_id (integer):
    """

    for user in data["users"]:
        if user["token"] == token:
            return user["u_id"]
    return False

def check_token(token):
    """
    Checks whether the token is valid and returns true if so.

    Args:
        token (string):

    Returns:
        bool:

    """
    for user in data['users']:
        if token == user['token']:
            return True
    return False
