""" FUNCTION WRAPPERS FOR FLASK SERVER """

import sys
import channel as ch
import user
import other
import os
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from error import InputError, AccessError
from pathlib import Path
from auth import auth_register, auth_login, auth_logout, decode_token, auth_passwordreset_request, auth_passwordreset_reset
from channels import channels_create, channels_list, channels_listall
from message import message_send, message_remove, message_edit, message_pin, message_unpin, message_sendlater, message_react, message_unreact
import user
import other
import standup
from data import data
from urllib.parse import urlparse
from flask_mail import Message, Mail

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__, static_url_path='/static/')
CORS(APP)

APP.config['STATIC'] = str(Path().absolute()) + "/src/static/"

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })




########################## AUTH ROUTES ###################################


@APP.route('/auth/register', methods=['POST'])
def register_flask():
    """
    Wrapping the registration function in a flask server

    Returns:
        dictionary: [user information]
    """
    user_info = request.get_json()

    returns = auth_register(user_info['email'], user_info['password'],
                            user_info['name_first'], user_info['name_last'])
    return dumps(returns)


@APP.route('/auth/login', methods=['POST'])
def login_flask():
    """
    Wrapping the login function in a flask server

    Returns:
        dictionaty : [dictionary contains user's u_id and token]
    """
    user_info = request.get_json()

    returns = auth_login(user_info['email'], user_info['password'])
    return dumps(returns)


@APP.route('/auth/logout', methods=['POST'])
def logout_flask():
    """
    Wrapping the logout function in a flask server

    Returns:
        bool: [if login is successful]
    """

    user_info = request.get_json()

    returns = auth_logout(user_info['token'])
    return dumps(returns)

#configeration for mail
APP.config['MAIL_SERVER'] = 'smtp.gmail.com'
APP.config['MAIL_PORT'] = 465
APP.config['MAIL_USE_TLS'] = False
APP.config['MAIL_USE_SSL'] = True
APP.config['MAIL_DEBUG'] = True
APP.config['MAIL_USERNAME'] = 'thur01mangoteam5@gmail.com'
APP.config['MAIL_PASSWORD'] = 'Shrek123!'

mail = Mail(APP)

@APP.route('/auth/passwordreset/request', methods=['POST'])
def index():
    """
    sends an email to user with secret code for password reset

    Returns:
        empty dictionary
    """
    email = request.get_json()['email']


    if auth_passwordreset_request(email) is not False:
        msg = Message('Reset Code', sender='thur01mangoteam5@gmail.com', recipients=[email])
        msg.body = "Your password reset code for Flockr is: " + auth_passwordreset_request(email)
        mail.send(msg)
    return {}

@APP.route('/auth/passwordreset/reset', methods=['POST'])
def password_reset():
    """
    resets password if a correct code is entered

    Returns:
        empty dictionary
    """
    reset_info = request.get_json()
    returns = auth_passwordreset_reset(reset_info['reset_code'], reset_info['new_password'])
    return dumps(returns)



######################## CHANNEL ROUTES ##################################

@APP.route('/channel/details', methods=['GET'])
def server_channel_details():
    """
    Wrapper for channel_details function

    Returns:
        Dictionary: {
            channel_name (string),
            all_members (list),
            owner_members (list)
        }
    """

    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    channel_det = ch.channel_details(token, channel_id)
    return dumps(channel_det)

@APP.route('/channel/invite', methods=['POST'])
def server_channel_invite():
    """
    Wrapper for channel_invite function

    Returns:
        Empty dictionary
    """

    details = request.get_json()
    invite = ch.channel_invite(details["token"], int(details["channel_id"]), 
                                    int(details["u_id"]))
    return dumps(invite)

@APP.route('/channel/leave', methods=['POST'])
def server_channel_leave():
    """
    Wrapper for channel_leave function

    Returns:
        Empty dictionary
    """
    details = request.get_json()
    leave = ch.channel_leave(details["token"], int(details["channel_id"]))
    return dumps(leave)

@APP.route('/channel/join', methods=['POST'])
def server_channel_join():
    """
    Wrapper for channel_join function

    Returns:
        Empty dictionary
    """
    details = request.get_json()
    join = ch.channel_join(details["token"], int(details["channel_id"]))
    return dumps(join)

@APP.route('/channel/addowner', methods=['POST'])
def server_channel_addowner():
    """
    Wrapper for channel_addowner function

    Returns:
        Empty dictionary
    """
    details = request.get_json()
    addowner = ch.channel_addowner(details["token"], 
                        int(details["channel_id"]), int(details["u_id"]))
    return dumps(addowner)

@APP.route('/channel/removeowner', methods=['POST'])
def server_channel_removeowner():
    """
    Wrapper for channel_removeowner
    Returns:
        Empty dictionary
    """
    details = request.get_json()
    removeowner = ch.channel_removeowner(details['token'], 
                        int(details['channel_id']), int(details['u_id']))
    return dumps(removeowner)

@APP.route('/channel/messages', methods=['GET'])
def server_channel_messages():
    """
    Wrappper for channel_messages
    Returns = {
        'start':
        'end':
        'messages': []
    }
    """
    
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))

    channel_messages = ch.channel_messages(token, channel_id, start)
    return dumps(channel_messages)

######################## CHANNELS ROUTES #################################


@APP.route('/channels/list', methods=['GET'])
def server_listchannel():
    """
    Wrapper for channels_list function.

    Returns:
        list: list of channels that authorised user is part of.
    """
    user_token = request.args.get('token')
    channels = channels_list(user_token)
    return dumps(channels)


@APP.route('/channels/listall', methods=['GET'])
def server_listallchannels():
    """
    Wrapper for channels_listall function.

    Returns:
        list: list of all channels.
    """
    user_token = request.args.get('token')
    channels_all = channels_listall(user_token)
    return dumps(channels_all)


@APP.route('/channels/create', methods=['POST'])
def server_createchannel():
    """
    Wrapper for channels_create function.

    Returns:
        int: channel_id of the created channel.
    """
    channel_data = request.get_json()
    channel_id = channels_create(channel_data['token'], channel_data['name'],
                                 channel_data['is_public'])
    return dumps(channel_id)


######################## MESSAGE ROUTES ##################################

@APP.route('/message/send', methods=['POST'])
def server_message_send():
    """
    Wrapper for message_send function

    Returns:
        message_id
    """
    details = request.get_json()
    message_id = message_send(details['token'], int(details['channel_id']), 
                                details['message'])
    return dumps(message_id)

@APP.route('/message/remove', methods=['DELETE'])
def server_message_remove():
    """
    Wrapper for message_remove function

    Returns:
        Empty dictionary
    """
    details = request.get_json()
    remove = message_remove(details['token'], details['message_id'])
    return dumps(remove)

@APP.route('/message/edit', methods=['PUT'])
def server_message_edit():
    """
    Wrapper for message_edit function

    Returns:
        Empty dictionary
    """
    details = request.get_json()
    edit = message_edit(details['token'], details['message_id'], details['message'])
    return dumps(edit)

@APP.route('/message/pin', methods=['POST'])
def server_message_pin():
    """
    Wrapper for message_pin function

    Returns:
        Empty dictionary
    """
    details = request.get_json()
    pin = message_pin(details['token'], details['message_id'])
    return dumps(pin)

@APP.route('/message/unpin', methods=['POST'])
def server_message_unpin():
    """
    Wrapper for message_unpin function

    Returns:
        Empty dictionary
    """
    details = request.get_json()
    unpin = message_unpin(details['token'], details['message_id'])
    return dumps(unpin)

@APP.route('/message/sendlater', methods=['POST'])
def server_message_sendlater():
    """
    Wrapper for message sendlater

    Returns:
        message_id
    """
    details = request.get_json()
    sendlater = message_sendlater(details['token'], int(details['channel_id']), 
                                details['message'], int(details['time_sent']))
    return dumps(sendlater)

@APP.route('/message/react', methods=['POST'])
def server_message_react():
    """
    Wrapper for message_react function

    Returns:
        Empty dictionary
    """ 
    details = request.get_json()
    react = message_react(details['token'], int(details['message_id']), int(details['react_id']))
    return dumps(react)

@APP.route('/message/unreact', methods=['POST'])
def server_message_unreact():
    """
    Wrapper for message_unreact function

    Returns:
        Empty dictionary
    """ 
    details = request.get_json()
    unreact = message_unreact(details['token'], int(details['message_id']), int(details['react_id']))
    return dumps(unreact)

######################### USER ROUTES ####################################

@APP.route('/user/profile', methods=['GET'])
def server_user_profile():
    """
    Wrapper for user_profile function.

    Returns:
        dict: information about their user_id, email, first name,
                last name, and handle
    """

    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    profile = user.user_profile(token, u_id)
    return dumps(profile)

@APP.route('/user/profile/setname', methods=['PUT'])
def server_user_set_name():
    """
    Wrapper for user_profile_setname function.

    Returns: {}
    """

    profile = request.get_json()
    user.user_profile_setname(profile['token'], profile['name_first'],
                              profile['name_last'])
    return {
    }

@APP.route('/user/profile/setemail', methods=['PUT'])
def server_user_set_email():
    """
    Wrapper for user_profile_setemail function.

    Returns: {}
    """

    profile = request.get_json()
    user.user_profile_setemail(profile['token'], profile['email'])
    return {
    }


@APP.route('/user/profile/sethandle', methods=['PUT'])
def server_sethandle():
    """
    Wrapper for user_profile_sethandle function.

    """
    input_info = request.get_json()
    user.user_profile_sethandle(input_info['token'], input_info['handle_str'])

    return {
    }


@APP.route('/static/<path:path>')
def send_file(path):
    """ 
    Send an image from the local static folder to the server.
    """
    return send_from_directory(APP.config['STATIC'], path)


@APP.route('/user/profile/uploadphoto', methods=['POST'])
def server_uploadphoto():
    """
    Server route to upload a profile photo, given an image url off the
    internet, crops the image and generates a new img url for the server.
    """
    
    profile = request.get_json()
    
    # Crop the image.
    user.user_profile_uploadphoto(profile['token'], profile['img_url'], 
                        int(profile['x_start']), int(profile['y_start']), 
                        int(profile['x_end']), int(profile['y_end']))
    
    # Send the file to the server.
    file_name = get_filename(profile['img_url'])
    send_file(file_name) 
    
    # Generate a url for the cropped image.
    profile_img_url = request.url_root + 'static/' + file_name
    
    # Set the user's profile_img_url.
    for users in data['users']:
        if users['token'] == decode_token(profile['token']):
            users['profile_img_url'] = profile_img_url
            break
        
    return {}


######################### STANDUP ROUTES ###################################

@APP.route('/standup/start', methods=['POST'])
def server_standup_start():
    """
    Wrapper for standup_start function
    """
    details = request.get_json()
    start = standup.standup_start(details["token"], int(details["channel_id"]), int(details['length']))

    return dumps(start)


@APP.route('/standup/active', methods=['GET'])
def server_standup_active():
    """
    Wrapper for standup_active function
    """
    token = request.args.get("token")
    channel_id = request.args.get("channel_id")
    active = standup.standup_active(token, int(channel_id))

    return dumps(active)

@APP.route('/standup/send', methods=['POST'])
def server_standup_send():
    """
    Wrapper for standup_send function
    """
    details = request.get_json()
    send = standup.standup_send(details["token"], int(details["channel_id"]), 
                                details["message"])

    return dumps(send)


######################### OTHER ROUTES ###################################

@APP.route('/clear', methods=['DELETE'])
def server_clear():
    """
    Wrapper for clear function.

    Returns:
        Empty dictionary
    """

    clear_all = other.clear()
    return dumps(clear_all)

@APP.route('/users/all', methods=['GET'])
def server_user_all():
    """
    Wrapper for users_all function.

    Returns:
        list: containing dictionary of individual users with information
        about their user_id, email, first name, last name, and handle
    """

    token = request.args.get('token')
    all_users = other.users_all(token)
    return dumps(all_users)

@APP.route('/admin/userpermission/change', methods=['POST'])
def server_admin_userpermission_change():
    """
    Wrapper for admin_userpermission_change function

    Returns:
        Empty dictionary
    """

    details = request.get_json()
    perm_change = other.admin_userpermission_change(details["token"], details["u_id"],
                                                    details["permission_id"])
    return dumps(perm_change)

@APP.route('/search', methods=['GET'])
def server_search():
    """
    Wrapper for search function

    Returns:
        List [ messages{
            "message_id": ,
            "u_id": ,
            "message": ,
            "time_created": ,
        }]
    """

    token = request.args.get('token')
    query_str = request.args.get('query_str')
    search = other.search(token, query_str)
    return dumps(search)


######################## HELPER FUNCTIONS ################################

def get_filename(url):
    url = urlparse(url)
    return Path(url.path).name

def clear_static():
    """
    Delete all images in the static folder when the server ends.
    """
    path = str(Path().absolute()) + "/src/static/"
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))


if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
    
    # Delete all images in static folder when the server ends. 
    clear_static()
