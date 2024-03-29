#!/usr/bin/env python
"""
RengaBit - collaborative creation, just a right click away

Usage:
    build.py (py2app | py2exe)
    build.py pack [(-l | --local_install)]
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
import zipfile
import shlex
from subprocess import check_output, CalledProcessError
from docopt import docopt
import boto
from rengautils import path

logger = logging.getLogger(__name__)
version = 'RengaBit-ALPHA-0.2.1'


def osx():
    return sys.platform == 'darwin'

pwd = os.getcwd()
parent = os.path.dirname(pwd)
out_dir = os.path.join(parent, 'build')
if osx():
    out = os.path.join(out_dir, 'RengaBit.dmg')
else:
    out = os.path.join(out_dir, 'RengaBit.exe')


def config_logger():
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s:\n%(message)s')
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    path.config_logger(debug=True)


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


def cleanup():
    path.delete('dist')
    path.delete('build')


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
    icon_file = os.path.join(out_dir, 'RengaBit.ico')
    OPTIONS = {
        "script": "rengabit.py",
        "icon_resources": [(1, icon_file)]
    }
    setup(windows=[OPTIONS])


def zip(src, dst):
    zf = zipfile.ZipFile("%s.zip" % (dst), "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            print 'zipping %s as %s' % (os.path.join(dirname, filename),
                                        arcname)
            zf.write(absname, arcname)
    zf.close()


def pack(install_local=False):
    if osx():
        # create a temp folder
        tmp = os.path.join(parent, 'tmp')
        path.mkdir(tmp, override=True)
        txt = os.path.join(parent, 'INSTALL_MAC.txt')
        # get mac files
        pkg = os.path.join(out_dir, version + '.pkg')
        csh = os.path.join(parent, 'post_install.sh')
        # copy files to temp folder
        path.copy_to_dir(pkg, tmp)
        path.copy_to_dir(csh, tmp)
        path.copy_to_dir(txt, tmp)
        # make dmg
        path.delete(out)
        run_command('hdiutil create ../build/RengaBit_tmp.dmg -ov -volname "RengaBit" -fs HFS+ -srcfolder "../tmp/"')
        run_command('hdiutil convert ../build/RengaBit_tmp.dmg -format UDZO -o ../build/RengaBit.dmg')
        # clean temp files
        path.delete(os.path.join(out_dir, 'RengaBit_tmp.dmg'))
        if install_local:
            install_app = '~/.cg/dist/rengabit.app'
            path.delete(install_app)
            path.copy_to_dir('dist/rengabit.app', '~/.cg/')
        # delete tmp folder
        path.delete(tmp)
    else:
        # Run inno setup
        iss = os.path.join(out_dir, 'rengabit.iss')
        print iss
        run_command('iscc "' + iss + '"')


def uplaod():
    s3 = boto.connect_s3()
    logger.debug("Connected to S3")
    bucket = s3.get_bucket('rengabit')
    logger.debug("Connected to bucket %s", bucket)
    from boto.s3.key import Key
    k = Key(bucket)
    k.key = 'public/' + os.path.basename(out)
    logger.debug("Uploading %s as %s", *(out, k.key))
    k.set_contents_from_filename(out)
    k.set_acl('public-read')
    logger.debug("Upload done sucssesfuly.")


def build():
    if osx():
        build_osx()
    else:
        build_win()


def main():
    args = docopt(__doc__, version=version)
    config_logger()
    if args['py2app'] or args['py2exe']:
        cleanup()
        build()
    if args['pack']:
        pack(install_local=args['-l'])
    if args['upload']:
        uplaod()


if __name__ == '__main__':
    main()
