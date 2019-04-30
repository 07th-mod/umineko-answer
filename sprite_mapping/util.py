import os
def get_with_file_extension(file_path : str, new_extension_with_dot : str):
    path_no_ext, ext = os.path.splitext(file_path)
    return path_no_ext + new_extension_with_dot
