#! /usr/bin/python
#==============================================================================
#
# Name: clone_project.py
#
# Purpose: CGI project clone.
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


# Main procedure.

def main(project_id, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # Get original project name.

    project_name = dbutil.get_project_name(cnx, project_id)
    clone_id = 0

    if project_name != '':

        # Generate first candidate clone project name.

        clone_project_name = 'Clone of %s' % project_name

        # Check whether this project name is already used.

        dup_id = dbutil.get_project_id(cnx, clone_project_name)

        # Modify project name until we find one that isn't alrady used.

        ntry = 1
        while dup_id > 0:
            ntry += 1
            clone_project_name = 'Clone %d of %s' % (ntry, project_name)
            dup_id = dbutil.get_project_id(cnx, clone_project_name)

        # Now clone the project.

        clone_id = dbutil.clone_project(cnx, project_id, clone_project_name)

    # Generate redirect html document header to invoke the project editor for
    # the newly created document.

    url = ''
    if clone_id > 0:
        url = '%s/edit_project.py?id=%d&%s' % \
              (dbconfig.base_url, clone_id, dbargs.convert_args(qdict))
    else:
        url = '%s/query_projects.py?%s' % \
              (dbconfig.base_url, dbargs.convert_args(qdict))

    print 'Content-type: text/html'
    print 'Status: 303 See Other'
    print 'Location: %s' % url
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<body>'
    url = ''
    if clone_id > 0:
        print 'Cloned project %s' % project_name
    else:
        print 'Project not cloned.'
    print '<br><br>'
    print 'If page does not automatically reload click this <a href=%s>link</a>' % url
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
