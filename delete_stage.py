#! /usr/bin/python
#==============================================================================
#
# Name: delete_stage.py
#
# Purpose: CGI script to delete a stage from database.
#
# CGI arguments:
#
# id      - Stage id.
# confirm - Confirm flag.
#           If value is zero, display a confirmation page.
#           If value is nonzero, delete stage.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 15-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(id, confirm, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # Query the stage name and project id.

    c = cnx.cursor()
    q = 'SELECT id,name,project_id FROM stages WHERE id=%d' % id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch stage id %d' % id)
    row = rows[0]
    stage_name = row[1]
    project_id = row[2]

    # Check confirm flag.

    if confirm == 0:

        # If confirm flag is zero, generate a confirmation page.

        print 'Content-type: text/html'
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<head>'
        print '<title>Delete Stage</title>'
        print '</head>'
        print '<body>'

        if id == 0 or stage_name == '':

            print 'No such stage.'

        else:

            print 'Delete stage %s?' % stage_name

            # Generate a form with two buttons "Delete" and "Cancel."

            print '<br>'
            print '<form action="/cgi-bin/db/delete_stage.py?id=%d&confirm=1&%s" method="post">' % \
                (id, dbargs.convert_args(qdict))
            print '<input type="submit" value="Delete">'
            print '<input type="submit" value="Cancel" formaction="/cgi-bin/db/edit_project.py?id=%d&%s">' % \
                (project_id, dbargs.convert_args(qdict))
            print '</form>'

        print '</body>'
        print '</html>'

    else:

        # If confirm flag is nonzero, delete stage and redirect to project editor.

        dbutil.delete_stage(cnx, id)
        url = '%s/edit_project.py?id=%d&%s' % \
              (dbconfig.base_url, project_id, dbargs.convert_args(qdict))

        # Generate redirect page.

        print 'Content-type: text/html'
        print 'Status: 303 See Other'
        print 'Location: %s' % url
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<body>'
        print 'Deleted stage %s.' % stage_name
        print '<br><br>'
        print 'If page does not automatically reload click this <a href=%s>link</a>' % url
        print '</body>'
        print '</html>'

        # Done.

        return

# End of definitions.  Executable code starts here.

if __name__ == "__main__":

    # Parse arguments.

    argdict = dbargs.get()
    qdict = dbargs.extract_qdict(argdict)
    id = 0
    confirm = 0
    if 'id' in argdict:
        id = int(argdict['id'])
    if 'confirm' in argdict:
        confirm = int(argdict['confirm'])

    # Call main procedure.

    main(id, confirm, qdict)
