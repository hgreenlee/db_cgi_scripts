#! /usr/bin/python
#==============================================================================
#
# Name: edit_project.py
#
# Purpose: CGI project editor.
#
# CGI arguments:
#
# id - Project id.
# results_per_page - Number of projects to display on each page.
# page - Current page (starts at 1).
#
# Created: 19-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict
import cgi
import cgitb
cgitb.enable()


# Project edit form.

def project_form(cnx, id, results_per_page, current_page, pattern):

    # Query project name from database.

    c = cnx.cursor()
    q = 'SELECT id,name FROM projects WHERE id=%d' % id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch project id %d' % id)
    row = rows[0]
    name = row[1]

    # Generate form.

    print '<h2>Project %s</h2>' % name

    # Add button to insert another stage.

    print '<h2>Stages</h2>'
    print '<form action="/cgi-bin/add_stage.py?id=%d&results_per_page=%d&page=%d&pattern=%s" method="post" target="_blank" rel="noopener noreferer">' % \
        (id, results_per_page, current_page, pattern)
    print '<input type="submit" value="Add Stage">'
    print '</form>'
    print '<br>'

    # Query stage ids belonging to this project.

    q = 'SELECT id, name FROM stages WHERE project_id=%d ORDER BY seqnum' % id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) > 0:

        # Add links to edit project stages.

        print '<table border=1 style="border-collapse:collapse">'
        print '<tr>'
        print '<th>Stage ID</th>'
        print '<th>Stage Name</th>'
        print '</tr>'

        for row in rows:
            print '<tr>'
            stage_id = row[0]
            stage_name = row[1]
            print '<td>%d</td>' % stage_id
            print '<td><a target="_blank" rel="noopener noreferer" href="https://microboone-exp.fnal.gov/cgi-bin/edit_stage.py?id=%d&results_per_page=%d&page=%d&pattern=%s">%s</a></td>' % \
                (stage_id, results_per_page, current_page, pattern, stage_name)

            # Add Clone button/column

            print '<td>'
            print '<form target="_blank" rel="noopener noreferer" action="/cgi-bin/clone_stage.py?id=%d&results_per_page=%d&page=%d&pattern=%s" method="post">' % \
                (stage_id, results_per_page, current_page, pattern)
            print '<input type="submit" value="Clone">'
            print '</form>'
            print '</td>'        

            # Add Delete button/column

            print '<td>'
            print '<form action="/cgi-bin/delete_stage.py?id=%d&results_per_page=%d&page=%d&pattern=%s" method="post">' % \
                (stage_id, results_per_page, current_page, pattern)
            print '<input type="submit" value="Delete">'
            print '</form>'
            print '</td>'        

            # Add Up button/column

            print '<td>'
            print '<form action="/cgi-bin/up_stage.py?id=%d&results_per_page=%d&page=%d&pattern=%s" method="post">' % \
                (stage_id, results_per_page, current_page, pattern)
            print '<input type="submit" value="Up">'
            print '</form>'
            print '</td>'        

            # Add Down button/column

            print '<td>'
            print '<form action="/cgi-bin/down_stage.py?id=%d&results_per_page=%d&page=%d&pattern=%s" method="post">' % \
                (stage_id, results_per_page, current_page, pattern)
            print '<input type="submit" value="Down">'
            print '</form>'
            print '</td>'        

            # Finish row.

            print '</tr>'

        # Finish table.

        print '</table>'

    print '<h2>Project Data</h2>'

    # Query full project from database.

    q = 'SELECT * FROM projects WHERE id=%d' % id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch project id %d' % id)
    row = rows[0]

    print '<form action="/cgi-bin/dbhandler.py" method="post">'

    # Add hidden input field to store table name.

    print '<input type="hidden" id="table" name="table" value="projects">'

    # Loop over fields of this project.
    # Put fields in a table.

    print '<table border=1 style="border-collapse:collapse">'
    cols = databaseDict['projects']
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
    url = 'https://microboone-exp.fnal.gov/cgi-bin/query_projects.py?id=%d&results_per_page=%d&page=%d&pattern=%s' % (id, results_per_page, current_page, pattern)
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
    print '<title>Project Editor</title>'
    print '</head>'
    print '<body>'
    print '<a href=https://microboone-exp.fnal.gov/cgi-bin/query_projects.py?results_per_page=%d&page=%d&pattern=%s>Project list</a><br>' % \
        (results_per_page, current_page, pattern)

    # Generate main parg of html document.

    project_form(cnx, id, results_per_page, current_page, pattern)

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
