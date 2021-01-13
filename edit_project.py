#! /usr/bin/python
#==============================================================================
#
# Name: edit_project.py
#
# Purpose: CGI project editor.
#
# CGI arguments:
#
# id      - Project id.
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


# Project edit form.

def project_form(cnx, id, qdict):

    # Construct global disabled option for restricted controls.

    disabled = ''
    if not dbconfig.restricted_access_allowed() and dbutil.restricted_access(cnx, 'projects', id):
        disabled = 'disabled'

    # Construct disable option that applies only to status options.

    option_disabled = ''
    if not dbconfig.restricted_access_allowed():
        option_disabled = 'disabled'

    # Get project name.

    name = dbutil.get_project_name(cnx, id)

    # Get experiment.

    experiment = dbutil.get_project_experiment(cnx, id)

    # Generate form.

    print '<h2>Project %s</h2>' % name

    # Add button to insert another stage.

    print '<h2>Stages</h2>'
    print '<form action="%s/add_stage.py?id=%d&%s" method="post" target="_self">' % \
        (dbconfig.rel_url, id, dbargs.convert_args(qdict))
    print '<input type="submit" value="Add Stage" %s>' % disabled
    print '</form>'
    print '<br>'

    # Query stage ids belonging to this project.

    c = cnx.cursor()
    q = 'SELECT id, name FROM stages WHERE project_id=%d ORDER BY seqnum' % id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) > 0:

        # Add links to edit project stages.

        print '<table border=1 style="border-collapse:collapse">'
        print '<tr>'
        print '<th>&nbsp;Stage ID&nbsp;</th>'
        print '<th>&nbsp;Stage Name&nbsp;</th>'
        print '</tr>'

        for row in rows:
            print '<tr>'
            stage_id = row[0]
            stage_name = row[1]
            print '<td align="center">%d</td>' % stage_id
            print '<td>&nbsp;<a target="_self" href="%s/edit_stage.py?id=%d&%s">%s</a>&nbsp;</td>' % \
                (dbconfig.base_url, stage_id, dbargs.convert_args(qdict), stage_name)

            # Add Edit button/column

            print '<td>'
            print '<form target="_self" action="%s/edit_stage.py?id=%d&%s" method="post">' % \
                (dbconfig.rel_url, stage_id, dbargs.convert_args(qdict))
            print '<div title="Edit stage">'
            print '<input type="submit" value="&#x270e;">'
            print '</div>'
            print '</form>'
            print '</td>'        

            # Add Clone button/column

            print '<td>'
            print '<form target="_self" action="%s/clone_stage.py?id=%d&%s" method="post">' % \
                (dbconfig.rel_url, stage_id, dbargs.convert_args(qdict))
            print '<div title="Clone stage">'
            print '<input type="submit" value="&#x2398;" %s>' % disabled
            print '</div>'
            print '</form>'
            print '</td>'        

            # Add Delete button/column

            print '<td>'
            print '<form action="%s/delete_stage.py?id=%d&%s" method="post">' % \
                (dbconfig.rel_url, stage_id, dbargs.convert_args(qdict))
            print '<div title="Delete stage">'
            print '<input type="submit" value="&#x1f5d1;" %s>' % disabled
            print '</div>'
            print '</form>'
            print '</td>'        

            # Add Up button/column

            print '<td>'
            print '<form action="%s/up_stage.py?id=%d&%s" method="post">' % \
                (dbconfig.rel_url, stage_id, dbargs.convert_args(qdict))
            print '<div title="Move up">'
            print '<input type="submit" value="&#x25b2;" %s>' % disabled
            print '</div>'
            print '</form>'
            print '</td>'        

            # Add Down button/column

            print '<td>'
            print '<form action="%s/down_stage.py?id=%d&%s" method="post">' % \
                (dbconfig.rel_url, stage_id, dbargs.convert_args(qdict))
            print '<div title="Move down">'
            print '<input type="submit" value="&#x25bc;" %s>' % disabled
            print '</div>'
            print '</form>'
            print '</td>'        

            # Finish row.

            print '</tr>'

        # Finish table.

        print '</table>'

    print '<h2>Project Data</h2>'

    # Query full project from database.

    q = 'SELECT %s FROM projects WHERE id=%d' % (dbutil.columns('projects'), id)
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch project id %d' % id)
    row = rows[0]

    print '<form action="%s/dbhandler.py" method="post">' % dbconfig.rel_url

    # Add hidden input field to store table name.

    print '<input type="hidden" id="table" name="table" value="projects">'

    # Add hidden input field to store save url (parent of this page).

    print '<input type="hidden" id="saveurl" name="saveurl" value="%s/query_projects.py?%s">' % \
        (dbconfig.base_url, dbargs.convert_args(qdict))

    # Add hidden qdict input fields.

    for key in qdict:
        print '<input type="hidden" name="%s" value="%s">' % (dbutil.convert_str(key),
                                                              dbutil.convert_str(qdict[key]))
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
                        pulldown_list = pulldowns[colname]
                        if type(pulldown_list) == type({}):
                            if experiment in pulldown_list:
                                pulldown_list = pulldowns[colname][experiment]
                            else:
                                pulldown_list = ['']
                        for value in pulldown_list:
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
    print '<title>Project Editor</title>'
    print '</head>'
    print '<body>'
    print '<a href=%s/query_projects.py?%s>Project list</a><br>' % \
        (dbconfig.base_url, dbargs.convert_args(qdict))

    # Generate main parg of html document.

    project_form(cnx, id, qdict)

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
