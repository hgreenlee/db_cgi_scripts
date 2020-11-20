#! /usr/bin/python
#==============================================================================
#
# Name: edit_stage.py
#
# Purpose: CGI stage editor.
#
# CGI arguments:
#
# id               - Stage id.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 19-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Stage edit form.

def stage_form(cnx, id, qdict):

    # Query project name and id from database.

    c = cnx.cursor()
    q = 'SELECT id, name, project_id FROM stages WHERE id=%d' % id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch stage id %d' % id)
    row = rows[0]
    name = row[1]
    project_id = row[2]
    project_name = dbutil.get_project_name(cnx, project_id)

    # Generate form.

    print '<h2>Project %s</h2>' % project_name
    print '<h2>Stage %s</h2>' % name

    # Add button to insert another substage.

    print '<h2>Substages</h2>'
    print '<form action="/cgi-bin/add_substage.py?id=%d&%s" method="post" target="_blank" rel="noopener noreferer">' % \
        (id, dbargs.convert_args(qdict))
    print '<input type="submit" value="Add Substage">'
    print '</form>'
    print '<br>'

    # Query substage ids belonging to this stage.

    q = 'SELECT id, fclname FROM substages WHERE stage_id=%d ORDER BY seqnum' % id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) > 0:

        # Add links to edit project stages.

        print '<table border=1 style="border-collapse:collapse">'
        print '<tr>'
        print '<th>&nbsp;Substage ID&nbsp;</th>'
        print '<th>&nbsp;FCL&nbsp;</th>'
        print '</tr>'

        for row in rows:
            print '<tr>'
            substage_id = row[0]
            fclname = row[1]
            print '<td align="center">%d</td>' % substage_id
            print '<td>&nbsp;<a target="_blank" rel="noopener noreferer" href="https://microboone-exp.fnal.gov/cgi-bin/edit_substage.py?id=%d&%s">%s</a>&nbsp;</td>' % \
                (substage_id, dbargs.convert_args(qdict), fclname)

            # Add Clone button/column

            print '<td>'
            print '<form target="_blank" rel="noopener noreferer" action="/cgi-bin/clone_substage.py?id=%d&%s" method="post">' % \
                (substage_id, dbargs.convert_args(qdict))
            print '<input type="submit" value="Clone">'
            print '</form>'
            print '</td>'        

            # Add Delete button/column

            print '<td>'
            print '<form action="/cgi-bin/delete_substage.py?id=%d&%s" method="post">' % \
                (substage_id, dbargs.convert_args(qdict))
            print '<input type="submit" value="Delete">'
            print '</form>'
            print '</td>'        

            # Add Up button/column

            print '<td>'
            print '<form action="/cgi-bin/up_substage.py?id=%d&%s" method="post">' % \
                (substage_id, dbargs.convert_args(qdict))
            print '<input type="submit" value="Up">'
            print '</form>'
            print '</td>'        

            # Add Down button/column

            print '<td>'
            print '<form action="/cgi-bin/down_substage.py?id=%d&%s" method="post">' % \
                (substage_id, dbargs.convert_args(qdict))
            print '<input type="submit" value="Down">'
            print '</form>'
            print '</td>'        

            # Finish row.

            print '</tr>'

        # Finish table.

        print '</table>'

    print '<h2>Stage Data</h2>'

    # Query full stage from database.

    q = 'SELECT * FROM stages WHERE id=%d' % id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch stage id %d' % id)
    row = rows[0]

    print '<form action="/cgi-bin/dbhandler.py" method="post">'

    # Add hidden input field to store table name.

    print '<input type="hidden" id="table" name="table" value="stages">'

    # Loop over fields of this stage.
    # Put fields in a table.

    print '<table border=1 style="border-collapse:collapse">'
    cols = databaseDict['stages']
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
                    print '<input type="text" id="%s" name="%s" size=100 value="%8.6f">' % \
                        (colname, colname, row[n])
                elif coltype[0:7] == 'VARCHAR':
                    print '<input type="text" id="%s" name="%s" size=100 value="%s">' % \
                        (colname, colname, row[n])

                    # Add datasets.

                    if (colname == 'defname' or colname == 'ana_defname') and row[n] != '':
                        dbutil.add_dataset(cnx, project_id, 'output', row[n])
                    if colname == 'inputdef' and row[n] != '':
                        dbutil.add_dataset(cnx, project_id, 'input', row[n])

            else:

                # Array columns.
                # Display using multiline <textarea>.

                strs = dbutil.get_strings(cnx, row[n])
                print '<textarea id="%s" name="%s" rows=%d cols=80>' % \
                    (colname, colname, max(len(strs), 1))
                print '\n'.join(strs)
                print '</textarea>'

            print '</td>'
            print '</tr>'

    # Finish table.

    print '</table>'

    # Add "Save" and "Back" buttons.

    print '<input type="submit" value="Save">'
    print '<input type="submit" value="Back" formaction="/cgi-bin/edit_project.py?id=%d&%s">' % \
        (project_id, dbargs.convert_args(qdict))
    print '</form>'




# Main procedure.

def main(id, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False)

    # Generate html document header.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<title>Stage Editor</title>'
    print '</head>'
    print '<body>'
    print '<a href=https://microboone-exp.fnal.gov/cgi-bin/query_projects.py?%s>Project list</a><br>' % \
        dbargs.convert_args(qdict)

    # Generate main parg of html document.

    stage_form(cnx, id, qdict)

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
