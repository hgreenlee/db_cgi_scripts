#! /usr/bin/python
#==============================================================================
#
# Name: add_project.py
#
# Purpose: CGI script to add an empty project.
#
# CGI arguments:
#
# <qdict> - Standard query_projects.py arguments.
#
# Created: 15-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False)

    # Add project and redirect to project editor.

    project_id = dbutil.insert_blank_project(cnx)
    url = 'https://microboone-exp.fnal.gov/cgi-bin/db/edit_project.py?id=%d&%s' % \
          (project_id, dbargs.convert_args(qdict))

    # Generate redirect page.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<meta http-equiv="refresh" content="0; url=%s" />' % url
    print '</head>'
    print '<body>'
    print 'Add project.'
    print '<br><br>'
    print 'If page does not automatically reload click this <a href=%s>link</a>' % url
    print '</body>'
    print '</html>'

    # Done.

    return

# End of definitions.  Executable code starts here.

if __name__ == "__main__":

    # Parse arguments.

    argdict = dbargs.get()
    qdict = dbargs.extract_qdict(argdict)

    # Call main procedure.

    main(qdict)
