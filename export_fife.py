#! /usr/bin/python
#==============================================================================
#
# Name: export_fife.py
#
# Purpose: CGI script to export a project to fife_launch config to standard output.
#
# CGI arguments:
#
# id      - Project id.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 15-Apr-2021  H. Greenlee
#
#==============================================================================

import sys, os, StringIO
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(id, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = True, devel = qdict['dev'])

    # Get project name.

    name = dbutil.get_project_name(cnx, id)

    # Generate document header.

    print 'Content-type: text/plain'
    print

    # Generate main part of text document.

    if id == 0 or name == '':
        print 'No such project.'
    else:

        # Generate text.

        cfg = StringIO.StringIO()
        dbutil.export_fife_project(cnx, id, cfg)
        print cfg.getvalue()

    # Done.


# End of definitions.  Executable code starts here.

if __name__ == "__main__":

    # Parse arguments.

    argdict = dbargs.get()
    qdict = dbargs.extract_qdict(argdict)
    id = 0
    if 'id' in argdict:
        id = int(argdict['id'])

    # Call main procedure.

    main(id, qdict)
