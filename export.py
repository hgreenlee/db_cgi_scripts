#! /usr/bin/python
#==============================================================================
#
# Name: export.py
#
# Purpose: This script is a wrapper around export_project.py that can be 
#          executed from any directory.
#
# CGI arguments:
#
# id      - Project id.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 15-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os

# Calculate the directory where most python scripts and modules are located.

dir = os.path.abspath(__file__)
while dir != '/' and not dir.endswith('fnal.gov'):
    dir = os.path.dirname(dir)
dir = '%s/cgi-bin/db' % dir
sys.path.append(dir)

# Import modules.

import export_project, dbargs

# Parse arguments.

argdict = dbargs.get()
qdict = dbargs.extract_qdict(argdict)
id = 0
if 'id' in argdict:
    id = int(argdict['id'])

# Call export_projects

export_project.main(id, qdict)
