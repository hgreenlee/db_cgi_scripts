#! /usr/bin/python
#==============================================================================
#
# Name: clone_substage.py
#
# Purpose: CGI substage clone.
#
# CGI arguments:
#
# id      - Substage id.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 19-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs


# Main procedure.

def main(substage_id, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False)

    # Query the stage id.

    c = cnx.cursor()
    q = 'SELECT id,fclname,stage_id FROM substages WHERE id=%d' % substage_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch substage id %d' % substage_id)
    row = rows[0]
    fclname = row[1]
    stage_id = row[2]    

    # Now clone the substage.

    clone_id = dbutil.clone_substage(cnx, substage_id, stage_id)

    # Generate redirect html document header to invoke the substage editor for
    # the newly created document.

    url = ''
    if clone_id > 0:
        url = 'https://microboone-exp.fnal.gov/cgi-bin/edit_substage.py?id=%d&%s' % \
              (clone_id, dbargs.convert_args(qdict))
    else:
        url = 'https://microboone-exp.fnal.gov/cgi-bin/edit_stage.py?id=%d&%s' % \
              (stage_id, dbargs.convert_args(qdict))

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<meta http-equiv="refresh" content="0; url=%s" />' % url
    print '</head>'
    print '<body>'
    if clone_id > 0:
        print 'Cloned substage %s' % fclname
    else:
        print 'Substage not cloned.'
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
