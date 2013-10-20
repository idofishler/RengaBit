#!/usr/bin/env python
"""
RengaBit - collaborative creation, just a right click away

Usage:
    build.py compile
    build.py pack
    build.py upload
    build.py (-h | --help)
    build.py --version

Options:
    -h --help             Show this screen.
    --version             Show version.

"""

import logging
import sys
import os
import shutil
import zipfile
import shlex
from subprocess import check_output, CalledProcessError
from docopt import docopt

logger = logging.getLogger(__name__)
version = 'RengaBit-ALPHA-0.2.1'


def osx():
    return sys.platform == 'darwin'


def config_logger():
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s:\n%(message)s')
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def mkdir(path, override=False):
    if os.path.exists(path):
        if override:
            shutil.rmtree(path)
        else:
            return
    os.makedirs(path)
    logger.debug("created directory at: %s", path)


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


def run_command(cmd):
    """
    Run the given cmd in win or mac. return the result output.
    If the command returned with error code will return False
    """
    try:
        logger.debug(cmd)
        cmd_list = shlex.split(cmd)
        res = check_output(cmd_list)
        logger.debug(res)
        return res
    except CalledProcessError as e:
        logger.warning(e)
        return False


def delete(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def cleanup():
    delete('dist')
    delete('build')


def build_osx():
    from setuptools import setup
    APP = ['rengabit.py']
    DATA_FILES = []
    OPTIONS = {'argv_emulation': True}
    setup(
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )


def build_win():
    from distutils.core import setup
    import py2exe
    setup(console=['rengabit.py'])


def zip(src, dst):
    zf = zipfile.ZipFile("%s.zip" % (dst), "w")
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            print 'zipping %s as %s' % (os.path.join(dirname, filename),
                                        arcname)
            zf.write(absname, arcname)
    zf.close()


def pack():
    pwd = os.getcwd()
    parent = os.path.dirname(pwd)
    if osx():
        # get files
        pkg = os.path.join(parent, 'build', version + '.pkg')
        txt = os.path.join(parent, 'INSTALL.txt')
        csh = os.path.join(parent, 'post_install.sh')
        tmp = os.path.join(parent, 'tmp')
        # create a temp folder
        mkdir(tmp, override=True)
        # copy files to temp folder
        copy_to_dir(pkg, tmp)
        copy_to_dir(txt, tmp)
        copy_to_dir(csh, tmp)
        # make dmg
        run_command('hdiutil create ../build/RengaBit_tmp.dmg -ov -volname "RengaBit" -fs HFS+ -srcfolder "../tmp/"')
        run_command('hdiutil convert ../build/RengaBit_tmp.dmg -format UDZO -o ../build/RengaBit.dmg')
        # delete tmp folder
        delete(tmp)
        delete(os.path.join(parent, 'build', 'RengaBit_tmp.dmg'))
    else:
        dst = os.path.join(parent, 'build', version)
        zip('dist', dst)
        #zip(os.path.join('lib', 'chromedriver.exe'), dst)
        #zip(os.path.join(parent, 'renga_win_client', 'install.bat'), dst)
        #zip(os.path.join(parent, 'renga_win_client', 'rengaReg.reg'), dst)
        #zip(os.path.join(parent, 'INSTALL.txt'), dst)


def uplaod():
    pass


def build():
    if osx():
        build_osx()
    else:
        build_win()


def main():
    args = docopt(__doc__, version=version)
    config_logger()
    if args['compile']:
        cleanup()
        build()
    if args['pack']:
        pack()
    if args['upload']:
        uplaod()  # TODO


if __name__ == '__main__':
    main()
