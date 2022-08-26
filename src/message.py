'''
Implementation of message functions
'''

import datetime
import time
import threading
from data import data
from error import InputError, AccessError
import channel as ch
from auth import decode_token
import other

# Global variable to return message_id from function called by timer
timer_message_id = 0

def message_send(token, channel_id, message):
    '''
    Takes a token, channel_id and message to store the message in the data structure.

    Raises an input error if the message is longer than 1000 characters
    Raises an access error if the user is not in the channel given by the channel_id

    Returns message_id
    '''
    # Check if message is valid
    if not valid_message(message):
        raise InputError("Message longer than 1000 characters")

    # Decode token
    new_token = decode_token(token)
    # Check access error
    user_id = ch.channel_valid_token(new_token)
    if not ch.user_in_channel(user_id, channel_id) and not ch.is_flockr_owner(user_id):
        raise AccessError('User not in given channel')

    # Find the time the message is created
    dt = datetime.datetime.now()
    timestamp = dt.replace(tzinfo=datetime.timezone.utc).timestamp()

    # Create dictionary with message, message_id and token of sender
    message_id = get_message_id(channel_id)
    message_data = {
        'message_id': message_id,
        'u_id': user_id,
        'message': message,
        'time_created': timestamp,
        'is_pinned': False,
        'reacts': [],
    }

    # Store message in data structure
    for channel in data['channels']:
        if channel_id == channel['channel_id']:
            channel['messages'].insert(0, message_data)
            break

    return {
        'message_id': message_id
    }

def message_remove(token, message_id):
    '''
    Function that takes a token and message id and removes message

    Raises an input error if the message (based on id) is no longer there
    Raises an access error if the user was not the one that sent the message
    and is not flockr owner or owner of this channel

    Returns an empty dictionary
    '''
    # Check that the message is still there
    channel_id = message_exist(message_id)
    if not channel_id:
        raise InputError('Message does not exist')

    # Decode token
    new_token = decode_token(token)
    #Check that user is authorized
    user_id = ch.channel_valid_token(new_token)
    if not ch.user_in_channel(user_id, channel_id):
        if not ch.owner_of_channel(user_id, channel_id):
            if not ch.is_flockr_owner(user_id):
                raise AccessError('User not authorized')

    # Remove given message
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            for message in channel['messages']:
                if message_id == message['message_id']:
                    channel['messages'].remove(message)
                    break
    return {}

def message_edit(token, message_id, message):
    '''
    Function that, given a message (by message_id), updates its text with new
    text. If the new text is an empty string, the message is deleted

    Raises an access error if the authorized user is not the original sender of
    the message and is not an owner of the channel nor flockr

    Returns an empty dictionary
    '''
    # Check the message exists
    channel_id = message_exist(message_id)

    # Check if message is valid
    if not valid_message(message):
        raise InputError("Message longer than 1000 characters")

    # Check the new text is not empty, remove message if it is
    if len(message) == 0:
        message_remove(token, message_id)
        return {}

    # Decode token
    new_token = decode_token(token)
    # Check that user is authorized
    user_id = ch.channel_valid_token(new_token)
    if not ch.user_in_channel(user_id, channel_id):
        if not ch.owner_of_channel(user_id, channel_id):
            if not ch.is_flockr_owner(user_id):
                raise AccessError('User not authorized')

    # Update message
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            for curr_message in channel['messages']:
                if curr_message['message_id'] == message_id:
                    curr_message['message'] = message
                    break
    return {}

def message_sendlater(token, channel_id, message, time_sent):
    '''
    Function that, given a channel_id, message and time, sends a message at the given
    time to the specified channel.

    Raises an input error if the channel_id is invalid, if the time given has already passed
    or if the message is more than 1000 characters.
    Raises an access error if the user is not a member of the specified channel.

    Returns the message_id of the new message
    '''
    global timer_message_id

    # Check if message is valid
    if not valid_message(message):
        raise InputError('Message longer than 1000 characters')

    # Check the channel ID is valid
    if not channel_exists(channel_id):
        raise InputError('Channel ID is invalid')

    # Decode token
    new_token = decode_token(token)
    # Check access error
    user_id = ch.channel_valid_token(new_token)
    if not ch.user_in_channel(user_id, channel_id):
        raise AccessError('User not in given channel')

    # Get date to calculate length for timer
    dt = datetime.datetime.now()
    timestamp = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
    
    # Convert input time to utc.
    dt_time_sent = datetime.datetime.fromtimestamp(time_sent)
    time_sent = dt_time_sent.replace(tzinfo=datetime.timezone.utc).timestamp()
    
    send_time = time_sent - timestamp
    
    # Check the time specified has not already passed
    if send_time < 0:
        raise InputError('Specified time has already passed')

    # Set up timer
    sendlater = threading.Timer(send_time, message_sendnow, [token, channel_id, message])
    sendlater.start()
    sendlater.join()

    return {
        'message_id': timer_message_id
    }

def message_pin(token, message_id):
    '''
    Function that, given a message id, pins the given message in the channel
    it is within for special display properties on the frontend

    Raises an input error if message_id is not valid or if the message is already pinned
    Raises an access error if the authorised user is not a member of the channel and either
    the owner or owner of the flockr

    Returns an empty dictionary
    '''
    # Check the message exists
    channel_id = message_exist(message_id)
    if not channel_id:
        raise InputError('Message does not exist')

    # Check the message is not already pinned
    if message_pinned(channel_id, message_id):
        raise InputError('Message already pinned')

    # Decode token
    new_token = decode_token(token)
    # Check that user is authorized
    user_id = ch.channel_valid_token(new_token)
    if not ch.user_in_channel(user_id, channel_id):
        raise AccessError('User is not a member of the channel')

    # Check the user is either flockr owner or channel owner
    if not ch.owner_of_channel(user_id, channel_id):
        if not ch.is_flockr_owner(user_id):
            raise AccessError('User not authorized')

    # Pin Message
    for channel in data['channels']:
        if channel_id == channel['channel_id']:
            for curr_message in channel['messages']:
                if message_id == curr_message['message_id']:
                    curr_message['is_pinned'] = True

    return {}

def message_unpin(token, message_id):
    '''
    Function that, given a message id, unpins the given message in the channel
    it is within

    Raises an input error if message_id is not valid or if the message is already pinned
    Raises an access error if the authorised user is not a member of the channel and either
    the owner or owner of the flockr

    Returns an empty dictionary
    '''
    # Check the message exists
    channel_id = message_exist(message_id)
    if not channel_id:
        raise InputError('Message does not exist')

    # Check the message is already pinned
    if not message_pinned(channel_id, message_id):
        raise InputError('Message is not pinned')

    # Decode token
    new_token = decode_token(token)
    # Check that user is authorized
    user_id = ch.channel_valid_token(new_token)
    if not ch.user_in_channel(user_id, channel_id):
        raise AccessError('User is not a member of the channel')

    # Check the user is either flockr owner or channel owner
    if not ch.owner_of_channel(user_id, channel_id):
        if not ch.is_flockr_owner(user_id):
            raise AccessError('User not authorized')

    # Unpin Message
    for channel in data['channels']:
        if channel_id == channel['channel_id']:
            for curr_message in channel['messages']:
                if message_id == curr_message['message_id']:
                    curr_message['is_pinned'] = False

    return {}

def message_react(token, message_id, react_id):
    '''
    Function to add a react to a message
        - Raises input error for non existing message with token not in same channel
        - Raises input error for invalid react id
        - Raises input error if message already has a react from same user
    Returns empty dictionary
    '''
    # Decode token
    token = decode_token(token)

    # Test that message_id is valid within one of the users channels, input error
    channel_id = message_exist(message_id)
    u_id = find_u_id(token)
    if not ch.user_in_channel(u_id, channel_id):
        raise  InputError('Invalid message_id')

    valid_id = 1 # Create a function
    # Check for valid react_id, input error
    if react_id is not valid_id:
        raise  InputError('Invalid react id')

    
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            for message in channel['messages']:
                if message['message_id'] == message_id:
                    # Test for message with message_id already contains an active react from the user
                    if already_react(u_id, message, react_id):
                        raise InputError('User already reacted to message')
                    update_react(message, react_id, u_id)
    return {}

def message_unreact(token, message_id, react_id):
    '''
    Given a message within a channel the authorised user is part of,
    remove a "react" to that particular message
        - Raises input error for non existing message with token not in same channel
        - Raises input error for invalid react id
        - Raises input error if message has not already a react from user
    Returns empty dictionary
    '''
    # Decode token
    token = decode_token(token)

    # Test that message_id is valid within one of the users channels, input error
    channel_id = message_exist(message_id)
    u_id = find_u_id(token)
    if not ch.user_in_channel(u_id, channel_id):
        raise  InputError('Invalid message_id')

    valid_id = get_valid_react_id()
    # Check for valid react_id, input error
    if react_id is not valid_id:
        raise  InputError('Invalid react id') 

    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            for message in channel['messages']:
                if message['message_id'] == message_id:
                    # Test that the message already has a reaction from user, input error
                    if not already_react(u_id, message, react_id):
                        raise InputError('User has not reacted to message')
                    remove_u_id_react(message, u_id, react_id)
                    break
    return {}

############# HELPER FUNCTIONS #############
def remove_u_id_react(message, u_id, react_id):
    '''
    Function to remove user from list of users that
    has reacted, with a certain react_id
    Returns true if succsesful, false otherwise
    '''
    for react in message['reacts']:
        if react_id == react['react_id']:
            react['u_ids'].remove(u_id)
            return True
    return False
    
def channel_exists(channel_id):
    '''
    Function to check if the channel_id exists and represents a valid channel
    '''
    for channel in data['channels']:
        if channel_id == channel['channel_id']:
            return True
    return False

def message_exist(message_id):
    '''
    Function to check if message (with message_id) exists
    Returns channel_id if it exists, False otherwise
    '''
    for channel in data['channels']:
        for message in channel['messages']:
            if message_id == message['message_id']:
                channel_id = channel['channel_id']
                return channel_id
    return False

def valid_message(message):
    '''
    Takes in a message and counts the number of characters
    Returns False if number of characters is above 1000, otherwise True
    '''
    if len(message) > 1000:
        return False
    return True

def get_message_id(channel_id):
    '''
    Takes in a channel_id and returns a new, unique message_id
    '''
    # Counts the number of messages and adds 1 to the count to create an id
    for channel in data['channels']:
        if channel_id == channel['channel_id']:
            # when there are other messages in the channel
            if len(channel['messages']) != 0:
                return channel['messages'][0]['message_id'] + 1

    # when there are no other messages in the channel
    num_channels = len(data['channels'])
    return num_channels * 10000

def message_pinned(channel_id, message_id):
    '''
    Function to check if message with message_id is pinned or not
    Returns a boolean true or false
    '''
    for channel in data['channels']:
        if channel_id == channel['channel_id']:
            for message in channel['messages']:
                if message_id == message['message_id']:
                    return message['is_pinned']

    return False

def message_sendnow(*args):
    '''
    Function that executes upon sendlater reaching the time to be sent.
    Simply sends a message to the given channel now that the time has arrived.
    '''
    global timer_message_id
    timer_message_id = message_send(args[0], args[1], args[2])['message_id']

    return {}

def find_u_id(token):
    '''
    Function to find the user id based on the token
    Returns user_id if it exists, false if not
    '''
    for user in data['users']:
        if token == user['token']:
            return user['u_id']
    return False

def already_react(u_id, message, react_id):
    '''
    Function to check if the user has already reacted to message
    Returns True if user has, and false otherwise
    '''
    for react in message['reacts']:
        if react_id == react['react_id']:
            if u_id in react['u_ids']:
                return True
    return False

def get_message_react(message_id):
    '''
    Function to get message react
    Returns the react dictionary
    False, if the message does not exist
    '''
    for channel in data['channels']:
        for message in channel['messages']:
            if message_id in message:
                return message['reacts']
    return False

def update_react(message, react_id, u_id):
    '''
    Function to update a react
    Returns True if succsesful
    '''
    if not bool(message['reacts']):
        react = {
            'react_id': react_id,
            'u_ids': [u_id]
        }
        message['reacts'].append(react)
        return True
    for react in message['reacts']:
        if react_id == react['react_id']:
            react['u_ids'].append(u_id)
            return True
        else:
            react = {
                'react_id': react_id,
                'u_ids': [u_id]
            }
            message['reacts'].append(react)
            return True
    return False

def get_valid_react_id():
    '''
    Function to get a valid react id
    Returns id
    '''
    valid_id = 1
    return valid_id
