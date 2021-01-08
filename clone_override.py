#! /usr/bin/python
#==============================================================================
#
# Name: clone_override.py
#
# Purpose: CGI override clone.
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


# Main procedure.

def main(override_id, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # Query the stage id.

    c = cnx.cursor()
    q = 'SELECT id,stage_id FROM overrides WHERE id=%d' % override_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch override id %d' % override_id)
    row = rows[0]
    stage_id = row[1]

    # Now clone the override.

    clone_id = dbutil.clone_override(cnx, override_id)

    # Generate redirect html document header to invoke the stage editor.

    url = '%s/edit_stage.py?id=%d&%s' % \
          (dbconfig.base_url, stage_id, dbargs.convert_args(qdict))

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<meta http-equiv="refresh" content="0; url=%s" />' % url
    print '</head>'
    print '<body>'
    if clone_id > 0:
        print 'Cloned override.'
    else:
        print 'Override not cloned.'
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
    if 'id' in argdict:
        id = int(argdict['id'])

    # Call main procedure.

    main(id, qdict)
