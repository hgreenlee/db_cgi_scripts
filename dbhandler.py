#! /usr/bin/python
#==============================================================================
#
# Name: dbhandler.py
#
# Purpose: CGI script to process form data from database edit forms.
#
# CGI arguments:
#
# table    - Table to update.
# id       - Row id.
# <column> - Value.  Matched against column names stired in dictionary.
#
# Created: 20-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(argdict):

    # Open database connection.

    qdict = dbargs.extract_qdict(argdict)
    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # Get table name and id (primary key).
    # Both of these values should exist and be non-null, or else operation will fail.

    table = ''
    id = 0
    saveurl = ''
    update_db = False
    if 'table' in argdict:
        table = argdict['table']
    if 'id' in argdict:
        id = int(argdict['id'])
    if 'saveurl' in argdict and 'submit' in argdict and \
       (argdict['submit'] == 'Save' or argdict['submit'] == 'Back'):
        saveurl = argdict['saveurl']
    if 'submit' in argdict and (argdict['submit'] == 'Save' or argdict['submit'] == 'Update'):
        update_db = True
    

    # Check access restrictions.

    if not dbconfig.restricted_access_allowed():

        # Check whether this table/id is restricted access.

        if dbutil.restricted_access(cnx, table, id):
            dbutil.restricted_error()

        # If the projects table is being updated to a status which is anything other
        # than '' or 'Requested', it is an error.

        if table == 'projects' and 'status' in argdict and \
           argdict['status'] != '' and argdict['status'] != 'Requested':
            dbutil.restricted_error()

    if update_db:

        # Update database.

        c = cnx.cursor()
        q = 'UPDATE %s SET ' % table

        # Loop over columns of this table.

        cols = databaseDict[table]
        first = True
        for n in range(len(cols)):
            coltup = cols[n]
            colname = coltup[0]
            coltype = coltup[2]
            colarray = coltup[3]
            coldesc = coltup[4]

            if colname != '' and colname != 'id':

                # Did form supply a value for this column?

                if colname in argdict:

                    # Maybe add separator.

                    if first:
                        first = False
                    else:
                        q += ', '

                    # Add value.

                    if colarray == 0:

                        # Scalar column.

                        if coltype[0:3] == 'INT':
                            q += '%s=%d' % (colname, int(argdict[colname]))
                        elif coltype[0:6] == 'DOUBLE':
                            q += '%s=%8.6f' % (colname, float(argdict[colname]))
                        elif coltype[0:7] == 'VARCHAR':
                            q += '%s=\'%s\'' % (colname, argdict[colname].replace("'", "\\'"))

                    else:

                        # String array.

                        strs = argdict[colname].split()
                        strid = dbutil.update_strings(cnx, strs)
                        q += '%s=%d' % (colname, strid)

        # Add where clause.

        q += ' WHERE id=%d' % id

        # Run query.

        c.execute(q)

        # Special handling for table groups.

        if table == 'groups':

            # Loop over arguments to find projects to add to this group.

            project_ids = []
            for k in argdict:
                if k.startswith('add'):
                    project_ids.append(int(argdict[k]))

            # Loop over projects.

            for project_id in project_ids:
                q = 'INSERT INTO group_project SET group_id=%d,project_id=%d' % (id, project_id)
                c.execute(q)

            # Loop over arguments to find projects to remove from this group.

            project_ids = []
            for k in argdict:
                if k.startswith('remove'):
                    project_ids.append(int(argdict[k]))

            # Loop over projects.

            for project_id in project_ids:
                q = 'DELETE FROM group_project WHERE group_id=%d AND project_id=%d' % (id, project_id)
                c.execute(q)

        # Commit updates.

        cnx.commit()

    # Calculate redirect url.

    url = '%s/query_projects.py' % dbconfig.base_url
    if saveurl != '':
        url = saveurl
    elif 'HTTP_REFERER' in os.environ:
        url = os.environ['HTTP_REFERER']

    # Generate html redirect document.

    print 'Content-type: text/html'
    print 'Status: 303 See Other'
    print 'Location: %s' % url
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<body>'
    if table != '':
        print 'Database table "%s" updated.' % table
    else:
        print 'Database not updated.'
    print '<br><br>'
    print 'If page does not automatically reload click this <a href=%s>link</a>' % url
    print '</body>'
    print '</html>'


# End of definitions.  Executable code starts here.

if __name__ == "__main__":

    # Parse arguments.

    argdict = dbargs.get()

    # Call main procedure.

    main(argdict)
