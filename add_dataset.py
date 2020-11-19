#! /usr/bin/python
#==============================================================================
#
# Name: add_dataset.py
#
# Purpose: CGI script to add a dataset.
#
# CGI arguments:
#
# id      - Project id.
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

def main(project_id, dataset_name, dataset_type, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False)
    c = cnx.cursor()

    if dataset_name == '':

        # If dataset name is empty, generate a dialog to query the dataset name.

        print 'Content-type: text/html'
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<head>'
        print '<title>Add Dataset</title>'
        print '</head>'
        print '<body>'
        
        # Generate a form with file dialog and two buttons "Import" and "Cancel."

        print '<h2>Add %s dataset</h2>' % dataset_type
        print '<form action="/cgi-bin/add_dataset.py" method="post">'
        for key in qdict:
            print '<input type="hidden" name="%s" value="%s">' % (dbutil.convert_str(key),
                                                                  dbutil.convert_str(qdict[key]))
        print '<input type="hidden" name="id" value=%d>' % project_id
        print '<input type="hidden" name="type" value=\'%s\'>' % dataset_type
        print '<label for="dataset_name">Dataset Name</label>'
        print '<input type="text" id="dataset_name" name="name">'
        print '<br>'
        print '<input type="submit" value="Add">'
        print '<input type="submit" value="Cancel" formaction="/cgi-bin/edit_datasets.py">'
        print '</form>'
        print '</body>'
        print '</html>'

    else:

        # Maybe insert dataset.

        dataset_id = dbutil.add_dataset(cnx, project_id, dataset_type, dataset_name)
        if dataset_id == 0:

            # This dataset name is already used.
            # Generate informative page.

            url = 'https://microboone-exp.fnal.gov/cgi-bin/edit_datasets.py?id=%d&%s' % \
                  (project_id, dbargs.convert_args(qdict))
            print 'Content-type: text/html'
            print
            print '<!DOCTYPE html>'
            print '<html>'
            print '<head>'
            print '<title>Add Dataset</title>'
            print '</head>'
            print '<body>'
            print 'Dataset with same name is already in database.'
            print '<br><br>'
            print '<a href=%s>Return to dataset list</a>.' % url
            print '</body>'
            print '</html>'
            return

        else:

            # Insert succeeded.
            # Redirect to dataset list.

            url = 'https://microboone-exp.fnal.gov/cgi-bin/edit_datasets.py?id=%d&%s' % \
                  (project_id, dbargs.convert_args(qdict))
            print 'Content-type: text/html'
            print
            print '<!DOCTYPE html>'
            print '<html>'
            print '<head>'
            print '<meta http-equiv="refresh" content="0; url=%s" />' % url
            print '</head>'
            print '<body>'
            print 'Dataset addition successful.'
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
    project_id = 0
    dataset_name = ''
    dataset_type = ''
    if 'id' in argdict:
        project_id = int(argdict['id'])
    if 'name' in argdict:
        dataset_name = argdict['name'].strip()
    if 'type' in argdict:
        dataset_type = argdict['type']

    # Call main procedure.

    main(project_id, dataset_name, dataset_type, qdict)
