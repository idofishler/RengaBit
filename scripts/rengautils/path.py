#!/usr/bin/env python

import os
import shutil
import logging
logger = logging.getLogger(__name__)


def config_logger(debug, log_file=None):
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s:\n%(message)s')
    if debug:
        handler = logging.StreamHandler()
    else:
        handler = logging.FileHandler(log_file)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def delete(path):
    if not os.path.exists(path):
        logger.debug("%s does not exists", path)
        return
    logger.debug("Deleting %s", path)
    if os.path.isdir(path):
        shutil.rmtree(path, onerror=onerror)
    else:
        os.remove(path)


def mkdir(path, override=False):
    if os.path.exists(path):
        if override:
            delete(path)
        else:
            return
    os.makedirs(path)
    logger.debug("created directory at: %s", path)


def change_dir(f_path):
    """change directory to file's or folder's directory"""
    if os.path.isdir(f_path):
        os.chdir(f_path)
        logger.debug("filepath is a directory")
        logger.debug("Changed directory to: %s", f_path)
    else:
        os.chdir(os.path.dirname(f_path))
        logger.debug("filepath is a file")
        logger.debug("Changed directory to: %s", os.path.dirname(f_path))


def copy_to_dir(file_path, dest_dir):
    """Copy file or folder to dest_dir"""
    new_name = os.path.basename(file_path)
    dst = os.path.join(dest_dir, new_name)
    logger.debug("copying %s to %s", *(file_path, dst))
    if os.path.isdir(file_path):
        shutil.copytree(file_path, dst)
    else:
        shutil.copy2(file_path, dst)
    return dst
