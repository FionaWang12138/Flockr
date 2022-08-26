""" FUNCTIONS FOR CHANNELS.PY """

from data import data
from error import InputError, AccessError
from auth import encode_token, decode_token, check_decoded_token_validity

def channels_list(token):
    """
    Provide a list of all channels (and their associated details)
    that the authorised user is part of

    Args:
        token (string):

    Raises:
        AccessError: When the token passed in is not a valid token.

    Returns:
        List: { channels }

    """
    token = decode_token(token)

    # Check that the user is authorised.
    authorised_user = check_token(token)
    if authorised_user is False:
        raise AccessError("User is not authorised")

    # Loop through data and find channels that the user is part of.
    channels = []
    for channel in data['channels']:
        for member in channel['all_members']:
            if authorised_user == member['u_id']:
                list_channel = {
                    'channel_id': channel['channel_id'],
                    'name': channel['name']
                }
                channels.append(list_channel)

    return {'channels': channels}

def channels_listall(token):
    """
    Provide a list of all channels (and their associated details).

    Args:
        token (string):

    Raises:
        AccessError: When the token passed in is not a valid token.

    Returns:
        List: { channels }

    """
    token = decode_token(token)

    # Check user is authorised.
    authorised_user = check_token(token)
    if authorised_user is False:
        raise AccessError("User is not authorised")

    channels = []
    for channel in data['channels']:
        list_channel = {
            'channel_id': channel['channel_id'],
            'name': channel['name']
        }
        channels.append(list_channel)

    return {'channels': channels}

def channels_create(token, name, is_public):
    """
    Creates a new channel with that name that is either a public or
    private channel.

    Args:
        token (string):
        name (string):
        is_public (bool):

    Raises:
        InputError: When name is more than 20 characters long.
        AccessError: When invalid token is passed.
    Returns:
        [type]: [description]
    """
    token = decode_token(token)

    if len(name) > 20:
        raise InputError("Invalid channel name. Name must not be "
                         "longer than 20 characters.")

    # Finds the user who is creating the channel and set that user
    # as the owner.
    owner = None
    for user in data['users']:
        if token == user['token']:
            owner = user
    # Token does not match with a user
    if owner is None:
        raise AccessError("User is not authorised")

    channel_id = int(len(data['channels']) + 1)

    standup = {
        'is_active': False,
        'time_finish': None,
        'messages': [],
    }

    channel = {
        'channel_id': channel_id,
        'name': name,
        'public': is_public,
        'owner_members': [owner],
        'all_members': [owner],
        'messages': [],
        'standup': standup,
    }

    data['channels'].append(channel)

    return {'channel_id': channel_id}

########################### HELPER FUNCTIONS #############################

def check_token(token):
    """
    Checks whether the token is valid and returns that user_id if so.

    Args:
        token (string):

    Returns:
        int: u_id
        bool:

    """
    for user in data['users']:
        if token == user['token']:
            return user['u_id']

    return False
