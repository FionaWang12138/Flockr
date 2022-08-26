"""
Implementation for the channel functions for flockr.
"""

from data import data
from error import InputError, AccessError
from auth import decode_token

def channel_invite(token, channel_id, u_id):
    """
    Takes in a user's access token, a channel id and a user id
    and adds that user as a member of that channel.

    Raises an input error if either the channel id or the user id
    do not exist, i.e. they are invalid.
    Raises an access error if the access token is for a user who does
    not belong to the channel with channel id.

    Returns an empty dictionary upon successfully adding the user
    to the channel.
    """
    token = decode_token(token)
    # check for a valid channel id
    if not channel_valid_id(channel_id):
        raise InputError("Please enter a valid channel id")
    # check for a valid user id
    if not valid_user_id(u_id):
        raise InputError("Please enter a valid user id")

    # check the user trying to invite someone is a member of the channel
    auth_user_id = channel_valid_token(token)
    if not auth_user_id or not user_in_channel(auth_user_id, channel_id):
        raise AccessError("User is not authorised")

    # if the person being invited is already a member of the channel, do nothing
    for channel in data['channels']:
        if channel['channel_id'] == channel_id and u_id in channel['all_members']:
            return {}

    invited_user = None
    for user in data['users']:
        if u_id == user['u_id']:
            invited_user = user
            break

    # Now the user can be added as a member to a channel.
    # Since everything else was valid, this loop will always add a member
    # to the channel
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            channel['all_members'].append(invited_user)
            break
    return {}


def channel_details(token, channel_id):
    """
    Takes in a user's access token and a channel id and returns
    details about that channel.

    Raises an input error if either the channel id does not exist,
    i.e. it is invalid.
    Raises an access error if the access token is for a user who does
    not belong to the channel with channel id.

    Returns a dictionary containing the channel name, a list of channel
    members and a list of channel owners.

    """
    token = decode_token(token)
    # check for a valid channel id
    if not channel_valid_id(channel_id):
        raise InputError("Please enter a valid channel id")

    # check the user trying to check the details is a member of the channel
    auth_user_id = channel_valid_token(token)
    if not auth_user_id or not user_in_channel(auth_user_id, channel_id):
        raise AccessError("User is not a member of this channel")

    # find the channel and extract the required details
    owner_members = []
    all_members = []
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            name = channel['name']

            for members in channel['owner_members']:
                member = {
                    'u_id': members['u_id'],
                    'name_first': members['name_first'],
                    'name_last': members['name_last'],
                    'profile_img_url': members['profile_img_url'],
                }
                owner_members.append(member)


            for members in channel['all_members']:
                member = {
                    'u_id': members['u_id'],
                    'name_first': members['name_first'],
                    'name_last': members['name_last'],
                    'profile_img_url': members['profile_img_url'],
                }
                all_members.append(member)

    return {
        'name' : name,
        'owner_members' : owner_members,
        'all_members' : all_members
    }

def channel_messages(token, channel_id, start):
    """
    Function that is given a start value to find up to 50 messages, between the start value
    and start + 50. It does this in the channel corresponding to the channel_id it is given,
    if the user with the token is authorized.

    Raises an input error if the given channel_id is invalid.
    Raises an input error if the given start value is not valid.
    Raises an access error if acces token does not belong to the channel.

    Returns a dictionary with start, end, and a list of all the messages.
    """
    token = decode_token(token)

    # Check for invalid channel
    if not channel_valid_id(channel_id):
        raise InputError("Invalid Channel ID")

    # Check for invalid start value, negative, not numeric and start greater than total messages
    # Count total messages
    total_messages = 0
    for channel in data["channels"]:
        if channel["channel_id"] == channel_id:
            total_messages = len(channel["messages"])
            break

    # Check for invalid start value
    if start < 0 or start > total_messages:
        raise InputError("Invalid start value")

    # Check for authorised user
    auth_user_id = channel_valid_token(token)
    if not auth_user_id or not user_in_channel(auth_user_id, channel_id):
        raise AccessError("User is not authorised")

    # Create a new dictionary that holds the start, end, and a list
    # of the messages including all the details
    messages_list = []
    count = -1                  # Counts all messages, included those outside the index
    messages_count = 0          # Counts only messages within the index
    for channel in data["channels"]:
        if channel["channel_id"] == channel_id:
            for message in channel["messages"]:
                count += 1
                if count >= start and message is not None:
                    if messages_count == 50:
                        break
                    messages_count += 1
                    mock_message = message
                    mock_message['reacts'] = user_reacted(mock_message, auth_user_id)
                    messages_list.append(mock_message)

    # Find end of index
    end = start + messages_count

    # If end of messages is reached, end is -1
    if count + 1 == messages_count:
        end = -1

    return {
        'messages': messages_list,
        'start': start,
        'end': end,
    }

def channel_leave(token, channel_id):
    """
    Takes in a user's access token and a channel id. Removes the user as a
    member of the channel.

    Raises an input error if the channel ID is not a valid channel.
    Raises an access error if the access token is for a user who does
    not belong to the channel with channel id.

    Returns nothing.
    """
    token = decode_token(token)

    # Check the channel ID is valid
    if not channel_valid_id(channel_id):
        raise InputError("Invalid Channel ID")

    # Obtain user ID
    u_id = channel_valid_token(token)

    # Check the user belongs to the channel
    if not user_in_channel(u_id, channel_id):
        raise AccessError("Current user is not a member of channel")

    # Remove the user from the channel
    for channel in data["channels"]:
        if channel["channel_id"] == channel_id:
            for user in channel["all_members"]:
                if user['u_id'] == u_id:
                    channel['all_members'].remove(user)
    return {}

def channel_join(token, channel_id):
    """
    Takes in a user's access token and a channel id. Adds the member to
    the given channel.

    Raises an input error if the channel ID is not a valid channel.
    Raises an access error when the given channel is private and the user
    is not a global owner.

    Returns nothing.
    """
    token = decode_token(token)
    # Check the channel ID is valid
    if not channel_valid_id(channel_id):
        raise InputError("Invalid Channel ID")

    # Obtain user ID
    u_id = channel_valid_token(token)

    # Check the given token is valid
    if not u_id:
        raise InputError("Invalid token")

    # Check the channel is public or the user is a global owner
    if not is_flockr_owner(u_id):
        if not channel_ispublic(channel_id):
            raise AccessError("Channel is private")

    joining_user = None
    for user in data['users']:
        if token == user['token']:
            joining_user = user
            break

    # Add the user to the channel
    for channel in data["channels"]:
        if channel["channel_id"] == channel_id:
            channel["all_members"].append(joining_user)
            break
    return {}

def channel_addowner(token, channel_id, u_id):
    """
    Takes in a user's access token and a channel id and returns
    details about that channel.

    Raises an input error if:
        - the channel ID is not a valid channel.
        - the user (given by u_id) is already an owner of the channel.
    Raises an access error if the authorised user is not of owner of this
    channel nor a global owner.

    Returns nothing.
    """
    token = decode_token(token)

    # Check the channel ID is valid
    if not channel_valid_id(channel_id):
        raise InputError("Invalid Channel ID")

    # Obtain ID of authorised user
    owner_id = channel_valid_token(token)

    # check the u_id given is valid
    if not valid_user_id(u_id):
        raise InputError("Invalid u_id")

    # Check the authorised user is a channel owner or global owner
    if not owner_of_channel(owner_id, channel_id) and not is_flockr_owner(owner_id):
        raise AccessError("Current user is not a flockr nor channel owner")

    for user in data['users']:
        if user['u_id'] == u_id:
            add_user = user
            break

    # Add the given user as an owner of the channel
    for channel in data["channels"]:
        if channel["channel_id"] == channel_id:

            # Check the given user is not already an owner of the channel
            if add_user in channel["owner_members"]:
                raise InputError("User is already an owner of the channel")

            # Add given user as owner
            channel["owner_members"].append(add_user)
            channel["all_members"].append(add_user)
    return {}

def channel_removeowner(token, channel_id, u_id):
    """
    Takes in a users access token, channel_id and the u_id of the owner to be removed.

    Raises an input errro if the channel_id is invalid
    Raises an input error if the u_id to be removed is not an owner
    Raises an access error if the users access token is not an owner of the channel
    nor a global owner the flockr

    Returns nothing.
    """
    new_token = decode_token(token)

    # Check for invalid channel
    if not channel_valid_id(channel_id):
        raise InputError("Invalid Channel ID")

    # Checks that user is an owner of the channel or flockr
    owner_id = channel_valid_token(new_token)
    if not owner_of_channel(owner_id, channel_id) and not is_flockr_owner(owner_id):
        raise AccessError("Access Error")

    # Check for invalid owner
    if not owner_of_channel(u_id, channel_id):
        raise InputError("User is not owner of channel")

    # Go through the data directory and remove owner
    for channel in data["channels"]:
        if channel["channel_id"] == channel_id:
            for owner in channel["owner_members"]:
                if owner['u_id'] == u_id:
                    channel["owner_members"].remove(owner)
                    break
    return {}

########################### HELPER FUNCTIONS #############################

def user_reacted(message, auth_user_id):
    '''
    Function to check if user has already reacted to message
    Returns a list of react dictionaries
    '''
    list_of_reacts = []
    if not bool(message['reacts']):
        react_dict = {
            'react_id': 1,
            'u_ids': [],
            'is_this_user_reacted': False,
        }
        list_of_reacts.append(react_dict)
    else:
        for react in message['reacts']:
            react_dict = {
                'react_id': react['react_id'],
                'u_ids': react['u_ids'],
                'is_this_user_reacted': auth_user_id in react['u_ids'],
            }
            list_of_reacts.append(react_dict)
    
    return list_of_reacts

def valid_user_id(user_id):
    """
    Takes in a user id and determines if that user exists or not

    Returns true if user exists and false otherwise
    """

    for user in data['users']:
        if user['u_id'] == user_id:
            return True
    return False

def channel_valid_id(channel_id):
    """
    Takes in a channel id and determines if that channel exists or not

    Returns true if channel exists and false otherwise
    """

    for channel in data['channels']:
        if channel_id == channel['channel_id']:
            return True
    return False

def channel_valid_token(token):
    """
    Takes in an access token and determines if it corresponds to an actual user

    Returns user_id if user exists and false otherwise
    """

    for user in data['users']:
        if token == user['token']:
            return user['u_id']
    return False

def user_in_channel(u_id, channel_id):
    """
    Takes in a user id and a channel id and determines whether
    that user is a member of the channel

    Returns true if user is a member and false otherwise
    """

    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            for member in channel['all_members']:
                if member['u_id'] == u_id:
                    return True
    return False

def owner_of_channel(u_id, channel_id):
    """
    Takes in a user id and a channel id and determines whether
    that user is an owner of the channel

    Returns true if user is an owner and false otherwise
    """

    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            for user in channel['owner_members']:
                if user['u_id'] == u_id:
                    return True
    return False

def is_flockr_owner(u_id):
    """
    Takes in a user id and determines whether
    that user is an owner of the flockr

    Returns true if user is an owner and false otherwise
    """

    for user in data["users"]:
        if user["u_id"] == u_id and user["permission_id"] == 1:
            return True
    return False

def channel_ispublic(channel_id):
    """
    Takes in a channel id and determines whether
    that channel is public or private

    Returns true if channel is public and false otherwise
    """

    for channel in data["channels"]:
        if channel["channel_id"] == channel_id:
            return channel["public"]
    return False
