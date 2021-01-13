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
import pycurl
import dbconfig, dbutil, dbargs
from dbdict import databaseDict
import cgi
import cgitb
cgitb.enable()


# Datasets form

def datasets_form(cnx, project_id, qdict):

    # Query project name and experiment.

    c = cnx.cursor()
    q = 'SELECT name, experiment FROM projects WHERE id=%d' % project_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch project id %d' % project_id)
    row = rows[0]
    name = row[0]
    experiment = row[1]

    # Construct global disabled option for restricted controls.

    disabled = ''
    if not dbconfig.restricted_access_allowed() and dbutil.restricted_access(cnx, 'projects', project_id):
        disabled = 'disabled'

    # Generate form.

    print '<h2>Datasets for Project %s</h2>' % name

    for dataset_type in ('input', 'output'):
        title_type = dataset_type[0].upper() + dataset_type[1:]
    
        # Section title.

        print '<h3>%s Datasets</h3>' % title_type

        # Add button to add dataset.

        print '<form action="%s/add_dataset.py?id=%d&type=%s&%s" method="post">' % \
            (dbconfig.rel_url, project_id, dataset_type, dbargs.convert_args(qdict))
        print '<label for="submit">Add %s Dataset: </label>' % title_type
        print '<input type="submit" id="submit" value="Add" %s>' % disabled
        print '</form>'
        print '<p>'

        # Query datasets belonging to this project and type.

        q = 'SELECT id, name, files, events, parent_files, parent_events, parent_id FROM datasets WHERE project_id=%d AND type=\'%s\' ORDER BY seqnum' % \
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
        if dataset_type == 'output':
            print '<th>&nbsp;Parent Files&nbsp;</th>'
            print '<th>&nbsp;Parent Events&nbsp;</th>'    
            print '<th>&nbsp;Complete (%)&nbsp;</th>'    
        print '</tr>'

        for row in rows:
            print '<tr>'
            dataset_id = row[0]
            dataset_name = row[1]
            nfile = row[2]
            nev = row[3]
            pfile = row[4]
            pev = row[5]
            parent_id = row[6]

            # If the parent_id is nonzero, query statistics of parent dataset.

            pfile2 = 0
            pev2 = 0
            if parent_id != 0:
                q2 = 'SELECT files, events FROM datasets WHERE id=%d' % parent_id
                c.execute(q2)
                rows2 = c.fetchall()
                if len(rows2) > 0:
                    row2 = rows2[0]
                    pfile2 = row2[0]
                    pev2 = row2[1]

            # Calculate complete fraction.

            frac = 0.
            if pev2 > 0:
                frac = float(pev) / float(pev2)
                
            print '<td align="center">%d</td>' % dataset_id
            print '<td>&nbsp;<a href=%s/definitions/name/%s>%s</a>&nbsp;</td>' % \
                (dbconfig.samweb_url[experiment], dataset_name, dataset_name)
            print '<td align="right">&nbsp;%d&nbsp;</td>' % nfile
            print '<td align="right">&nbsp;%d&nbsp;</td>' % nev
            if dataset_type == 'output':
                print '<td align="right">&nbsp;%d&nbsp;</td>' % pfile
                print '<td align="right">&nbsp;%d&nbsp;</td>' % pev
                print '<td align="right">&nbsp;%6.2f&nbsp;</td>' % (100.*frac)

            # Add Update button/column

            print '<td>'
            print '<form action="%s/edit_datasets.py?id=%d&update=%d&%s" method="post">' % \
                (dbconfig.rel_url, project_id, dataset_id, dbargs.convert_args(qdict))
            print '<div title="Update statistics">'
            print '<input type="submit" value="+Stats" %s>' % disabled
            print '</div>'
            print '</form>'
            print '</td>'        

            # Add Edit button/column

            print '<td>'
            print '<form target="_self" action="%s/edit_dataset.py?id=%d&%s" method="post">' % \
                (dbconfig.rel_url, dataset_id, dbargs.convert_args(qdict))
            print '<div title="Edit dataset">'
            print '<input type="submit" value="&#x270e;" %s>' % disabled
            print '</div>'
            print '</form>'
            print '</td>'        

            # Add Clone button/column

            print '<td>'
            print '<form action="%s/clone_dataset.py?id=%d&%s" method="post">' % \
                (dbconfig.rel_url, dataset_id, dbargs.convert_args(qdict))
            print '<div title="Clone dataset">'
            print '<input type="submit" value="&#x2398;" %s>' % disabled
            print '</div>'
            print '</form>'
            print '</td>'        

            # Add Delete button/column

            print '<td>'
            print '<form action="%s/delete_dataset.py?id=%d&%s" method="post">' % \
                (dbconfig.rel_url, dataset_id, dbargs.convert_args(qdict))
            print '<div title="Delete dataset">'
            print '<input type="submit" value="&#x1f5d1;" %s>' % disabled
            print '</div>'
            print '</form>'
            print '</td>'        

            # Add Up button/column

            print '<td>'
            print '<form action="%s/up_dataset.py?id=%d&%s" method="post">' % \
                (dbconfig.rel_url, dataset_id, dbargs.convert_args(qdict))
            print '<div title="Move up">'
            print '<input type="submit" value="&#x25b2;" %s>' % disabled
            print '</div>'
            print '</form>'
            print '</td>'        

            # Add Down button/column

            print '<td>'
            print '<form action="%s/down_dataset.py?id=%d&%s" method="post">' % \
                (dbconfig.rel_url, dataset_id, dbargs.convert_args(qdict))
            print '<div title="Move down">'
            print '<input type="submit" value="&#x25bc;" %s>' % disabled
            print '</div>'
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

        # Query experiment name.

        q = 'SELECT experiment FROM projects WHERE id=%d' % project_id
        c.execute(q)
        rows = c.fetchall()
        if len(rows) == 0:
            raise IOError('Unable to fetch project id %d' % project_id)
        row = rows[0]
        experiment = row[0]

        # Query event count form sam.

        files = 0
        events = 0
        parent_files = 0
        parent_events = 0
        update_ok = True
        r = dbutil.get_stats(dbconfig.samweb_url[experiment], dataset_name)
        if r == None:
            update_ok = False
        else:
            files = r[0]
            events = r[1]
            r = dbutil.get_parent_stats(dbconfig.samweb_url[experiment], dataset_name)
            if r == None:
                update_ok = False
            else:
                parent_files = r[0]
                parent_events = r[1]

        # Do update.

        if update_ok:

            # Check access.

            if not dbconfig.restricted_access_allowed() and dbutil.restricted_access(cnx, 'datasets', dataset_id):
                dbutil.restricted_error()

            # Update database.
                    
            q = 'UPDATE datasets SET events=%d, files=%d, parent_events=%d, parent_files=%d WHERE id=%d' % (events, files, parent_events, parent_files, update_id)
            c.execute(q)
            cnx.commit()

        else:

            url = '%s/edit_datasets.py?id=%d&%s' % \
                  (dbconfig.base_url, project_id, dbargs.convert_args(qdict))
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
    print '<a href=%s/query_projects.py?%s>Project list</a><br>' % \
        (dbconfig.base_url, dbargs.convert_args(qdict))

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
