#!/usr/bin/env python
# this script sets up the testing packages to allow the tests


from __future__ import absolute_import, division, print_function
import subprocess
import argparse
import os

pip_packages = [
    "git+https://bitbucket.org/dragon512/reusable-gold-testing-system.git",
]


def create_venv(path):
    '''
    Create virtual environment and add it
    to the path being used for the script
    '''
    subprocess.call(["virtualenv", path])


def main():
    " main script logic"
    parser = argparse.ArgumentParser()

    parser.add_argument("--use-pip",
                        nargs='?',
                        default="pip",
                        help="Which pip to use")

    parser.add_argument("venv_path",
                        nargs='?',
                        default="env-test",
                        help="The directory to us to for the virtualenv")

    parser.add_argument("--disable-virtualenv",
                        default=False,
                        action='store_true',
                        help="Do not create virtual environment to install packages under")

    parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0.0')

    args = parser.parse_args()
    print(args)
    if not args.disable_virtualenv:
        # set venv
        create_venv(args.venv_path)
    path_to_pip = os.path.join(args.venv_path, "bin", args.use_pip)

    # install pip packages
    subprocess.call([path_to_pip, "install"]+pip_packages)


if __name__ == '__main__':
    main()
