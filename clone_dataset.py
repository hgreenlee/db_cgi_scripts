#! /usr/bin/python
#==============================================================================
#
# Name: clone_dataset.py
#
# Purpose: CGI dataset clone.
#
# CGI arguments:
#
# id      - Dataset id.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 19-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs


# Main procedure.

def main(dataset_id, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # Query the project id.
    # This is only needed for the redirect page.

    c = cnx.cursor()
    q = 'SELECT id,project_id FROM datasets WHERE id=%d' % dataset_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch dataset id %d' % dataset_id)
    row = rows[0]
    project_id = row[1]

    # Clone the dataset row.

    clone_id = dbutil.clone_dataset(cnx, dataset_id)

    # Generate redirect html document header to invoke the dataset editor for
    # the newly created document.

    url = '%s/edit_datasets.py?id=%d&%s' % \
          (dbconfig.base_url, project_id, dbargs.convert_args(qdict))

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<meta http-equiv="refresh" content="0; url=%s" />' % url
    print '</head>'
    print '<body>'
    if clone_id > 0:
        print 'Cloned dataset.'
    else:
        print 'Dataset not cloned.'
    print '<br><br>'
    print 'If page does not automatically reload click this <a href=%s>link</a>' % url
    print '</body>'
    print '</html>'


# End of definitions.  Executable code starts here.

if __name__ == "__main__":

    # Parse arguments.

    argdict = dbargs.get()
    qdict = dbargs.extract_qdict(argdict)
    id = 0
    if 'id' in argdict:
        id = int(argdict['id'])

    # Call main procedure.

    main(id, qdict)
