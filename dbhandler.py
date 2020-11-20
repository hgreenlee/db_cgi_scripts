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

    cnx = dbconfig.connect(readonly = False)

    # Get table name and id (primary key).
    # Both of these values should exist and be non-null, or else operation will fail.

    table = ''
    id = 0
    if argdict.has_key('table'):
        table = argdict['table']
    if argdict.has_key('id'):
        id = int(argdict['id'])

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
    cnx.commit()

    # Calculate redirect url.

    url = 'https://microboone-exp.fnal.gov/cgi-bin/db/query_projects.py'
    if os.environ.has_key('HTTP_REFERER'):
        url = os.environ['HTTP_REFERER']

    # Generate html redirect document.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<meta http-equiv="refresh" content="0; url=%s" />' % url
    print '</head>'
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
