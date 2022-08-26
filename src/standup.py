"""
File that contains functions for standups
"""
import datetime as dt
import time
import threading
from data import data
from error import InputError, AccessError
from auth import decode_token
from channel import channel_valid_id, user_in_channel
from channels import check_token
from message import valid_message, message_send

def standup_start(token, channel_id, length):
    """
    Starts a standup in a given channel if the user is authorised
    and the channel exists

    Args:
        token (string):
        channel_id (integer):

    Raises:
        InputError: When channel_id does not correspond to a valid channel
        AccessError: When the token passed in is not a valid token

    Returns:
        Dictionary: {
            'time_finish': (integer):
        }
    """
    
    #decode token
    new_token = decode_token(token)
    
    # check for input and access errors
    u_id = check_token(new_token)
    if not u_id:
        raise AccessError("User is not authorised")

    if not channel_valid_id(channel_id):
        raise InputError("Please enter a valid channel id")

    if not user_in_channel(u_id, channel_id):
        raise AccessError("User is not in channel")

    if standup_active(token, channel_id)['is_active']:
        raise InputError("Standup is already active")

    if length < 0:
        raise InputError("Enter a valid length of time")

    # Find the time the message is created
    datentime = dt.datetime.now()
    time_created = time.mktime(datentime.timetuple())

    time_finish = time_created + length

    standup = threading.Timer(length, standup_end, [token, channel_id])
    standup.start()

    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            channel['standup']['is_active'] = True
            channel['standup']['time_finish'] = time_finish
            channel['standup']['messages'] = []
            

    return {
        'is_active': True,
        'time_finish': time_finish,
    }

def standup_end(*args):
    """
    Finishes a standup after the appropriate length of time has passed

    Args:
        token (string, args[0]):
        channel_id (integer, args[1]):

    Returns:
        Empty Dictionary: {}
    """

    standup_message = ''
    for channel in data['channels']:
        if channel['channel_id'] == args[1]:
            for msg in channel['standup']['messages']:
                standup_message = standup_message + msg['handle'] + ': ' + msg['message'] + '\n'
            channel['standup']['is_active'] = False
            channel['standup']['time_finish'] = None
            channel['standup']['messages'].clear()
            break
    message_send(args[0], args[1], standup_message)

    return {}

def standup_active(token, channel_id):
    """
    Determines whether a standup in a given channel is active if the user is authorised
    and the channel exists

    Args:
        token (string):
        channel_id (integer):
        length (integer):

    Raises:
        InputError: When channel_id does not correspond to a valid channel
        AccessError: When the token passed in is not a valid token

    Returns:
        Dictionary: {   
            'is_active': (boolean),
            'time_finish': (integer):
        }
    """

    token = decode_token(token)
    u_id = check_token(token)
    if not u_id:
        raise AccessError(description="User is not authorised")

    if not channel_valid_id(channel_id):
        raise InputError(description="Please enter a valid channel id")

    if not user_in_channel(u_id, channel_id):
        raise AccessError(description="User is not in channel")

    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            is_active = channel['standup']['is_active']
            time_finish = channel['standup']['time_finish']
    
    return {
        'is_active': is_active,
        'time_finish': time_finish,
    }

def standup_send(token, channel_id, message):
    """
    Sends a message to be buffered in a standup queue, given a standup is
    active and the user is authorised in the channel

    Args:
        token (string):
        channel_id (integer):
        message (string):

    Raises:
        InputError: When channel_id does not correspond to a valid channel
        InputError: When message length is more than 1000 characters
        InputError: When a standup is not currently active in the channel
        AccessError: When the token passed in is not a valid token

    Returns:
        Empty Dictionary {}
    """

    new_token = decode_token(token)
    u_id = check_token(new_token)
    if not u_id:
        raise AccessError(description="User is not authorised")

    if not channel_valid_id(channel_id):
        raise InputError(description="Please enter a valid channel id")

    if not user_in_channel(u_id, channel_id):
        raise AccessError(description="User is not in channel")

    if not valid_message(message):
        raise InputError(description="Message longer than 1000 characters")

    if not standup_active(token, channel_id)['is_active']:
        raise InputError(description="Standup not currently active")

    handle = u_id_to_handle(u_id)

    message_data = {
        'message': message,
        'handle': handle,
    }

    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            channel['standup']['messages'].append(message_data)
            
    
    return {}

########################### HELPER FUNCTIONS #############################

def u_id_to_handle(u_id):
    """
    Given a user id, returns that user's handle
    """

    for user in data['users']:
        if user['u_id'] == u_id:
            return user['handle']
    return False
