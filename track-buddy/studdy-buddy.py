"""
Track Buddy

The track buddy automates the adding of techies to the Track channels, and creates Track Buddy Groups, which are
composed by techies of the same (main) track
"""

import sys

import logging
import pandas as pd

import pyfiglet
from slack import WebClient, errors


__author__ = "Andres David Vega Botero"
__email__ = "andresvegabotero@gmail.com"


def terminal_intro(title):
    """
    Create a Title using pyfiglet
    Args:
        title (str): the title of the Script
    """
    print("{:_^61}".format("_"))
    ascii_banner = pyfiglet.figlet_format(title)
    print(ascii_banner)
    print("{:^61}".format("By {}".format(__author__)))
    print("{:_^61}".format("_"))
    print()


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    taken from: http://code.activestate.com/recipes/577058/

    Args:
        question (str): The question to show to the user
        default (str): default answer (if user does not provide an answer)

    Returns:
        bool: True if 'Yes' False if 'No'
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


class BuddyGroup:
    """
    Buddy Group
    """

    def __init__(self, suffix, track, members):
        self.members = members
        self.size = len(members)
        self.slack_id = ''
        # Set Track
        self.track = track
        # Set the Name
        self.name = "{}-{}-{}".format(cfg['buddy groups']['prefix'], track, suffix).lower()


class SlackClient(WebClient):
    """
    Connection Manager to the Slack API
    """
    users = []
    channels = []

    def __init__(self, bot_token):
        """
        Class constructor
        Args:
            bot_token: XOXB token found under oauth & Permissions
        """
        # Connection
        super().__init__(token=bot_token)
        # List Users and Channels
        self.update_users()
        self.update_channels()

    def update_users(self):
        """
        Call the user.list from the SLack API and save the channels under self.users
        Returns:
            list: user list
        """
        self.users = self.users_list()['members']
        logging.info("Users found = {}".format(len(self.users)))
        return self.users

    def add_to_channel(self, slack_user_id, slack_channel_id):
        """
        Add the user with the given id to the channel to the given id using the Slack API conversations.invite

        The bot has to be part of the Channel
        Args:
            slack_user_id (str): User ID in Slack
            slack_channel_id (str): Channel ID in slack

        Returns:
            SlackResponse: response form the API
        """
        return self.conversations_invite(channel=slack_channel_id, users=[slack_user_id])

    def update_channels(self):
        """
        Call the Conversations.list from the SLack API and save the channels under self.channels
        Returns:
            list: channel list
        """
        self.channels = self.conversations_list(types="public_channel, private_channel")['channels']
        logging.info("Channels found = {}".format(len(self.channels)))
        return self.channels

    def add_slack_id_to_df(self, data_frame, email_column):
        """
        Will add a new Column to the data frame, and will attempt to fill it with the user IDs in self.users
        Args:
            data_frame (pandas.DataFrame): input Data Frame
            email_column (str): Title of the column containing the Emails in the Data Frame

        Returns:
            pandas.DataFrame: new Data Frame with the IDs
        """
        # Check for users
        self.update_users()
        # Add an empty Column
        data_frame['ID'] = ''
        # Fill the Column with the corresponding Slack IDs
        for row_df in range(0, len(df)):
            df_email = df[email_column][row_df]
            for slack_user in self.users:
                try:
                    if str(df_email) == slack_user['profile']['email']:
                        data_frame.at[row_df, 'ID'] = slack_user['id']
                except KeyError:
                    logging.debug('No Email found for user with id {}'.format(slack_user['id']))
        return data_frame


if __name__ == "__main__":
    import math
    import yaml
    import os
    # Configure the logger
    logging.basicConfig(format='%(levelname)s : %(module)s : %(funcName)s >> %(message)s\n',
                        # level=logging.DEBUG)
                        # level=logging.INFO
                        )
    # Read the token (first Argument)
    if len(sys.argv) >= 2:
        token = sys.argv[1]
        logging.debug("Token set to: {}".format(token))
    else:
        logging.error("Not enough Arguments! (need token)")
        raise Exception('give the xoxb token as the first argument')

    # import the configuration File
    actual_folder = os.path.dirname(os.path.abspath(__file__))
    with open(actual_folder + "/config.yml") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # Intro
    terminal_intro("Study Buddy")

    # Create Slack App
    client = SlackClient(bot_token=token)

    # Import CSV and Change the columns according to the cfg File
    df = pd.read_csv(cfg['csv'], sep=cfg['separator'])
    columns = []
    for arg in cfg['columns']:
        for key, val in arg.items():
            df.rename(columns={val: key}, inplace=True)
            columns.append(key)
    df = df[columns]

    # Fill Slack User IDS using the Email column
    df = client.add_slack_id_to_df(df, 'email')

    # Check Slack API
    # Channel Check
    logging.info("Checking Channel IDs")
    client.update_channels()
    channel_id_list = []  # Create ID List
    for channel in client.channels:
        channel_id_list.append(str(channel['id']))
    for key, val in cfg['track channels'].items():
        if val in channel_id_list:
            logging.debug("Channel for {} with ID {} is valid!".format(key, val))
        else:
            raise Exception("Channel for {} with ID {} cannot be found in Workspace!"
                            " check the ID and make sure that the Bot is part of the Channel".format(key, val))
    logging.info("Channel IDs are valid!")
    # Users Check
    logging.info("Checking User IDs")
    client.update_users()
    user_id_list = []
    for user in client.users:
        user_id_list.append(str(user['id']))
    for row in range(0, len(df)):
        user_id = df['ID'][row]
        user_email = df['email'][row]
        if user_id in user_id_list:
            logging.debug("User {} with ID {} exist in Workspace".format(user_email, user_id))
        else:
            raise Exception("User {} with ID {} cannot be found in the workspace".format(user_email, user_id))
    logging.info("User IDs are valid!")

    # Add the Users to the Track Channel
    track_comlumns = ['track1', 'track2', 'track3', 'track4']
    if query_yes_no("Should I Add the Users to the respective track channels?"):
        for row in range(0, len(df)):
            for track_comlumn in track_comlumns:
                if str(df[track_comlumn][row]) != 'nan':
                    user_track = df[track_comlumn][row]
                    user_id = df['ID'][row]
                    channel_id = cfg['track channels'][user_track]
                    user_email = df['email'][row]
                    try:
                        client.add_to_channel(user_id, channel_id)
                        logging.info("user {} with ID {} was added to the channel {}({})".format(user_email,
                                                                                                 user_id,
                                                                                                 user_track,
                                                                                                 channel_id))
                    except errors.SlackApiError:
                        logging.error("could not Add user {} with ID {} to the channel {}({})".format(user_email,
                                                                                                      user_id,
                                                                                                      user_track,
                                                                                                      channel_id))

    # Create Data frames for each track
    tracks_dfs = dict()
    for key, val in cfg['track channels'].items():
        track_filter = df[track_comlumns[0]] == key
        tracks_dfs[key] = df[track_filter]

    # Create the groups
    buddy_groups = []

    for key, val in tracks_dfs.items():
        # Check if there's a techie in the Track
        techies_nr = len(val)
        if techies_nr != 0:
            # restart sufix
            buddy_group_nr = 1
            # Check for an optimal number of members
            desired_members = cfg['buddy groups']['members max']

            leftover = techies_nr % desired_members
            group_nr = techies_nr / desired_members
            while not (leftover == 0 or leftover > cfg['buddy groups']['members min']):
                # try to find a better group size
                desired_members -= 1
                if desired_members < cfg['buddy groups']['members min']:
                    raise Exception(" Cannot find a optimal size for groups in the {} track".format(key))
                techies_nr = len(val)
                leftover = techies_nr % desired_members
                group_nr = techies_nr / desired_members
            if leftover:
                logging.info("for track {}, {} groups each with {} (last group with {})".format(key,
                                                                                                math.ceil(group_nr),
                                                                                                desired_members,
                                                                                                leftover))
            else:
                logging.info("for track {}, {} groups each with {}".format(key,
                                                                           math.ceil(group_nr),
                                                                           desired_members))
            # Make Groups accordingly
            groups = {n: val.iloc[n:n + desired_members, :]
                      for n in range(0, len(val), desired_members)}
            # Save groups in the array
            for g_key, g_val in groups.items():
                buddy_groups.append(BuddyGroup(buddy_group_nr, key, g_val))
                buddy_group_nr += 1
        else:
            logging.warning("the track {} is empty!".format(key))

    # Check that the channels do not exist (known channels)
    channel_name_list = []
    for channel in client.channels:
        channel_name_list.append(str(channel['name']))
    for buddy_group in buddy_groups:
        if buddy_group.name in channel_name_list:
            raise Exception("a channel with the name {} already exist in the workspace!".format(buddy_group.name))

    # Ask the user
    width = 50
    # sleep(3)
    print('\n'
          '>>>>I Will create the following Groups:')
    for buddy_group in buddy_groups:
        print()
        print()
        print("|{}|".format("=" * 96))
        print("|{:^96}|".format('#' + buddy_group.name))
        print("|{}|".format("=" * 96))
        print('|{:^30}|{:63d}  |'.format('SIZE', buddy_group.size))
        print('|{:^30}|{:>63}  |'.format('TRACK', buddy_group.track))
        print("|{:-^96}|".format('MEMBERS'))
        print("|{:_^30.30}|{:_^51.51}|{:_^13.13}|".format('Full_Name', 'email', 'SlackID'))
        for index, row in buddy_group.members.iterrows():
            print("|{:^30.30}|{:^51.51}|{:^13.13}|".format('{} {}'.format(row['name'], row['last name']),
                                                           row['email'],
                                                           row['ID']))
        print("|{}|".format("=" * 96))
    print()
    print()
    print("and will post the following message:\n{}".format(cfg['buddy groups']['start message']))

    if query_yes_no("Should I Proceed?"):
        for buddy_group in buddy_groups:
            # Create Channel
            try:
                response = client.conversations_create(name=buddy_group.name, is_private=True)
            except errors.SlackApiError:
                logging.warning("Cannot create the channel #{}, will try with the name #{}".format(buddy_group.name,
                                                                                                   buddy_group.name +
                                                                                                   '_2'))
                try:
                    response = client.conversations_create(name=buddy_group.name + '_2', is_private=True)

                except errors.SlackApiError:
                    logging.error("Cannot create the channel #{} or #{}".format(buddy_group.name,
                                                                                buddy_group.name + '_2'))
                    continue

            # Set Channel ID
            buddy_group.slack_id = response['channel']['id']
            # Add techies
            for index, row in buddy_group.members.iterrows():
                try:
                    client.add_to_channel(row['ID'], buddy_group.slack_id)
                    logging.info("user {} with ID {} was added to the channel ({}) {}".format(
                        '{} {}'.format(row['name'], row['last name']),
                        row['ID'],
                        buddy_group.slack_id,
                        buddy_group.name))
                except errors.SlackApiError:
                    logging.error("could not Add user {} with ID {} to the channel ({}){}".format(
                        '{} {}'.format(row['name'], row['last name']),
                        row['ID'],
                        buddy_group.slack_id,
                        buddy_group.name))
            # Send Message
            message = cfg['buddy groups']['start message']
            try:
                response = client.chat_postMessage(
                    channel=buddy_group.slack_id,
                    text=message
                )
                logging.info("Message sent! to channel {}".format(buddy_group.name))
            except errors.SlackApiError as e:
                # You will get a SlackApiError if "ok" is False
                assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    else:
        logging.warning("No Studdy Buddy Groups were created...")
