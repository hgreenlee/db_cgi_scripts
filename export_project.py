#! /usr/bin/python
#==============================================================================
#
# Name: export_project.py
#
# Purpose: CGI script to export a project to an XML file on the local computer.
#          This script generates an html page that informs whether the export
#          operation was successful, including the name of the exported file.
#          The information page includes a clickable button that returns to
#          the projects query page.
#
# CGI arguments:
#
# id      - Project id.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 15-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os, StringIO
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(id, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = True)

    # Get project name.

    name = dbutil.get_project_name(cnx, id)

    # Generate html document header.

    print 'Content-type: text/xml'
    print

    # Generate main parg of html document.

    if id == 0 or name == '':
        print 'No such project.'
    else:

        # Generate XML.

        xml = StringIO.StringIO()
        dbutil.export_project(cnx, id, xml)
        print xml.getvalue()

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
