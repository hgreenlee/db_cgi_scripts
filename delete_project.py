#! /usr/bin/python
#==============================================================================
#
# Name: delete_project.py
#
# Purpose: CGI script to delete a project from database.
#
# CGI arguments:
#
# id - Project id.
# confirm - Confirm flag.  If value is zero, display a confirmation page.
#           If value is nonzero, delete project.
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

    # Get project name.

    name = dbutil.get_project_name(cnx, id)

    # Check confirm flag.

    if confirm == 0:

        # If confirm flag is zero, generate a confirmation page.

        print 'Content-type: text/html'
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<head>'
        print '<title>Delete Project</title>'
        print '</head>'
        print '<body>'
        if id == 0 or name == '':

            print 'No such project.'

        else:

            print 'Delete project %s?' % name

            # Generate a form with two buttons "Delete" and "Cancel."

            print '<br>'
            print '<form action="/cgi-bin/delete_project.py?id=%d&confirm=1&results_per_page=%d&page=%d&pattern=%s" method="post">' % \
                (id, results_per_page, current_page, pattern)
            print '<input type="submit" value="Delete">'
            url = 'https://microboone-exp.fnal.gov/cgi-bin/query_projects.py?id=%d&results_per_page=%d&page=%d&pattern=%s' % (id, results_per_page, current_page, pattern)
            print '<input type="button" value="Cancel" onclick="window.open(\'%s\',\'_self\')">' % url
            print '</form>'

        print '</body>'
        print '</html>'

    else:

        # If confirm flag is nonzero, delete project and generate an information page/form.

        dbutil.delete_project(cnx, id)
        url = 'https://microboone-exp.fnal.gov/cgi-bin/query_projects.py?results_per_page=%d&page=%d&pattern=%s' % \
              (results_per_page, current_page, pattern)

        # Generate redirect page.

        print 'Content-type: text/html'
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<head>'
        print '<meta http-equiv="refresh" content="0; url=%s" />' % url
        print '</head>'
        print '<body>'
        print 'Deleted project %s.' % name
        print '<br><br>'
        print 'If page does not automatically reload click this <a href=%s>link</a>' % url
        print '</body>'
        print '</html>'

    # Generate html document trailer.
    

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
