#!/usr/bin/env python

"""
RengaBit - collaborative creation, just a right click away

Usage:
    rengabit.py [(-d | --debug)] mark <filepath> [<commit_msg>]
    rengabit.py [(-d | --debug)] show <filepath>
    rengabit.py [(-d | --debug)] return <filepath> --rev=<revision>
    rengabit.py (-h | --help)
    rengabit.py --version

Options:
    -h --help             Show this screen.
    --version             Show version.
    -d --debug            Debug mode
    --rev=<revision>      The SHA1 for a spesific revision.

"""

import logging
import os
from subprocess import check_output, CalledProcessError
from rengautils import gui, macbrg
import sys
import shutil
import json
import shlex


debug = False

renga_path = os.path.join(os.environ['HOME'], ".cg")
renga_icon_path = os.path.join(renga_path, "RengaBitIcon.png")
renga_log_file = os.path.join(renga_path, "rengabit.log")
baseScript = os.path.join(renga_path, "rengabit.sh")
change_file_comment_script = os.path.join(renga_path, "change_file_comment")
alert_script = os.path.join(renga_path, "alert")
logger = logging.getLogger(__name__)


def osx():
    return sys.platform == 'darwin'

if osx():
    from docopt import docopt


def check_reop():
    """check if git repository exists"""
    return run_command('git status')


def check_and_create_repo():
    """check if repo exists and create it if not"""
    if not check_reop():
        # no repo , need to create one
        return run_command('git init')


def add_file_or_folder(file_path):
    """ Added git file or folder to stage """
    if os.path.isdir(file_path):
        run_command('git add .')
    else:
        run_command('git add "' + file_path + '"')


def ask_for_comment():
    """
    Show a gui that ask for comment on changes the user has made
    and return the user's input.

    """
    app = gui.RengaGui(None)
    app.ask_for_comment()
    app.mainloop()
    return app.result


def alert(msg):
    """Shows a gui with the given msg to the user"""
    app = gui.RengaGui(None)
    app.alert(msg)
    app.mainloop()


def prepare_mile_stone_dir(file_path):
    """
    Will create a folder as a sibling to file_path with the
    name: <file_path>_milestones. If a such folder already exists
    it will be removed and a new one will be created
    """
    milesones_dir = file_path + "_milestones"
    if os.path.exists(milesones_dir):
        shutil.rmtree(milesones_dir)
    os.makedirs(milesones_dir)
    logger.debug("created milestones directory at: %s", milesones_dir)
    return milesones_dir


def copy_to_dir(file_path, mls_dir, ver):
    """Copy file or folder to mls_dir with the name <file>_<ver>.<ext>"""
    file_name, ext = os.path.splitext(file_path)
    new_path = file_name + "_" + str(ver) + ext
    new_name = os.path.basename(new_path)
    dst = os.path.join(mls_dir, new_name)
    if os.path.isdir(file_path):
        shutil.copytree(file_path, dst)
    else:
        shutil.copy2(file_path, dst)
    logger.debug("copyied %s to %s", *(file_path, dst))
    return dst


def change_file_comment(file_path, comment):
    cmd = [change_file_comment_script, file_path, comment]
    logger.debug(' '.join(cmd))
    res = check_output(cmd)
    logger.debug(res)


def get_revs(file_path):
    """
    Return a list of directories where each list item is a revision in the
    following format:
    {
     "sha1": <hash>,
     "commiter" : <commiter name>,
     "date": <commit date>
     "commit_msg": <the short commit massage>
    }

    """
    cmd = ["git", "log", "--reverse", "--format=%H|%cn|%ci|%s", "--", file_path]
    logger.debug(' '.join(cmd))
    res = check_output(cmd)
    revs_list = str(res.decode("utf-8").rstrip()).split("\n")
    result = []
    for rev_str in revs_list:
        rev_dict = dict(zip(["sha1", "commiter", "date", "commit_msg"], rev_str.split("|")))
        result.append(rev_dict)
    return result


def write_meta_file(dst_dir, obj):
    """
    Writes the given object (using json) to a file in dst_dir and
    return the file's path
    """
    if not os.path.isdir(dst_dir):
        logger.error("%s is not a directory", dst_dir)
        return None
    dst = os.path.join(dst_dir, ".cg")
    f = open(dst, "w")
    logger.debug("writing meta file to: %s", dst)
    json.dump(obj, f)
    return dst


def run_command(cmd):
    try:
        logger.debug(cmd)
        cmd_list = shlex.split(cmd)
        res = check_output(cmd_list)
        logger.debug(res)
        return True
    except CalledProcessError as e:
        logger.warning(e)
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
    ok = run_command('git commit -m "' + commit_msg + '"')
    if ok and osx():
        logger.debug("changing icon")
        macbrg.change_icon(file_path)
        change_file_comment(file_path, commit_msg)
    else:
        alert("There were no changes since last milestone.")


def show_milestones(file_path):
    """
    Creates a folder named: <file_path>_milestones
    and put all revision of the given file in it
    """
    try:
        got_repo = check_reop()
        if not got_repo:
            logger.debug("No git repo here!")
            alert("There are no milestones for this file")
            return
        monitored = run_command('git ls-files "' + file_path + '" --error-unmatch')
        if not monitored:
            logger.debug("This file(s) is(are) not being monitored!")
            alert("There are no milestones for this file")
            return
        mls_dir = prepare_mile_stone_dir(file_path)
        copy_to_dir(file_path, mls_dir, "current")
        run_command("git stash")
        revs = get_revs(file_path)
        write_meta_file(mls_dir, revs)
        for i, rev in enumerate(revs):
            run_command('git checkout ' + rev['sha1'] + ' -- "' + file_path + '"')
            new_file = copy_to_dir(file_path, mls_dir, i + 1)
            if osx():
                comment = rev["commiter"] + ": " + rev["commit_msg"]
                change_file_comment(new_file, comment)
    finally:
        run_command("git reset --hard HEAD")
        run_command("git stash pop")


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
    f = os.path.realpath(os.path.expanduser(args['<filepath>']))

    # change directory to file's directort
    if os.path.isdir(f):
        os.chdir(f)
        logger.debug("filepath is a directory")
        logger.debug("Changed directory to: %s", f)
    else:
        os.chdir(os.path.dirname(f))
        logger.debug("filepath is a file")
        logger.debug("Changed directory to: %s", os.path.dirname(f))

    # Rund the command
    if args['mark']:
        mark_milestone(f, args['<commit_msg>'])
    elif args['show']:
        show_milestones(f)
    elif args['return']:
        return_to_milestone(f, args["--rev"])

if __name__ == '__main__':
    main()
