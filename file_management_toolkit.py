import os
from time import sleep


def judge_create_directory(directory):
    # Judge whether directory exists and if not, create it
    judgement = os.path.exists(directory)
    if judgement is not True:
        os.makedirs(directory)

        while os.path.exists(directory) is False:  # Ensure
            # directory has been successfully created
            sleep(0.5)

        msg = 'Directory {} has been created successfully.'.format(directory)
    else:
        msg = 'You already have the directory {}.'.format(directory)
    return msg

