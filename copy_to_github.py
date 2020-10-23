#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copy to github
"""

import os,shutil,subprocess,sys
import shlex

if sys.version_info[0] > 2:
    unicode = str


os.chdir(os.path.dirname(__file__))

cmd = 'git ls-files > .FILES'
subprocess.call(cmd,shell=True)

cmd = 'git tag -f github_copy'
subprocess.call(shlex.split(cmd))

pp = subprocess.check_output(shlex.split('git path')).strip()
if not isinstance(pp,unicode):
    pp = pp.decode('utf8')


SRC = os.path.abspath('.') + '/' # MUST end in /
DST = os.path.abspath('../github/dicttable')

cmd = [
    'rsync',
    '-avzhh','--delete',
    '--include-from','.FILES',
    '--exclude','.*',
    '--exclude','copy_to_github.py',
    SRC,DST]

subprocess.check_call(cmd)

os.remove('.FILES')

os.chdir(DST)

subprocess.check_call(['git','add','.'])

msg = ''
if len(sys.argv)>1:
    msg = sys.argv[1] +'\n\n'

cmd = ['git','commit','-am','{}Copy from local devel repo: {}'.format(msg,pp)]
subprocess.call(cmd)
subprocess.call(['git','commit','--amend'])

