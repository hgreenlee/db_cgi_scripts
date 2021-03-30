#! /usr/bin/python
#==============================================================================
#
# Name: down_substage.py
#
# Purpose: CGI substage move down.
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

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # Check access.

    if not dbconfig.restricted_access_allowed() and dbutil.restricted_access(cnx, 'substages', substage_id):
        dbutil.restricted_error()

    # Query the stage id and sequence number.

    c = cnx.cursor()
    q = 'SELECT id,stage_id,seqnum FROM substages WHERE id=%s'
    c.execute(q, (substage_id,))
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch substage id %d' % substage_id)
    row = rows[0]
    stage_id = row[1]
    seqnum = row[2]

    # Query the succeeding sequence number

    q = 'SELECT id, stage_id, seqnum FROM substages WHERE stage_id=%s AND seqnum>%s ORDER BY seqnum'
        
    c.execute(q, (stage_id, seqnum))
    rows = c.fetchall()
    if len(rows) > 0:
        row = rows[0]
        next_substage_id = row[0]
        next_seqnum = row[2]

        # Swap sequence numbers.

        q = 'UPDATE substages SET seqnum=%s WHERE id=%s'
        c.execute(q, (next_seqnum, substage_id))
        q = 'UPDATE substages SET seqnum=%s WHERE id=%s'
        c.execute(q, (seqnum, next_substage_id))
        cnx.commit()

    # Generate redirect html document header to invoke the substage editor for
    # the newly created document.

    url = ''
    url = '%s/edit_stage.py?id=%d&%s' % \
          (dbconfig.base_url, stage_id, dbargs.convert_args(qdict))
    print 'Content-type: text/html'
    print 'Status: 303 See Other'
    print 'Location: %s' % url
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<body>'
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
