#! /usr/bin/python
#==============================================================================
#
# Name: delete_group.py
#
# Purpose: CGI script to delete a project group from database.
#
# CGI arguments:
#
# id      - Group id.
# confirm - Confirm flag.
#           If value is zero, display a confirmation page.
#           If value is nonzero, delete group.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 3-Dec-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(id, confirm, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # Get group name.

    name = dbutil.get_group_name(cnx, id)

    # Check confirm flag.

    if confirm == 0:

        # If confirm flag is zero, generate a confirmation page.

        print 'Content-type: text/html'
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<head>'
        print '<title>Delete Group</title>'
        print '</head>'
        print '<body>'
        if id == 0 or name == '':

            print 'No such group.'

        else:

            print 'Delete group %s?' % name

            # Generate a form with two buttons "Delete" and "Cancel."

            print '<br>'
            print '<form action="%s/delete_group.py?id=%d&confirm=1&%s" method="post">' % \
                (dbconfig.rel_url, id, dbargs.convert_args(qdict))
            print '<input type="submit" value="Delete">'
            print '<input type="submit" value="Cancel" formaction="%s/query_groups.py?%s">' % \
                (dbconfig.rel_url, dbargs.convert_args(qdict))
            print '</form>'

        print '</body>'
        print '</html>'

    else:

        # If confirm flag is nonzero, delete group and redirect to group list.

        dbutil.delete_group(cnx, id)
        url = '%s/query_groups.py?%s' % \
              (dbconfig.base_url, dbargs.convert_args(qdict))

        # Generate redirect page.

        print 'Content-type: text/html'
        print 'Status: 303 See Other'
        print 'Location: %s' % url
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<body>'
        print 'Deleted group %s.' % name
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
