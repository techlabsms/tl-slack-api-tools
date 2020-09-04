"""
Slack User ID Completion

the Slack API cannot send more than 1001 users, and right now the workspace have 
more than 1900, the user ID matching has to be done using the export csv file from 
the admin console

"""

import sys
import pyfiglet

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

if __name__ == "__main__":
    import yaml
    import os
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
    with open(actual_folder + "/config.yml", encoding='utf-8') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # Intro
    terminal_intro("Slack User ID Assigning")

    # Import first CSV and Change the columns according to the cfg File
    df1 = pd.read_csv(cfg['slack user list']['csv'], sep=cfg['slack user list']['separator'])
    columns = []
    for arg in cfg['slack user list']['columns']:
        for key, val in arg.items():
            df1.rename(columns={val: key}, inplace=True)
            columns.append(key)
    df1 = df1[columns]
    logging.info('Imported from {}'.format(cfg['slack user list']['csv']))

    print(df1)
    # import the second CSV
    df2 = pd.read_csv(cfg['typeform']['csv'], sep=cfg['typeform']['separator'])
    columns = []
    for arg in cfg['typeform']['columns']:
        for key, val in arg.items():
            df2.rename(columns={val: key}, inplace=True)
            columns.append(key)
    df2 = df2[columns]
    logging.info('Imported from {}'.format(cfg['typeform']['csv']))

    print(df2)

    df = pd.merge(df1, df2, on='email')
    print(df)

    # Write to the output csv
    logging.info('Saving the result to {}'.format(cfg['output file']['csv']))
    df.to_csv(cfg['output file']['csv'], sep=cfg['output file']['separator'])