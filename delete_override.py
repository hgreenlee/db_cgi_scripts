#! /usr/bin/python
#==============================================================================
#
# Name: delete_override.py
#
# Purpose: CGI script to delete an override from database.
#
# CGI arguments:
#
# id      - Override id.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 7-Jan-2021  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(id, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # Query the stage id.

    c = cnx.cursor()
    q = 'SELECT id,stage_id FROM overrides WHERE id=%d' % id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch override id %d' % id)
    row = rows[0]
    stage_id = row[1]

    # Delete override and redirect to stage editor.

    dbutil.delete_override(cnx, id)
    url = '%s/edit_stage.py?id=%d&%s' % \
          (dbconfig.base_url, stage_id, dbargs.convert_args(qdict))

    # Generate redirect page.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<meta http-equiv="refresh" content="0; url=%s" />' % url
    print '</head>'
    print '<body>'
    print 'Deleted override.'
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
