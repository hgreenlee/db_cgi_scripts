#! /usr/bin/python
#==============================================================================
#
# Name: edit_override.py
#
# Purpose: CGI override editor.
#
# CGI arguments:
#
# id      - Override id.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 7-Jan-2021  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Override edit form.

def override_form(cnx, id, qdict):

    # Construct global disabled option for restricted controls.

    disabled = ''
    if not dbconfig.restricted_access_allowed() and dbutil.restricted_access(cnx, 'overrides', id):
        disabled = 'disabled'

    # Query override from database.

    c = cnx.cursor()
    q = 'SELECT stage_id,name,value FROM overrides WHERE id=%d' % id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch override id %d' % id)
    row = rows[0]
    stage_id = row[0]
    name = row[1]
    value = row[2]

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
    print '<h2>Override %s</h2>' % name
    print '<form action="/cgi-bin/db/dbhandler.py" method="post">'

    # Add hidden input field to store table name.

    print '<input type="hidden" id="table" name="table" value="overrides">'

    # Add hidden input field to store save url (parent of this page).

    print '<input type="hidden" id="saveurl" name="saveurl" value="%s/edit_stage.py?id=%d&%s">' % \
        (dbconfig.base_url, stage_id, dbargs.convert_args(qdict))

    # Add hidden qdict input fields.

    for key in qdict:
        print '<input type="hidden" name="%s" value="%s">' % (dbutil.convert_str(key),
                                                              dbutil.convert_str(qdict[key]))
    # Add form fields in a table.

    print '<table border=1 style="border-collapse:collapse">'
    print '<tr>'
    print '<td>'
    print '<label for="id">ID:</label>'
    print '</td>'
    print '<td>'
    print '<input type="number" id="id" name="id" value="%d" readonly>' % id
    print '</td>'
    print '</tr>'
    print '<tr>'
    print '<td>'
    print '<label for="stage_id">Stage ID:</label>'
    print '</td>'
    print '<td>'
    print '<input type="number" id="stage_id" name="stage_id" value="%d" readonly>' % stage_id
    print '</td>'
    print '</tr>'
    print '<tr>'
    print '<td>'
    print '<label for="name">Name:</label>'
    print '</td>'
    print '<td>'
    print '<input type="text" id="name" name="name" value="%s">' % name
    print '</td>'
    print '</tr>'
    print '<tr>'
    print '<td>'
    print '<label for="value">Value:</label>'
    print '</td>'
    print '<td>'
    print '<input type="text" id="value" name="value" value="%s">' % value
    print '</td>'
    print '</tr>'

    # Finish table.

    print '</table>'

    # Add "Save" and "Back" buttons.

    print '<input type="submit" name="submit" value="Save" %s>' % disabled
    print '<input type="submit" name="submit" value="Update" %s>' % disabled
    print '<input type="submit" name="submit" value="Back">'
    print '</form>'


# Main procedure.

def main(id, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = True, devel = qdict['dev'])

    # Generate html document header.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<title>Override Editor</title>'
    print '</head>'
    print '<body>'
    print '<a href=%s/query_projects.py?%s>Project list</a><br>' % \
        (dbconfig.base_url, dbargs.convert_args(qdict))

    # Generate main parg of html document.

    override_form(cnx, id, qdict)

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
