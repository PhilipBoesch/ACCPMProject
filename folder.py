import os
import shutil

path1 = r'test_inputs'
path2 = r'test_inputs/combined_inputs'
os.mkdir(path2)

for folder in os.listdir(path1):
  if not folder.startswith('.') and not folder.startswith('combined'):
    old_files = os.listdir(os.path.join(path1, folder))
    for file in old_files:
      if file.startswith('MAIC_input_') and not 'unconverted' in file and not 'duplicates' in file:
        new_name = r'test_inputs/combined_inputs/maic_input_' + str(folder) + '.txt'
        os.rename(os.path.join(path1, folder, file), new_name)
