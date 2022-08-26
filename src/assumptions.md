Auth.py

1. There will be less than 1000 user on flocker with the exact same name

Channel.py
1. Assume that the given messages are ordered in a way where index[0] is the most recent message
2. Assume that removeowner will leave the previous owner as a member of the channel
3. A user can only join a channel once, i.e. there cannot be two members in a single channel with the same u_id 


Channels.py
1. Assume that the user who creates the channel is automatically the owner
2. Assume that channel  'name' cannot be 0 characters long
3. Assume that a user exists and has been successfully registered before a channel is created
4. Assume that an empty list is returned if channels_list/channels_listall is called and the user is not part of any channel or no channels have been created


Message.py
1. The maximum length of a message is <=1000. A message is too long if it exceeds 1000 characters (message length > 1000)
3. All characters in a message are ASCII
2. There won't be more than 10000 messages stored in a channel at any given time. (For message_id purposes)
3. For message_send, assume that both date and time of sent message is wanted
4. Assume that also message_edit follows the same input standards as message_send
5. For message_pin, the authorised user must be either an owner of the channel the message is within or an owner of the flockr
6. For message_unpin, the authorised user must be either an owner of the channel the message is within or an owner of the flockr


User.py
1. There will be a max of 1000 users of Flockr at a given time
2. Assume that setname will not accept names of 0 characters in length
3. Assume that given email is a legit email in real life.


