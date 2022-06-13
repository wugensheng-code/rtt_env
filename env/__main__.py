'''
env is executed as a module
'''

import os
import sys

from env.main import app

os.chdir(r'/home/shinu/文档/github/rt-thread/bsp/qemu-vexpress-a9/')
sys.argv = ['env', 'pkgs', 'update']
app(prog_name="env")
