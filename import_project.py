#! /usr/bin/python
#==============================================================================
#
# Name: import_project.py
#
# Purpose: CGI script to import a project from an xml file on the local computer.
#
# CGI arguments:
#
# file             - Local xml file name.
# results_per_page - Number of projects to display on each page.
# page             - Current page (starts at 1).
# pattern          - Search pattern.
#
# Created: 15-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(xmldata, results_per_page, current_page, pattern):

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

        print '<form action="/cgi-bin/import_project.py" method="post" enctype="multipart/form-data">'
        print '<input type="hidden" name="results_per_page" value="%d">' % results_per_page
        print '<input type="hidden" name="page" value="%d">' % current_page
        print '<input type="hidden" name="pattern" value="%s">' % pattern
        print '<label for="filename">Choose input xml file</label>'
        print '<input type="file" id="filename" name="file" accept=".xml">'
        print '<br>'
        print '<input type="submit" value="Import">'
        print '<input type="submit" value="Cancel" formaction="/cgi-bin/query_projects.py">'
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

            url = 'https://microboone-exp.fnal.gov/cgi-bin/query_projects.py?results_per_page=%d&page=%d&pattern=%s' % \
                  (results_per_page, current_page, pattern)
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

            url = 'https://microboone-exp.fnal.gov/cgi-bin/query_projects.py?results_per_page=%d&page=%d&pattern=%s' % \
                  (results_per_page, current_page, pattern)
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
            url = 'https://microboone-exp.fnal.gov/cgi-bin/edit_project.py?id=%d&results_per_page=%d&page=%d&pattern=%s' % \
                  (project_id, results_per_page, current_page, pattern)
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

            url = 'https://microboone-exp.fnal.gov/cgi-bin/query_projects.py?results_per_page=%d&page=%d&pattern=%s' % \
                  (results_per_page, current_page, pattern)
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

    xmldata = ''
    results_per_page = 20
    current_page = 1
    pattern = ''
    args = dbargs.get()
    if 'file' in args:
        xmldata = args['file']
    if 'results_per_page' in args:
        results_per_page = int(args['results_per_page'])
    if 'page' in args:
        current_page = int(args['page'])
    if 'pattern' in args:
        pattern = args['pattern']

    # Call main procedure.

    main(xmldata, results_per_page, current_page, pattern)
