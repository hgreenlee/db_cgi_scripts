#! /usr/bin/python
#==============================================================================
#
# Name: delete_dataset.py
#
# Purpose: CGI script to delete a dataset from database.
#
# CGI arguments:
#
# id      - Dataset id.
# confirm - Confirm flag.
#           If value is zero, display a confirmation page.
#           If value is nonzero, delete dataset.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 16-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(id, confirm, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # Query the dataset name and project id.

    c = cnx.cursor()
    q = 'SELECT id, name, project_id FROM datasets WHERE id=%s'
    c.execute(q, (id,))
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch dataset id %d' % id)
    row = rows[0]
    dataset_name = row[1]
    project_id = row[2]

    # Check confirm flag.

    if confirm == 0:

        # If confirm flag is zero, generate a confirmation page.

        print 'Content-type: text/html'
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<head>'
        print '<title>Delete Dataset</title>'
        print '</head>'
        print '<body>'

        if id == 0:

            print 'No such dataset.'

        else:

            print 'Delete dataset %s?' % dataset_name

            # Generate a form with two buttons "Delete" and "Cancel."

            print '<br>'
            print '<form action="%s/delete_dataset.py?id=%d&confirm=1&%s" method="post">' % \
                (dbconfig.rel_url, id, dbargs.convert_args(qdict))
            print '<input type="submit" value="Delete">'
            print '<input type="submit" value="Cancel" formaction="%s/edit_datasets.py?id=%d&%s">' % \
                (dbconfig.rel_url, project_id, dbargs.convert_args(qdict))
            print '</form>'

        print '</body>'
        print '</html>'

    else:

        # If confirm flag is nonzero, delete dataset and redirect to datasets editor.

        dbutil.delete_dataset(cnx, id)
        url = '%s/edit_datasets.py?id=%d&%s' % \
              (dbconfig.base_url, project_id, dbargs.convert_args(qdict))

        # Generate redirect page.

        print 'Content-type: text/html'
        print 'Status: 303 See Other'
        print 'Location: %s' % url
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<body>'
        print 'Deleted dataset %s.' % dataset_name
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
