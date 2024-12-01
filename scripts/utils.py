def change_extention(filename, new_extension):
    return '.'.join(filename.split('.')[:-1] + [new_extension])
