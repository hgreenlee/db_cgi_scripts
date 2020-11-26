#! /usr/bin/python
#==============================================================================
#
# Name: up_dataset.py
#
# Purpose: CGI dataset move up.
#
# CGI arguments:
#
# id      - Dataset id.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 19-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs


# Main procedure.

def main(dataset_id, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # Check access.

    if not dbconfig.restricted_access_allowed() and dbutil.restricted_access(cnx, 'datasets', dataset_id):
        dbutil.restricted_error()

    # Query the project id, dataset type, and sequence number.

    c = cnx.cursor()
    q = 'SELECT id,project_id,type,seqnum FROM datasets WHERE id=%d' % dataset_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch dataset id %d' % dataset_id)
    row = rows[0]
    project_id = row[1]
    dataset_type = row[2]
    seqnum = row[3]

    # Query the preceding sequence number

    q = 'SELECT id, project_id, type, seqnum FROM datasets WHERE project_id=%d AND type=\'%s\' AND seqnum<%d ORDER BY seqnum DESC' % \
        (project_id, dataset_type, seqnum)
        
    c.execute(q)
    rows = c.fetchall()
    if len(rows) > 0:
        row = rows[0]
        prev_dataset_id = row[0]
        prev_seqnum = row[3]

        # Swap sequence numbers.

        q = 'UPDATE datasets SET seqnum=%d WHERE id=%d' % (prev_seqnum, dataset_id)
        c.execute(q)
        q = 'UPDATE datasets SET seqnum=%d WHERE id=%d' % (seqnum, prev_dataset_id)
        c.execute(q)
        cnx.commit()

    # Generate redirect html document header to invoke the dataset editor for
    # the newly created document.

    url = '%s/edit_datasets.py?id=%d&%s' % \
          (dbconfig.base_url, project_id, dbargs.convert_args(qdict))
    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<meta http-equiv="refresh" content="0; url=%s" />' % url
    print '</head>'
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
