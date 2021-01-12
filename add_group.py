#! /usr/bin/python
#==============================================================================
#
# Name: add_group.py
#
# Purpose: CGI script to add a project group.
#
# CGI arguments:
#
# <qdict> - Standard query_groups.py arguments.
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

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # Add group and redirect to group editor.

    group_id = dbutil.insert_blank_group(cnx)
    url = '%s/edit_group.py?id=%d&%s' % \
          (dbconfig.base_url, group_id, dbargs.convert_args(qdict))

    # Generate redirect page.

    print 'Content-type: text/html'
    print 'Status: 303 See Other'
    print 'Location: %s' % url
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<body>'
    print 'Add group.'
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
