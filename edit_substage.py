#! /usr/bin/python
#==============================================================================
#
# Name: edit_substage.py
#
# Purpose: CGI stage editor.
#
# CGI arguments:
#
# id               - Subtage id.
# results_per_page - Number of stages to display on each page.
# page             - Current page (starts at 1).
# pattern          - Search pattern.
#
# Created: 19-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Stage edit form.

def substage_form(cnx, id, results_per_page, current_page, pattern):

    # Query substage from database.

    c = cnx.cursor()
    q = 'SELECT * FROM substages WHERE id=%d' % id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch substage id %d' % id)
    row = rows[0]
    fclname = row[1]
    stage_id = row[2]

    # Query stage name and project id.

    q = 'SELECT id, name, project_id FROM stages WHERE id=%d' % stage_id
    c.execute(q)
    stage_rows = c.fetchall()
    if len(stage_rows) == 0:
        raise IOError('Unable to fetch stage id %d' % stage_id)
    stage_row = stage_rows[0]
    stage_name = stage_row[1]
    project_id = stage_row[2]
    project_name = dbutil.get_project_name(cnx, project_id)

    # Generate form.

    print '<h2>Project %s</h2>' % project_name
    print '<h2>Stage %s</h2>' % stage_name
    print '<h2>FCL %s</h2>' % fclname
    print '<form action="/cgi-bin/dbhandler.py" method="post">'

    # Add hidden input field to store table name.

    print '<input type="hidden" id="table" name="table" value="substages" %s>'

    # Loop over fields of this stage.
    # Put fields in a table.

    print '<table border=1 style="border-collapse:collapse">'
    cols = databaseDict['substages']
    for n in range(len(cols)):
        coltup = cols[n]
        colname = coltup[0]
        coltype = coltup[2]
        colarray = coltup[3]
        coldesc = coltup[4]

        if colname != '':

            # Set readonly attribute

            readonly = ''
            if colname == 'id':
                readonly = 'readonly'

            print '<tr>'
            print '<td>'
            print '<label for="%s">%s:</label>' % (colname, coldesc)
            print '</td>'
            print '<td>'
            if colarray == 0:

                # Scalar column.

                if coltype[0:3] == 'INT':
                    print '<input type="number" id="%s" name="%s" size=80 value="%d" %s>' % \
                        (colname, colname, row[n], readonly)
                elif coltype[0:6] == 'DOUBLE':
                    print '<input type="text" id="%s" name="%s" size=80 value="%8.6f">' % \
                        (colname, colname, row[n])
                elif coltype[0:7] == 'VARCHAR':
                    print '<input type="text" id="%s" name="%s" size=80 value="%s">' % \
                        (colname, colname, row[n])

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
    url = 'https://microboone-exp.fnal.gov/cgi-bin/edit_stage.py?id=%d&results_per_page=%d&page=%d&pattern=%s' % (stage_id, results_per_page, current_page, pattern)
    print '<input type="button" value="Back" onclick="window.open(\'%s\',\'_self\')">' % url
    print '</form>'


# Main procedure.

def main(id, results_per_page, current_page, pattern):

    # Open database connection.

    cnx = dbconfig.connect(readonly = True)

    # Generate html document header.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<title>Substage Editor</title>'
    print '</head>'
    print '<body>'
    print '<a href=https://microboone-exp.fnal.gov/cgi-bin/query_projects.py?results_per_page=%d&page=%d&pattern=%s>Project list</a><br>' % \
        (results_per_page, current_page, pattern)

    # Generate main parg of html document.

    substage_form(cnx, id, results_per_page, current_page, pattern)

    # Generate html document trailer.
    
    print '</body>'
    print '</html>'


# End of definitions.  Executable code starts here.

if __name__ == "__main__":

    # Parse arguments.

    
    id = 0
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
