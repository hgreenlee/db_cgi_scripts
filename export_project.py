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
# id - Project id.
# results_per_page - Number of projects to display on each page.
# page - Current page (starts at 1).
#
# Created: 15-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os, StringIO
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(id, results_per_page, current_page, pattern):

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

    
    id = 0
    results_per_page = 20
    current_page = 1
    pattern = ''
    args = dbargs.get()
    if 'id' in args:
        id = int(args['id'])
    if 'results_per_page' in args:
        results_per_page = int(args['results_per_page'])
    if 'page' in args:
        current_page = int(args['page'])
    if 'pattern' in args:
        pattern = args['pattern']

    # Call main procedure.

    main(id, results_per_page, current_page, pattern)
