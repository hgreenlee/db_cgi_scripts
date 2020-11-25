#! /usr/bin/python
#==============================================================================
#
# Name: edit_dataset.py
#
# Purpose: CGI script to add a dataset.
#
# CGI arguments:
#
# id      - Dataset id.
# name    - Dataset name.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 17-Nov-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(dataset_id, dataset_name, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])
    c = cnx.cursor()

    # Query the current dataset name, and project id.

    current_dataset_name = ''
    project_id = 0
    q = 'SELECT name, project_id FROM datasets WHERE id=%d' % dataset_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch dataset id %d' % dataset_id)
    row = rows[0]
    current_dataset_name = row[0]
    project_id = row[1]

    if dataset_name == '':

        # If the argument dataset name is blank, generate a form to edit the name.

        print 'Content-type: text/html'
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<head>'
        print '<title>Edit Dataset</title>'
        print '</head>'
        print '<body>'
        
        # Generate a form with text dialog and two buttons "Save" and "Cancel."

        print '<h2>Edit Dataset Name</h2>'
        print '<form action="/cgi-bin/db/edit_dataset.py" method="post">'

        # Add qdict hidden fields.

        for key in qdict:
            print '<input type="hidden" name="%s" value="%s">' % (dbutil.convert_str(key),
                                                                  dbutil.convert_str(qdict[key]))

        # Add dataset id hidden field.

        print '<input type="hidden" name="id" value="%d">' % dataset_id

        # Add one-line text field for dataset name, pre-filled with current name.
        # This is the only visible and editable field for this form.

        print '<label for="dataset_name">Dataset Name: </label>'
        print '<input type="text" id="dataset_name" name="name" value="%s" size=100>' % \
            current_dataset_name
        print '<br>'

        # Add save and cancel buttons.

        print '<input type="submit" value="Save">'
        print '<input type="submit" value="Cancel" formaction="/cgi-bin/db/edit_datasets.py?id=%d">' % \
        project_id
        print '</form>'
        print '</body>'
        print '</html>'

    else:

        # Check access.

        if not dbconfig.restricted_access_allowed() and dbutil.restricted_access(cnx, 'datasets', dataset_id):
            dbutil.restricted_error()

        # If dataset name argument is not blank, update database and redirect back to datasets page.

        q = 'UPDATE datasets SET name=\'%s\' WHERE id=%d' % (dataset_name, dataset_id)
        c.execute(q)
        cnx.commit()

        # Redirect to dataset list.

        url = 'https://microboone-exp.fnal.gov/cgi-bin/db/edit_datasets.py?id=%d&%s' % \
              (project_id, dbargs.convert_args(qdict))
        print 'Content-type: text/html'
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<head>'
        print '<meta http-equiv="refresh" content="0; url=%s" />' % url
        print '</head>'
        print '<body>'
        print 'Dataset update successful.'
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
    dataset_id = 0
    dataset_name = ''
    if 'id' in argdict:
        dataset_id = int(argdict['id'])
    if 'name' in argdict:
        dataset_name = argdict['name']

    # Call main procedure.

    main(dataset_id, dataset_name, qdict)
