#! /usr/bin/python
#==============================================================================
#
# Name: up_substage.py
#
# Purpose: CGI substage move up.
#
# CGI arguments:
#
# id               - Substage id.
# results_per_page - Number of projects to display on each page.
# page             - Current page (starts at 1).
#
# Created: 19-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs


# Main procedure.

def main(substage_id, results_per_page, current_page):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False)

    # Query the stage id and sequence number.

    c = cnx.cursor()
    q = 'SELECT id,stage_id,seqnum FROM substages WHERE id=%d' % substage_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch substage id %d' % substage_id)
    row = rows[0]
    stage_id = row[1]
    seqnum = row[2]

    # Query the preceding sequence number

    q = 'SELECT id, stage_id, seqnum FROM substages WHERE stage_id=%d AND seqnum<%d ORDER BY seqnum DESC' % \
        (stage_id, seqnum)
        
    c.execute(q)
    rows = c.fetchall()
    if len(rows) > 0:
        row = rows[0]
        prev_substage_id = row[0]
        prev_seqnum = row[2]

        # Swap sequence numbers.

        q = 'UPDATE substages SET seqnum=%d WHERE id=%d' % (prev_seqnum, substage_id)
        c.execute(q)
        q = 'UPDATE substages SET seqnum=%d WHERE id=%d' % (seqnum, prev_substage_id)
        c.execute(q)
        cnx.commit()

    # Generate redirect html document header to invoke the substage editor for
    # the newly created document.

    url = ''
    url = 'https://microboone-exp.fnal.gov/cgi-bin/edit_stage.py?id=%d&results_per_page=%d&page=%d' % \
          (stage_id, results_per_page, current_page)
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

    id = 0
    name = ''
    results_per_page = 20
    current_page = 1
    pattern = ''
    args = dbargs.get()
    if 'id' in args:
        id = int(args['id'])
    if 'results_per_page' in args:
        results_per_page = int(args['results_per_page'])
    if 'page' in args:
        current_page = int(args['page'])
    if 'pattern' in args:
        pattern = args['pattern']

    # Call main procedure.

    main(id, results_per_page, current_page, pattern)
