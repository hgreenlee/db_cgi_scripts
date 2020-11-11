#! /usr/bin/python
#==============================================================================
#
# Name: clone_stage.py
#
# Purpose: CGI stage clone.
#
# CGI arguments:
#
# id               - Stage id.
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

def main(stage_id, results_per_page, current_page, pattern):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False)

    # Query the stage name and project id.

    c = cnx.cursor()
    q = 'SELECT id,name,project_id FROM stages WHERE id=%d' % stage_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch stage id %d' % stage_id)
    row = rows[0]
    stage_name = row[1]
    project_id = row[2]    

    # Now clone the stage.

    clone_id = dbutil.clone_stage(cnx, stage_id, project_id)

    # Generate redirect html document header to invoke the stage editor for
    # the newly created document.

    url = ''
    if clone_id > 0:
        url = 'https://microboone-exp.fnal.gov/cgi-bin/edit_stage.py?id=%d&results_per_page=%d&page=%d&pattern=%s' % \
              (clone_id, results_per_page, current_page, pattern)
    else:
        url = 'https://microboone-exp.fnal.gov/cgi-bin/edit_project.py?id=%d&results_per_page=%d&page=%d&pattern=%s' % \
              (project_id,results_per_page, current_page, pattern)

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<meta http-equiv="refresh" content="0; url=%s" />' % url
    print '</head>'
    print '<body>'
    if clone_id > 0:
        print 'Cloned stage %s' % stage_name
    else:
        print 'stage not cloned.'
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
