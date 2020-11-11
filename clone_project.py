#! /usr/bin/python
#==============================================================================
#
# Name: clone_project.py
#
# Purpose: CGI project clone.
#
# CGI arguments:
#
# id               - Project id.
# results_per_page - Number of projects to display on each page.
# page             - Current page (starts at 1).
# pattern          - Search pattern.
#
# Created: 19-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs


# Main procedure.

def main(project_id, results_per_page, current_page, pattern):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False)

    # Get original project name.

    project_name = dbutil.get_project_name(cnx, project_id)
    clone_id = 0

    if project_name != '':

        # Generate first candidate clone project name.

        clone_project_name = 'Clone of %s' % project_name

        # Check whether this project name is already used.

        dup_id = dbutil.get_project_id(cnx, clone_project_name)

        # Modify project name until we find one that isn't alrady used.

        ntry = 1
        while dup_id > 0:
            ntry += 1
            clone_project_name = 'Clone %d of %s' % (ntry, project_name)
            dup_id = dbutil.get_project_id(cnx, clone_project_name)

        # Now clone the project.

        clone_id = dbutil.clone_project(cnx, project_id, clone_project_name)

    # Generate redirect html document header to invoke the project editor for
    # the newly created document.

    url = ''
    if clone_id > 0:
        url = 'https://microboone-exp.fnal.gov/cgi-bin/edit_project.py?id=%d&results_per_page=%d&page=%d&pattern=%s' % \
              (clone_id, results_per_page, current_page, pattern)
    else:
        url = 'https://microboone-exp.fnal.gov/cgi-bin/query_projects.py?results_per_page=%d&page=%d&pattern=%s' % \
              (results_per_page, current_page, pattern)

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<meta http-equiv="refresh" content="0; url=%s" />' % url
    print '</head>'
    print '<body>'
    url = ''
    if clone_id > 0:
        print 'Cloned project %s' % project_name
    else:
        print 'Project not cloned.'
    print '<br><br>'
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
