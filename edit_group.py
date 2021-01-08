#! /usr/bin/python
#==============================================================================
#
# Name: edit_group.py
#
# Purpose: CGI project group editor.
#
# CGI arguments:
#
# id      - Group id.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 19-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict
from dbconfig import pulldowns
import cgi
import cgitb
cgitb.enable()


# Group edit form.

def group_form(cnx, id, qdict):

    # Construct global disabled option for restricted controls.

    disabled = ''
    if not dbconfig.restricted_access_allowed():
        disabled = 'disabled'

    # Get group name.

    name = dbutil.get_group_name(cnx, id)

    # Generate form.

    print '<h2>Group %s</h2>' % name

    # Query full group from database.

    c = cnx.cursor()
    q = 'SELECT %s FROM groups WHERE id=%d' % (dbutil.columns('groups'), id)
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch group id %d' % id)
    row = rows[0]

    print '<form action="/cgi-bin/db/dbhandler.py" method="post">'

    # Add hidden input field to store table name.

    print '<input type="hidden" id="table" name="table" value="groups">'

    # Add hidden qdict input fields.

    for key in qdict:
        print '<input type="hidden" name="%s" value="%s">' % (dbutil.convert_str(key),
                                                              dbutil.convert_str(qdict[key]))
    # Loop over fields of this group.
    # Put fields in a table.

    print '<table border=1 style="border-collapse:collapse">'
    cols = databaseDict['groups']
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
                    print '<input type="text" id="%s" name="%s" size=10 value="%8.6f" %s>' % \
                        (colname, colname, row[n], readonly)
                elif coltype[0:7] == 'VARCHAR':
                    if colname in pulldowns:
                        print '<select id="%s" name="%s" size=0 %s>' % (colname, colname, disabled)
                        for value in pulldowns[colname]:
                            sel = ''
                            if value == row[n]:
                                sel = 'selected'
                            if value == '' or value == 'Requested':
                                print '<option value="%s" %s>%s</option>' % (value, sel, value)
                            else:
                                print '<option value="%s" %s %s>%s</option>' % (value, sel, option_disabled, value)
                        print '</select>'
                    else:
                        print '<input type="text" id="%s" name="%s" size=100 value="%s" %s>' % \
                            (colname, colname, row[n], readonly)

            else:

                # Array columns.
                # Display using multiline <textarea>.

                strs = dbutil.get_strings(cnx, row[n])
                print '<textarea id="%s" name="%s" rows=%d cols=80 %s>' % \
                    (colname, colname, max(len(strs),1), readonly)
                print '\n'.join(strs)
                print '</textarea>'

            print '</td>'
            print '</tr>'

    # Finish table.

    print '</table>'

    # Projects section.

    print '<h3>Projects</h3>'

    # Query all projects.

    project_ids = []
    q = 'SELECT id,name FROM projects ORDER BY name'
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        project_id = row[0]
        project_ids.append(project_id)

    # Query all projects in this group.

    project_group_ids = set()
    q = 'SELECT project_id FROM group_project WHERE group_id=%d' % id
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        project_id = row[0]
        project_group_ids.add(project_id)

    # Projects table.

    print '<table border=1 style="border-collapse:collapse">'
    print '<tr>'
    print '<th>Group Projects</th>'
    print '<th>Available Projects</th>'
    print '</tr>'

    # Generate project lists.

    print '<td>'

    # Generate selection list for projects in group.
    # Loop over project ids in name order.

    print '<select id="ingroup" name="remove" size=20 multiple>'
    for project_id in project_ids:
        if project_id in project_group_ids:
            project_name = dbutil.get_project_name(cnx, project_id)
            print '<option value="%d">%s</option>' % (project_id, project_name)
    print '</select>'
    print '</td>'
    print '<td>'

    # Generate selection list for projects not in group.
    # Loop over project ids in name order.

    print '<select id="available" name="add" size=20 multiple>'
    for project_id in project_ids:
        if not project_id in project_group_ids:
            project_name = dbutil.get_project_name(cnx, project_id)
            print '<option value="%d">%s</option>' % (project_id, project_name)
    print '</select>'
    print '</td>'

    # Finish datasets table.

    print '</table>'

    # Add "Save" and "Back" buttons.

    print '<input type="submit" value="Save" %s>' % disabled
    print '<input type="submit" value="Back" formaction="/cgi-bin/db/query_groups.py?%s">' % \
        dbargs.convert_args(qdict)
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
    print '<title>Group Editor</title>'
    print '</head>'
    print '<body>'
    print '<a href=%s/query_groups.py?%s>Group list</a><br>' % \
        (dbconfig.base_url, dbargs.convert_args(qdict))

    # Generate main parg of html document.

    group_form(cnx, id, qdict)

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
