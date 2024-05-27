import os


def remove(file, dir):
    """
    delete prompt
    """
    os.remove(os.path.join(dir, file))
    return
