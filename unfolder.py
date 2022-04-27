# philip boesch
# 03-03-2022

import os
import shutil

# set file path
path = r'maic_raw/real_raw/no_daniloski'

# move files from individual folders into one place
for folder in os.listdir(path):
    if not folder.startswith('.'):
        old_file = os.listdir(path + '/' + folder)
        old_file = ''.join(old_file)
        old_file = r'maic_raw/real_raw/no_daniloski/' + folder + '/' + old_file
        destination = r'maic_raw/real_raw/no_daniloski/newbie' + str(folder)
        os.rename(old_file, destination)


