#!/usr/bin/env python

"""
RengaBit - collaborative creation, just a right click away

Usage:
    rengabit.py [(-d | --debug)] mark <filepath> [<commit_msg>]
    rengabit.py [(-d | --debug)] show <filepath>
    rengabit.py [(-d | --debug)] return <filepath> [--rev=<revision>]
    rengabit.py [(-d | --debug)] report
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
from rengautils import gui, macbrg, mail
from docopt import docopt
import sys
import shutil
import json
import shlex


def osx():
    return sys.platform == 'darwin'

if osx():
    renga_path = os.path.join(os.environ['HOME'], ".cg")
else:
    renga_path = "C:\\Users\\AlmondNET\\Documents\\GitHub\\renga_osx_client\\scripts"

renga_icon_path = os.path.join(renga_path, "RengaBitIcon.png")
renga_log_file = os.path.join(renga_path, "rengabit.log")
if(osx()):
    baseScript = os.path.join(renga_path, "rengabit.sh")
else:
    baseScript = os.path.join("C:\\Rengabit\\pgit\\renga.bat")
change_file_comment_script = os.path.join(renga_path, "change_file_comment")
alert_script = os.path.join(renga_path, "alert")
meta_file_name = ".cg"
logger = logging.getLogger(__name__)


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
        run_command("git add " + deal_with_spaces(file_path))


def ask_for_comment():
    """
    Show a gui that ask for comment on changes the user has made
    and return the user's input.

    """
    app = gui.RengaGui(None)
    app.ask_for_comment()
    app.mainloop()
    try:
        return app.result
    except AttributeError:
        return None


def ask_for_issue_cmt():
    app = gui.RengaGui(None)
    app.issue_report()
    app.mainloop()
    try:
        return app.result
    except AttributeError:
        return None


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


def get_filename_with_ver(file_path, ver):
    file_name, ext = os.path.splitext(file_path)
    new_path = file_name + "_" + str(ver) + ext
    return os.path.basename(new_path)


def copy_to_dir(file_path, dest_dir, ver=None):
    """Copy file or folder to mls_dir with the name <file>_<ver>.<ext>"""
    if ver:
        new_name = get_filename_with_ver(file_path, ver)
    else:
        new_name = os.path.basename(file_path)
    dst = os.path.join(dest_dir, new_name)
    logger.debug("copying %s to %s", *(file_path, dst))
    if os.path.isdir(file_path):
        shutil.copytree(file_path, dst)
    else:
        shutil.copy2(file_path, dst)
    return dst


def delete(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)


def change_file_name(file_name, ver):
    """
    Change file or folder to <file_name>_<ver>.<ext>
    return the real path for the new file
    """
    name, ext = os.path.splitext(file_name)
    new_name = name + "_" + str(ver) + ext
    shutil.move(file_name, new_name)
    return os.path.realpath(new_name)


def add_comment_for_windows(file_path, comment):
    """Copy file or folder to mls_dir with the name <file>_<ver>.<ext>"""
    file_name, ext = os.path.splitext(file_path)
    new_path = file_name + "_" + comment + ext
    os.rename(file_path, new_path)
    logger.debug("changes name of %s to %s", *(file_path, new_path))
    return new_path


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
    res = run_command('git log --reverse --format=%H,%cn,%ct,%s ' + deal_with_spaces(file_path))
    revs_list = str(res.decode("utf-8").rstrip()).split("\n")
    result = []
    deli = ","
    for rev_str in revs_list:
        rev_dict = dict(
            zip(["sha1", "commiter", "date", "commit_msg"], rev_str.split(deli)))
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
    dst = os.path.join(dst_dir, meta_file_name)
    f = open(dst, "w")
    logger.debug("writing meta file to: %s", dst)
    json.dump(obj, f)
    return dst


def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv


def get_revs_form_meta_file(meta_file):
    f = open(meta_file, "r")
    revs = json.load(f, object_hook=_decode_dict)
    return revs


def run_command(cmd):
    """
    Run the given cmd in win or mac. return the result output.
    If the command returned with error code will return False
    """
    try:
        logger.debug(cmd)
        if(osx()):
            cmd_list = shlex.split(cmd)
            res = check_output(cmd_list)
        else:
            res = check_output([baseScript, cmd])
        logger.debug(res)
        return res
    except CalledProcessError as e:
        logger.warning(e)
        return False


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


def mark_milestone(file_path, commit_msg=None):
    """
    Will create git repository (if nedded), add the relevant
    file or folder to the stage and commit with the given commit massage.
    """
    if not commit_msg:
        commit_msg = ask_for_comment()
        if not commit_msg:
            alert("You must write some comment.\nNo changes were made.")
            return
    logger.debug("Mark milestone for %s: %s", *(file_path, commit_msg))
    check_and_create_repo()
    # git add
    add_file_or_folder(file_path)
    # git commit
    ok = run_command("git commit -m " + deal_with_spaces(commit_msg))
    if ok:
        if osx():
            # change the file/folder's icon
            logger.debug("changing icon")
            macbrg.change_icon(file_path)
            # modify the file comments
            change_file_comment(file_path, commit_msg)
    else:
        alert("There were no changes since last milestone.")


def show_milestones(file_path):
    """
    Creates a folder named: <file_path>_milestones
    and put all revision of the given file in it
    """
    logger.debug("Show milestones for file: %s", file_path)
    try:
        got_repo = check_reop()
        if not got_repo:
            logger.debug("No git repo here!")
            alert("There are no milestones for this file")
            return
        monitored = run_command("git ls-files " + deal_with_spaces(file_path) + " --error-unmatch")
        if not monitored:
            logger.debug("This file(s) is(are) not being monitored!")
            alert("There are no milestones for this file")
            return
        # prepare a dir to put all milestones
        mls_dir = prepare_mile_stone_dir(file_path)
        # copy current file or folder to milestones folder
        copy_to_dir(file_path, mls_dir, "current")  # save file with _current
        backup = copy_to_dir(file_path, mls_dir)  # save file's uncommitted changes
        # find revision for this file where the file has been touched
        revs = get_revs(file_path)
        # write to file - for later use (return to milestone)
        write_meta_file(mls_dir, revs)
        for i, rev in enumerate(revs):
            # get this file revision
            run_command("git checkout " + rev[
                        'sha1'] + " -- " + deal_with_spaces(file_path))
            # copy revision to the milestones folder
            new_file = copy_to_dir(file_path, mls_dir, i + 1)
            if osx():
                comment = rev["commiter"] + ": " + rev["commit_msg"]
                # modifiy the file comment acorrding to it's commit message
                change_file_comment(new_file, comment)
            else:
                comment = " " + rev["commiter"] + "- " + rev["commit_msg"]
                new_file = add_comment_for_windows(new_file, comment)
            # modifiy the file "last modified" according to commit time
            os.utime(new_file, (int(rev["date"]), int(rev["date"])))
    finally:
        pass
        # clean up...
        # get orignal file to the last revision
        run_command("git checkout HEAD -- " + deal_with_spaces(file_path))
        # restore uncommited changes
        if (os.path.isdir(file_path)):
            delete(file_path)  # special handeling for folder
            shutil.move(backup, os.path.dirname(file_path))
        else:
            copy_to_dir(backup, os.getcwd())
            delete(backup)
        if osx():
            # restore icon
            macbrg.change_icon(file_path)


def return_to_milestone(file_path, revision=None):
    """
    Return to milestome with revision number. if revison is not provided,
    the revision number will be extracted from the file name.
    """
    logger.debug("return to milestone of: %s", file_path)
    mls_folder = os.path.dirname(file_path)
    meta_file = os.path.join(mls_folder, meta_file_name)
    if not os.path.exists(meta_file):
        logger.warning("no %s meta file here", meta_file_name)
        alert("This is not a milestome of any file or folder")
        return
    file_name, ext = os.path.splitext(os.path.basename(file_path))
    if not revision:
        # get the revision number from the file name
        if(osx()):
            revision = file_name.rsplit("_", 1)[1]
        else:
            revision = file_name.split("_")[1]

    rev = get_revs_form_meta_file(meta_file)[int(revision) - 1]
    logger.debug("return to rev:\n%s", rev)
    # get the original file name ()
    if osx():
        org_file_name = file_name.rsplit("_", 1)[0] + ext
    else:
        org_file_name = file_name.split("_")[0] + ext
    org_file = os.path.join(os.path.dirname(mls_folder), org_file_name)
    sha1 = rev["sha1"]
    # put the file in it's place
    run_command("git checkout " + sha1 + " -- " + deal_with_spaces(org_file))
    # commit the return to milestone
    if osx():
        cmt_msg = "Return to: " + rev["commit_msg"]
    else:
        cmt_msg = "Return to- " + rev["commit_msg"]
    run_command("git commit -m " + deal_with_spaces(cmt_msg) + " -- " + deal_with_spaces(org_file))
    if osx():
        # change commnet
        change_file_comment(org_file, rev["commit_msg"])
        # restore icon
        macbrg.change_icon(org_file)
    # clean milestone folder
    delete(mls_folder)


def report_issue():
    sub = "RengaBit client: Issue report"
    sender = "pilot@rengabit.com"  # TODO get the user's email
    msg = ask_for_issue_cmt()
    if not msg:
        return
    to = ['info@rengabit.com']
    logger.debug("sending issue report with massage:\n%s", msg)
    mail.send_mail(sender, to, sub, msg, renga_log_file)
    alert("Thanks. The issue report has been sent.\nWe'll fix it ASAP!")


def deal_with_spaces(string):
    if osx():
        return '"' + string + '"'
    else:
        string = "fakeQ" + string + "fakeQ"
        return string.replace(" ", "AAAA")


def main():
    args = docopt(__doc__, version='RengaBit-ALPHA-0.2.1')
    config_logger(args)
    logger.debug(args)
    # Run a command according to the given arguments
    f = None
    if args['<filepath>']:
        f = os.path.realpath(os.path.expanduser(args['<filepath>']))
        change_dir(f)

    # Rund the command
    if args['mark']:
        mark_milestone(f, args['<commit_msg>'])
    elif args['show']:
        show_milestones(f)
    elif args['return']:
        return_to_milestone(f, args["--rev"])
    elif args['report']:
        report_issue()

if __name__ == '__main__':
    main()
