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

import sys

# This is the directory where most python scripts and modules are located.

dir = '/web/sites/m/microboone-exp.fnal.gov/cgi-bin/db'
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
