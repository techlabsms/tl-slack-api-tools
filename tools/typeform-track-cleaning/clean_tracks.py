"""
CSV Track Cleaner

Tool to find out which is the track that the Techies chosen on an Text Field in Typeform
"""

import sys
import pyfiglet

__author__ = "Andres David Vega Botero"
__email__ = "andresvegabotero@gmail.com"

def query_tracks(question):
    """Ask for a track question via input() and return their answer.

    based on: http://code.activestate.com/recipes/577058/

    Args:
        question (str): is a string that is presented to the user.

    Returns:
        str: AI if '1', WebDev if '2', UX if '3', DataSc if '4', '' if '0'
    """
    valid = {"1": "AI", "2": "WebDev", "3": "UX",
             "4": "DataSc", "0": ''}

    prompt = " [1-> AI | 2 -> WebDev | 3 -> UX | 4 -> DataSc | None] "

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with '1' for AI,"
                             "'2' for WebDev, '3' for UX, '4' for DataSc or '0'for None\n")


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


if __name__ == "__main__":
    import yaml
    import os
    from fuzzywuzzy import fuzz
    from time import sleep
    import pandas as pd
    import logging

    # Configure the logger
    logging.basicConfig(format='%(levelname)s : %(module)s : %(funcName)s >> %(message)s\n',
                        # level=logging.DEBUG)
                        # level=logging.INFO
                        )
    # import the configuration File
    actual_folder = os.path.dirname(os.path.abspath(__file__))
    with open(actual_folder + "/config.yml") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # Intro
    terminal_intro("Track Cleaning")

    # Import CSV and Change the columns according to the cfg File
    df = pd.read_csv(cfg['source']['csv'], sep=cfg['source']['separator'],encoding = "ISO-8859-1")
    columns = []
    for arg in cfg['source']['columns']:
        for key, val in arg.items():
            df.rename(columns={val: key}, inplace=True)
            columns.append(key)
    df = df[columns]
    logging.info('Imported from {}'.format(cfg['source']['csv']))

    # Add empty Columns for the tracks
    df['track1'] = ''
    df['track2'] = ''
    df['track3'] = ''
    df['track4'] = ''

    for index, row in df.iterrows():
        # Check For each track
        match = []
        # Compare with each track:
        for track, possible_names in cfg['tracks'].items():
            track_max_match = 0
            for name in possible_names:
                m = fuzz.partial_ratio(row['track'].lower().replace('\n', ' '), name.lower())
                if m > track_max_match:
                    track_max_match = m
            if track_max_match >= cfg['fuzzy']['certainty ratio']:
                match.append({track: track_max_match})
        if len(match) == 0:
            print("\nI could not find any track for {} {}, The answer was:\n".format(row['name'], row['last name']))
            row['track1'] = query_tracks("Which Track should i assign?")
        elif len(match) == 1:
            row['track1'] = next(iter(match[0]))
            logging.info('For {} {} im sure the track is {}'.format(row['name'], row['last name'],next(iter(match[0]))))
        else:
            print("\nI am not sure about {} {}, The answer was:\n".format(row['name'], row['last name']))
            print(row['track'])
            print()
            track_nr = 1
            print(match)
            for m in match:
                if query_yes_no("Should i assign the {:-^15} track? (certanty: {})".format(next(iter(m)), m[next(iter(m))])):
                    row['track{}'.format(track_nr)] = next(iter(m))
                    logging.info(
                        ' {} {} was added to {}'.format(row['name'], row['last name'], next(iter(m))))
                    sleep(0.1)
                    track_nr += 1

    # Write to the output csv
    logging.info('Saving the result to {}'.format(cfg['output']['csv']))
    df.to_csv(cfg['output']['csv'], cfg['output']['separator'])
