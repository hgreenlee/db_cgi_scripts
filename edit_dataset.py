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
# <qdict> - Standard query_projects.py arguments.
#
# Created: 17-Nov-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict
from dbconfig import pulldowns


# Main procedure.

def dataset_form(cnx, id, qdict):

    # Construct global disabled option for restricted controls.

    disabled = ''
    if not dbconfig.restricted_access_allowed() and dbutil.restricted_access(cnx, 'datasets', id):
        disabled = 'disabled'

    # Query project name and id from database.

    c = cnx.cursor()
    q = 'SELECT id, name, project_id FROM datasets WHERE id=%d' % id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch dataset id %d' % id)
    row = rows[0]
    name = row[1]
    project_id = row[2]
    project_name = dbutil.get_project_name(cnx, project_id)

    # Generate form.

    print '<h2>Project %s</h2>' % project_name
    print '<h2>Datset %s</h2>' % name

    # Query full dataset from database.

    q = 'SELECT %s FROM datasets WHERE id=%d' % (dbutil.columns('datasets'), id)
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch dataset id %d' % id)
    row = rows[0]

    print '<form action="/cgi-bin/db/dbhandler.py" method="post">'

    # Add hidden input field to store table name.

    print '<input type="hidden" id="table" name="table" value="datasets">'

    # Add hidden input field to store save url (parent of this page).

    print '<input type="hidden" id="saveurl" name="saveurl" value="%s/edit_datasets.py?id=%d&%s">' % \
        (dbconfig.base_url, project_id, dbargs.convert_args(qdict))

    # Add hidden qdict input fields.

    for key in qdict:
        print '<input type="hidden" name="%s" value="%s">' % (dbutil.convert_str(key),
                                                              dbutil.convert_str(qdict[key]))
    # Loop over fields of this dataset.
    # Put fields in a table.

    print '<table border=1 style="border-collapse:collapse">'
    cols = databaseDict['datasets']
    for n in range(len(cols)):
        coltup = cols[n]
        colname = coltup[0]
        coltype = coltup[2]
        colarray = coltup[3]
        coldesc = coltup[4]

        if colname != '':

            # Set readonly attribute

            readonly = ''
            if colname == 'id' or colname == 'project_id':
                readonly = 'readonly'
            elif disabled != '':
                readonly = 'readonly'

            print '<tr>'
            print '<td>'
            print '<label for="%s">%s: </label>' % (colname, coldesc)
            print '</td>'
            print '<td>'
            if colarray == 0:

                # Scalar column.

                if coltype[0:3] == 'INT':
                    print '<input type="number" id="%s" name="%s" size=10 value="%d" %s>' % \
                        (colname, colname, row[n], readonly)
                elif coltype[0:6] == 'DOUBLE':
                    print '<input type="text" id="%s" name="%s" size=100 value="%8.6f" %s>' % \
                        (colname, colname, row[n], readonly)
                elif coltype[0:7] == 'VARCHAR':
                    if colname in pulldowns:
                        print '<select id="%s" name="%s" size=0 %s>' % (colname, colname, disabled)
                        for value in pulldowns[colname]:
                            sel = ''
                            if value == row[n]:
                                sel = 'selected'
                            print '<option value="%s" %s>%s</option>' % (value, sel, value)
                        print '</select>'
                    else:
                        print '<input type="text" id="%s" name="%s" size=100 value="%s" %s>' % \
                            (colname, colname, row[n], readonly)

            else:

                # Array columns.
                # Display using multiline <textarea>.

                strs = dbutil.get_strings(cnx, row[n])
                print '<textarea id="%s" name="%s" rows=%d cols=80 %s>' % \
                    (colname, colname, max(len(strs), 1), readonly)
                print '\n'.join(strs)
                print '</textarea>'

            print '</td>'
            print '</tr>'

    # Finish table.

    print '</table>'

    # Add "Save" and "Back" buttons.

    print '<input type="submit" name="submit" value="Save" %s>' % disabled
    print '<input type="submit" name="submit" value="Update" %s>' % disabled
    print '<input type="submit" name="submit" value="Back">'
    print '</form>'

    # Done.

    return

# Main procedure.

def main(id, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # Generate html document header.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<title>Dataset Editor</title>'
    print '</head>'
    print '<body>'
    print '<a href=%s/query_projects.py?%s>Project list</a><br>' % \
        (dbconfig.base_url, dbargs.convert_args(qdict))

    # Generate main parg of html document.

    dataset_form(cnx, id, qdict)

    # Generate html document trailer.
    
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
