#! /usr/bin/python
#==============================================================================
#
# Name: import_project.py
#
# Purpose: CGI script to import a project from an xml file on the local computer.
#
# CGI arguments:
#
# file    - Local xml file data.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 15-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(xmldata, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False)

    if xmldata == '':

        # If xml data is empty, generate a dialog to browse for local xml name.

        print 'Content-type: text/html'
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<head>'
        print '<title>Import Project</title>'
        print '</head>'
        print '<body>'
        
        # Generate a form with file dialog and two buttons "Import" and "Cancel."

        print '<form action="/cgi-bin/db/import_project.py" method="post" enctype="multipart/form-data">'
        for key in qdict:
            print '<input type="hidden" name="%s" value="%s">' % (dbutil.convert_str(key),
                                                                  dbutil.convert_str(qdict[key]))
        print '<label for="xmldata">Choose input xml file: </label>'
        print '<input type="file" id="xmldata" name="data" accept=".xml">'
        print '<br>'
        print '<input type="submit" value="Import">'
        print '<input type="submit" value="Cancel" formaction="/cgi-bin/db/query_projects.py">'
        print '</body>'
        print '</html>'

    else:

        # Got uploaded xml data.
        # Check any project are not already in database.

        names = []
        try:
            names = dbutil.xml_project_names(xmldata)
        except:
            names = []
        if len(names) == 0:

            # XML error.

            url = 'https://microboone-exp.fnal.gov/cgi-bin/db/query_projects.py?%s' % \
                  dbargs.convert_args(qdict)
            print 'Content-type: text/html'
            print
            print '<!DOCTYPE html>'
            print '<html>'
            print '<head>'
            print '<title>Import Project</title>'
            print '</head>'
            print '<body>'
            print 'Initial XML parsing error.'
            print '<br><br>'
            print '<a href=%s>Return to project list</a>.' % url
            print '</body>'
            print '</html>'
            return

        # See if names already exist in database.

        ok = False
        for name in names:
            id = dbutil.get_project_id(cnx, name)
            if id == 0:
                ok = True
                break

        if not ok:

            # All project names are already in database.
            # Generate informative page.

            url = 'https://microboone-exp.fnal.gov/cgi-bin/db/query_projects.py?%s' % \
                  dbargs.convert_args(qdict)
            print 'Content-type: text/html'
            print
            print '<!DOCTYPE html>'
            print '<html>'
            print '<head>'
            print '<title>Import Project</title>'
            print '</head>'
            print '<body>'
            print 'Project with same name is already in database.'
            print '<br><br>'
            print '<a href=%s>Return to project list</a>.' % url
            print '</body>'
            print '</html>'
            return

        # Insert project in database.

        ids = []
        try:
            ids = dbutil.import_project(cnx, xmldata)
        except:
            #print 'Content-type: text/html'
            #print
            #ids = dbutil.import_project(cnx, xmldata)
            ids = []

        if len(ids) > 0:

            # Import successful.
            # Redirect to project editor.

            project_id = ids[0]
            url = 'https://microboone-exp.fnal.gov/cgi-bin/db/edit_project.py?id=%d&%s' % \
                  (project_id, dbargs.convert_args(qdict))
            print 'Content-type: text/html'
            print
            print '<!DOCTYPE html>'
            print '<html>'
            print '<head>'
            print '<meta http-equiv="refresh" content="0; url=%s" />' % url
            print '</head>'
            print '<body>'
            print 'Import project successful.'
            print '<br><br>'
            print 'If page does not automatically reload click this <a href=%s>link</a>' % url
            print '</body>'
            print '</html>'

        else:

            # Import failed.

            url = 'https://microboone-exp.fnal.gov/cgi-bin/db/query_projects.py?%s' % \
                  dbargs.convert_args(qdict)
            print 'Content-type: text/html'
            print
            print '<!DOCTYPE html>'
            print '<html>'
            print '<head>'
            print '<title>Import Project</title>'
            print '</head>'
            print '<body>'
            print 'XML parsing error.'
            print '<br><br>'
            print '<a href=%s>Return to project list</a>.' % url
            print '</body>'
            print '</html>'

    # Done.

    return

# End of definitions.  Executable code starts here.

if __name__ == "__main__":

    # Parse arguments.

    argdict = dbargs.get()
    qdict = dbargs.extract_qdict(argdict)
    xmldata = ''
    if 'data' in argdict:
        xmldata = argdict['data']

    # Call main procedure.

    main(xmldata, qdict)
