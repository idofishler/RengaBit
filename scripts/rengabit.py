#!/usr/bin/env python

"""
RengaBit - collaborative creation, just a right click away

Usage:
    rengabit.py [(-d | --debug)] mark <filepath> [<commit_msg>]
    rengabit.py [(-d | --debug)] show <filepath>
    rengabit.py [(-d | --debug)] return <filepath> [--rev=<revision>]
    rengabit.py (-h | --help)
    rengabit.py --version

Options:
    -h --help             Show this screen.
    --version             Show version.
    -d --debug            Debug mode
    --rev=<revision>      The SHA1 for a spesific revision.

"""

import logging
from os import path, environ, chdir
from subprocess import check_output, CalledProcessError, call
from rengautils import gui, macbrg
from docopt import docopt


debug = False

renga_path = path.join(environ['HOME'], ".cg")
renga_icon_path = path.join(renga_path, "RengaBitIcon.png")
renga_log_file = path.join(renga_path, "rengabit.log")
baseScript = path.join(renga_path, "rengabit.sh")
change_file_comment_script = path.join(renga_path, "change_file_comment")
alert_script = path.join(renga_path, "alert")
logger = logging.getLogger(__name__)


def check_and_create_repo():
    """check if repo exists"""

    try:
        cmd = ["git", "status"]
        logger.debug(' '.join(cmd))
        res = check_output(cmd)
        logger.debug(res)
    except CalledProcessError:
        # no repo , need to create one
        cmd = ["git", "init"]
        logger.debug(' '.join(cmd))
        res = check_output(cmd)
        logger.debug(res)


def add_file_or_folder(file_path):
    """ Added git file or folder to stage """

    if path.isdir(file_path):
        cmd = ["git", "add"  "."]
    else:
        cmd = ["git", "add", file_path]
    logger.debug(' '.join(cmd))
    res = check_output(cmd)
    logger.debug(res)


def ask_for_comment():
    app = gui.RengaGui(None)
    app.ask_for_comment()
    app.mainloop()
    return app.result


def commit(commit_msg):
    cmd = ["git", "commit", "-m", '"' + commit_msg + '"']
    logger.debug(' '.join(cmd))
    try:
        res = check_output(cmd)
        logger.debug(res)
        return True
    except CalledProcessError:
        logger.debug("Commit issue")
        return False


def mark_milestone(file_path, commit_msg=None):
    """
    Will create git repository (if nedded), add the relevant
    file or folder to the stage and commit with the given commit massage.
    """
    if not commit_msg:
        commit_msg = ask_for_comment()
    logger.debug("Mark milestone for %s: %s", *(file_path, commit_msg))
    check_and_create_repo()
    add_file_or_folder(file_path)
    ok = commit(commit_msg)
    if ok:
        logger.debug("changing icon")
        macbrg.change_icon(file_path)
        call([change_file_comment_script, file_path, commit_msg])
    else:
        call([alert_script, "There were no changes since last milestone."])


def show_milestones(file_path):
    pass


def return_to_milestone(filepath, revision=None):
    pass


def config_logger(args):
    debug = args['--debug']
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s:\n%(message)s')
    if debug:
        handler = logging.StreamHandler()
    else:
        handler = logging.FileHandler(renga_log_file)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def main():
    args = docopt(__doc__, version='RengaBit-ALPHA-0.2.1')
    config_logger(args)
    logger.debug(args)
    # Run a command according to the given arguments
    f = path.realpath(path.expanduser(args['<filepath>']))

    # change directory to file's directort
    if path.isdir(f):
        chdir(f)
        logger.debug("filepath is a directory")
        logger.debug("Changed directory to: %s", f)
    else:
        chdir(path.dirname(f))
        logger.debug("filepath is a file")
        logger.debug("Changed directory to: %s", path.dirname(f))

    # Rund the command
    if args['mark']:
        mark_milestone(f, args['<commit_msg>'])
    elif args['show']:
        show_milestones(f)
    elif args['return']:
        return_to_milestone(f, args["--rev"])

if __name__ == '__main__':
    main()
