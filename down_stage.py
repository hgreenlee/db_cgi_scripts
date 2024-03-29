#! /usr/bin/python
#==============================================================================
#
# Name: down_stage.py
#
# Purpose: CGI stage move down.
#
# CGI arguments:
#
# id      - Stage id.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 19-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs


# Main procedure.

def main(stage_id, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # Check access.

    if not dbconfig.restricted_access_allowed() and dbutil.restricted_access(cnx, 'stages', stage_id):
        dbutil.restricted_error()

    # Query the stage id and sequence number.

    c = cnx.cursor()
    q = 'SELECT id,project_id,seqnum FROM stages WHERE id=%s'
    c.execute(q, (stage_id,))
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch stage id %d' % stage_id)
    row = rows[0]
    project_id = row[1]
    seqnum = row[2]

    # Query the succeeding sequence number

    q = 'SELECT id, project_id, seqnum FROM stages WHERE project_id=%s AND seqnum>%s ORDER BY seqnum'
        
    c.execute(q, (project_id, seqnum))
    rows = c.fetchall()
    if len(rows) > 0:
        row = rows[0]
        next_stage_id = row[0]
        next_seqnum = row[2]

        # Swap sequence numbers.

        q = 'UPDATE stages SET seqnum=%s WHERE id=%s'
        c.execute(q, (next_seqnum, stage_id))
        q = 'UPDATE stages SET seqnum=%s WHERE id=%s'
        c.execute(q, (seqnum, next_stage_id))
        cnx.commit()

    # Generate redirect html document header to invoke the stage editor for
    # the newly created document.

    url = '%s/edit_project.py?id=%d&%s' % \
          (dbconfig.base_url, project_id, dbargs.convert_args(qdict))
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
