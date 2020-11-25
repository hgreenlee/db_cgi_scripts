#! /usr/bin/python
#==============================================================================
#
# Name: edit_datasets.py
#
# Purpose: CGI script to edit datasets associated with a project.
#
# CGI arguments:
#
# id      - Project id.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 16-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import StringIO, pycurl
import dbconfig, dbutil, dbargs
from dbdict import databaseDict
import cgi
import cgitb
cgitb.enable()


# Datasets form

def datasets_form(cnx, project_id, qdict):

    # Get project name.

    name = dbutil.get_project_name(cnx, project_id)

    # Construct global disabled option for restricted controls.

    disabled = ''
    if not dbconfig.restricted_access_allowed() and dbutil.restricted_access(cnx, 'projects', project_id):
        disabled = 'disabled'

    # Generate form.

    print '<h2>Datasets for Project %s</h2>' % name

    c = cnx.cursor()

    for dataset_type in ('input', 'output'):
        title_type = dataset_type[0].upper() + dataset_type[1:]
    
        # Section title.

        print '<h3>%s Datasets</h3>' % title_type

        # Add button to add dataset.

        print '<form action="/cgi-bin/db/add_dataset.py?id=%d&type=%s&%s" method="post">' % \
            (project_id, dataset_type, dbargs.convert_args(qdict))
        print '<label for="submit">Add %s Dataset: </label>' % title_type
        print '<input type="submit" id="submit" value="Add" %s>' % disabled
        print '</form>'
        print '<p>'

        # Query datasets belonging to this project and type.

        q = 'SELECT id, name, files, events FROM datasets WHERE project_id=%d AND type=\'%s\' ORDER BY seqnum' % \
            (project_id, dataset_type)
        c.execute(q)
        rows = c.fetchall()

        # Make dataset table.

        print '<table border=1 style="border-collapse:collapse">'
        print '<tr>'
        print '<th>&nbsp;Dataset ID&nbsp;</th>'
        print '<th>&nbsp;Dataset Name&nbsp;</th>'
        print '<th>&nbsp;Files&nbsp;</th>'
        print '<th>&nbsp;Events&nbsp;</th>'    
        print '</tr>'

        for row in rows:
            print '<tr>'
            dataset_id = row[0]
            dataset_name = row[1]
            nfile = row[2]
            nev = row[3]
            print '<td align="center">%d</td>' % dataset_id
            print '<td>&nbsp;<a href=%s/definitions/name/%s>%s</a>&nbsp;</td>' % \
                (dbconfig.samweb_url, dataset_name, dataset_name)
            print '<td align="right">&nbsp;%d&nbsp;</td>' % nfile
            print '<td align="right">&nbsp;%d&nbsp;</td>' % nev

            # Add Update button/column

            print '<td>'
            print '<form action="/cgi-bin/db/edit_datasets.py?id=%d&update=%d&%s" method="post">' % \
                (project_id, dataset_id, dbargs.convert_args(qdict))
            print '<input type="submit" value="Update" %s>' % disabled
            print '</form>'
            print '</td>'        

            # Add Edit button/column

            print '<td>'
            print '<form action="/cgi-bin/db/edit_dataset.py?id=%d&%s" method="post">' % \
                (dataset_id, dbargs.convert_args(qdict))
            print '<input type="submit" value="Edit" %s>' % disabled
            print '</form>'
            print '</td>'        

            # Add Clone button/column

            print '<td>'
            print '<form action="/cgi-bin/db/clone_dataset.py?id=%d&%s" method="post">' % \
                (dataset_id, dbargs.convert_args(qdict))
            print '<input type="submit" value="Clone" %s>' % disabled
            print '</form>'
            print '</td>'        

            # Add Delete button/column

            print '<td>'
            print '<form action="/cgi-bin/db/delete_dataset.py?id=%d&%s" method="post">' % \
                (dataset_id, dbargs.convert_args(qdict))
            print '<input type="submit" value="Delete" %s>' % disabled
            print '</form>'
            print '</td>'        

            # Add Up button/column

            print '<td>'
            print '<form action="/cgi-bin/db/up_dataset.py?id=%d&%s" method="post">' % \
                (dataset_id, dbargs.convert_args(qdict))
            print '<input type="submit" value="Up" %s>' % disabled
            print '</form>'
            print '</td>'        

            # Add Down button/column

            print '<td>'
            print '<form action="/cgi-bin/db/down_dataset.py?id=%d&%s" method="post">' % \
                (dataset_id, dbargs.convert_args(qdict))
            print '<input type="submit" value="Down" %s>' % disabled
            print '</form>'
            print '</td>'        

            # Finish row.

            print '</tr>'

        # Finish table.

        print '</table>'



# Main procedure.

def main(project_id, update_id, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # See if we want to update any dataset.

    if update_id != 0:

        update_ok = False

        # Query dataset name.

        c = cnx.cursor()
        q = 'SELECT name FROM datasets WHERE id=%d' % update_id
        c.execute(q)
        rows = c.fetchall()
        if len(rows) == 0:
            raise IOError('Unable to fetch dataset id %d' % update_id)
        dataset_name = rows[0][0]

        # Query event count form sam.

        url = '%s/definitions/name/%s/files/summary' % (dbconfig.samweb_url, dataset_name)
        buffer = StringIO.StringIO()
        pyc = pycurl.Curl()
        pyc.setopt(pyc.URL, dbutil.convert_str(url))
        pyc.setopt(pyc.WRITEFUNCTION, buffer.write)
        pyc.setopt(pyc.FOLLOWLOCATION, True)
        pyc.setopt(pyc.TIMEOUT, 3600)
        pyc.perform()
        code = pyc.getinfo(pyc.RESPONSE_CODE)
        pyc.close()
        if code == 200:

            # Parse result.

            events = 0
            files = 0
            result = buffer.getvalue()
            for line in result.splitlines():
                words = line.split(':')
                if len(words) >= 2:
                    word0 = words[0].strip()
                    value = int(words[1].strip())
                    if word0 == 'File Count':
                        files = value
                    elif word0 == 'Total Event Count':
                        events = value
            if events > 0 and files > 0:
                update_ok = True

        if update_ok:

            # Check access.

            if not dbconfig.restricted_access_allowed() and dbutil.restricted_access(cnx, 'datasets', dataset_id):
                dbutil.restricted_error()

            # Update database.
                    
            q = 'UPDATE datasets SET events=%d, files=%d WHERE id=%d' % (events, files, update_id)
            c.execute(q)
            cnx.commit()

        else:

            url = 'https://microboone-exp.fnal.gov/cgi-bin/db/edit_datasets.py?id=%d&%s' % \
                  (project_id, dbargs.convert_args(qdict))
            print 'Content-type: text/html'
            print
            print '<!DOCTYPE html>'
            print '<html>'
            print '<head>'
            print '<title>Update Datasets</title>'
            print '</head>'
            print '<body>'
            print 'Failed to update dataset statistics.'
            print '<br><br>'
            print '<a href=%s>Return to dataset list</a>.' % url
            print '</body>'
            print '</html>'
            return

    # Generate html document header.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<title>Project Datasets Editor</title>'
    print '</head>'
    print '<body>'
    print '<a href=https://microboone-exp.fnal.gov/cgi-bin/db/query_projects.py?%s>Project list</a><br>' % \
        dbargs.convert_args(qdict)

    # Generate main parg of html document.

    datasets_form(cnx, project_id, qdict)

    # Generate html document trailer.
    
    print '</body>'
    print '</html>'


# End of definitions.  Executable code starts here.

if __name__ == "__main__":

    # Parse arguments.

    argdict = dbargs.get()
    qdict = dbargs.extract_qdict(argdict)
    project_id = 0
    update_id = 0
    if 'id' in argdict:
        project_id = int(argdict['id'])
    if 'update' in argdict:
        update_id = int(argdict['update'])

    # Call main procedure.

    main(project_id, update_id, qdict)
