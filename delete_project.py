#! /usr/bin/python
#==============================================================================
#
# Name: delete_project.py
#
# Purpose: CGI script to delete a project from database.
#
# CGI arguments:
#
# id      - Project id.
# confirm - Confirm flag.
#           If value is zero, display a confirmation page.
#           If value is nonzero, delete project.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 15-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(id, confirm, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False)

    # Get project name.

    name = dbutil.get_project_name(cnx, id)

    # Check confirm flag.

    if confirm == 0:

        # If confirm flag is zero, generate a confirmation page.

        print 'Content-type: text/html'
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<head>'
        print '<title>Delete Project</title>'
        print '</head>'
        print '<body>'
        if id == 0 or name == '':

            print 'No such project.'

        else:

            print 'Delete project %s?' % name

            # Generate a form with two buttons "Delete" and "Cancel."

            print '<br>'
            print '<form action="/cgi-bin/delete_project.py?id=%d&confirm=1&%s" method="post">' % \
                (id, dbargs.convert_args(qdict))
            print '<input type="submit" value="Delete">'
            print '<input type="submit" value="Cancel" formaction="/cgi-bin/query_projects.py?%s">' % \
                dbargs.convert_args(qdict)
            print '</form>'

        print '</body>'
        print '</html>'

    else:

        # If confirm flag is nonzero, delete project and redirect to project list.

        dbutil.delete_project(cnx, id)
        url = 'https://microboone-exp.fnal.gov/cgi-bin/query_projects.py?%s' % \
              dbargs.convert_args(qdict)

        # Generate redirect page.

        print 'Content-type: text/html'
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<head>'
        print '<meta http-equiv="refresh" content="0; url=%s" />' % url
        print '</head>'
        print '<body>'
        print 'Deleted project %s.' % name
        print '<br><br>'
        print 'If page does not automatically reload click this <a href=%s>link</a>' % url
        print '</body>'
        print '</html>'


# End of definitions.  Executable code starts here.

if __name__ == "__main__":

    # Parse arguments.

    argdict = dbargs.get()
    qdict = dbargs.extract_qdict(argdict)
    id = 0
    confirm = 0
    if 'id' in argdict:
        id = int(argdict['id'])
    if 'confirm' in argdict:
        confirm = int(argdict['confirm'])

    # Call main procedure.

    main(id, confirm, qdict)
