#! /usr/bin/python
#==============================================================================
#
# Name: add_stage.py
#
# Purpose: CGI script to add an empty stage.
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
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(id, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False)

    # Add stage and redirect to stage editor.

    stage_id = dbutil.insert_blank_stage(cnx, id)
    url = 'https://microboone-exp.fnal.gov/cgi-bin/db/edit_stage.py?id=%d&%s' % \
          (stage_id, dbargs.convert_args(qdict))

    # Generate redirect page.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<meta http-equiv="refresh" content="0; url=%s" />' % url
    print '</head>'
    print '<body>'
    print 'Add stage.'
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
    id = 0
    if 'id' in argdict:
        id = int(argdict['id'])

    # Call main procedure.

    main(id, qdict)
