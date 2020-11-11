#! /usr/bin/python
#==============================================================================
#
# Name: delete_substage.py
#
# Purpose: CGI script to delete a substage from database.
#
# CGI arguments:
#
# id - Substage id.
# confirm - Confirm flag.  If value is zero, display a confirmation page.
#           If value is nonzero, delete substage.
# results_per_page - Number of projects to display on each page.
# page - Current page (starts at 1).
#
# Created: 15-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(id, confirm, results_per_page, current_page, pattern):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False)

    # Query the fclname and stage id.

    c = cnx.cursor()
    q = 'SELECT id,fclname,stage_id FROM substages WHERE id=%d' % id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch substage id %d' % id)
    row = rows[0]
    fclname = row[1]
    stage_id = row[2]

    # Check confirm flag.

    if confirm == 0:

        # If confirm flag is zero, generate a confirmation page.

        print 'Content-type: text/html'
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<head>'
        print '<title>Delete Substage</title>'
        print '</head>'
        print '<body>'

        if id == 0 or fclname == '':

            print 'No such substage.'

        else:

            print 'Delete substage %s?' % fclname

            # Generate a form with two buttons "Delete" and "Cancel."

            print '<br>'
            print '<form action="/cgi-bin/delete_substage.py?id=%d&confirm=1&results_per_page=%d&page=%d&pattern=%s" method="post">' % \
                (id, results_per_page, current_page, pattern)
            print '<input type="submit" value="Delete">'
            url = 'https://microboone-exp.fnal.gov/cgi-bin/edit_stage.py?id=%d&results_per_page=%d&page=%d&pattern=%s' % (stage_id, results_per_page, current_page, pattern)
            print '<input type="button" value="Cancel" onclick="window.open(\'%s\',\'_self\')">' % url
            print '</form>'

        print '</body>'
        print '</html>'

    else:

        # If confirm flag is nonzero, delete substage and redirect to stage editor.

        dbutil.delete_substage(cnx, id)
        url = 'https://microboone-exp.fnal.gov/cgi-bin/edit_stage.py?id=%d&results_per_page=%d&page=%d&pattern=%s' % \
              (stage_id, results_per_page, current_page, pattern)

        # Generate redirect page.

        print 'Content-type: text/html'
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<head>'
        print '<meta http-equiv="refresh" content="0; url=%s" />' % url
        print '</head>'
        print '<body>'
        print 'Deleted substage %s.' % fclname
        print '<br><br>'
        print 'If page does not automatically reload click this <a href=%s>link</a>' % url
        print '</body>'
        print '</html>'

        # Done.

        return

# End of definitions.  Executable code starts here.

if __name__ == "__main__":

    # Parse arguments.

    
    id = 0
    confirm = 0
    results_per_page = 20
    current_page = 1
    pattern = ''
    args = dbargs.get()
    if 'id' in args:
        id = int(args['id'])
    if 'confirm' in args:
        confirm = int(args['id'])
    if 'results_per_page' in args:
        results_per_page = int(args['results_per_page'])
    if 'page' in args:
        current_page = int(args['page'])
    if 'pattern' in args:
        pattern = args['pattern']

    # Call main procedure.

    main(id, confirm, results_per_page, current_page, pattern)
