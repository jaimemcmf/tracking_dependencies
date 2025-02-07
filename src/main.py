'''
main file
'''

import os
import pathlib
import argparse
from colorama import Fore, Style
from get_package import *
from extools import *

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--package', required=False, action='store')
parser.add_argument('-d', '--download', required=False, action='store')
parser.add_argument('-c', '--checker', required=False, action='store',
                    help='The Python file should be present in the "checker" directory.')
try:
    args = parser.parse_args()
except argparse.ArgumentError as e:
    print(e)

src = os.getcwd()
root = os.path.dirname(src)

os.chdir(root)

if not os.path.isdir(root+'/flagged_packages'):
    os.system('mkdir flagged_packages')

if not os.path.isdir(root+'/downloaded_packages'):
    os.system('mkdir downloaded_packages')

if not os.path.isdir(root+'/checker'):
    os.system('mkdir checker') 

os.chdir(src)

if args.download is not None:
    # -d flag
    print(args.download)
    prev_down = set()
    prev_down.add(args.download)
    cur = download_package(args.download)
    deps = find_deps(cur)
    while True:
        if not deps:
            break

        for dep in deps:
            deps.remove(dep)
            if isinstance(dep,list):
                dep = dep[0]

            dep = parse_package_name(dep)[0]

            if dep in prev_down or dep is None:
                continue

            prev_down.add(str(dep))

            print(dep)
            prev_down.add(dep)
            cur = download_package(dep)
            ndeps = find_deps(cur)
            if ndeps:
                deps.append(ndeps)
                deps = flatten(deps)

elif args.package is not None:
    # -p flag
    print(args.package)
    get_all_deps(args.package, '    ')

elif args.checker is not None:
    # -c flag
    path = root + '/checker'
    suspicious = False

    if args.checker in os.listdir(path) and os.path.isfile(path+'/'+args.checker) and pathlib.Path(path+'/'+args.checker).suffix == '.py':

        clean = remove_comments(path, args.checker)

        if find_hardcoded_urls(clean) and not url_in_setup(clean) and not url_in_prints(clean):
            suspicious = True
            print(f"{Fore.RED}This file is suspicious.{Style.RESET_ALL}")
        if not suspicious and manual_pip_install(clean):
            suspicious = True
            print(f"{Fore.RED}This file is suspicious.{Style.RESET_ALL}")

        if not suspicious:
            print(f"{Fore.GREEN}This file seems to be safe.{Style.RESET_ALL}")

        os.remove(path + '/' + clean)
    else:
        print('This file is not present in "checker" directory or is not a Python file.')

else:
    #default
    iterate_pypi()
