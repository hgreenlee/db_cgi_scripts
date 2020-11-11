#! /usr/bin/python
#==============================================================================
#
# Name: add_substage.py
#
# Purpose: CGI script to add an empty substage.
#
# CGI arguments:
#
# id - Stage id.
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

def main(id, results_per_page, current_page):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False)

    # Add substage and redirect to substage editor.

    substage_id = dbutil.insert_blank_substage(cnx, id)
    url = 'https://microboone-exp.fnal.gov/cgi-bin/edit_substage.py?id=%d&results_per_page=%d&page=%d' % \
          (substage_id, results_per_page, current_page)

    # Generate redirect page.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<meta http-equiv="refresh" content="0; url=%s" />' % url
    print '</head>'
    print '<body>'
    print 'Add substage.'
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
