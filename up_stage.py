#! /usr/bin/python
#==============================================================================
#
# Name: up_stage.py
#
# Purpose: CGI stage move up.
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

    # Query the project id and sequence number.

    c = cnx.cursor()
    q = 'SELECT id,project_id,seqnum FROM stages WHERE id=%d' % stage_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch stage id %d' % stage_id)
    row = rows[0]
    project_id = row[1]
    seqnum = row[2]

    # Query the preceding sequence number

    q = 'SELECT id, project_id, seqnum FROM stages WHERE project_id=%d AND seqnum<%d ORDER BY seqnum DESC' % \
        (project_id, seqnum)
        
    c.execute(q)
    rows = c.fetchall()
    if len(rows) > 0:
        row = rows[0]
        prev_stage_id = row[0]
        prev_seqnum = row[2]

        # Swap sequence numbers.

        q = 'UPDATE stages SET seqnum=%d WHERE id=%d' % (prev_seqnum, stage_id)
        c.execute(q)
        q = 'UPDATE stages SET seqnum=%d WHERE id=%d' % (seqnum, prev_stage_id)
        c.execute(q)
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
