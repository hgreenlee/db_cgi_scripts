#! /usr/bin/python
#==============================================================================
#
# Name: clone_group.py
#
# Purpose: CGI project gropu clone.
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


# Main procedure.

def main(group_id, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # Get original group name.

    group_name = dbutil.get_group_name(cnx, group_id)
    clone_id = 0

    if group_name != '':

        # Generate first candidate clone group name.

        clone_group_name = 'Clone of %s' % group_name

        # Check whether this group name is already used.

        dup_id = dbutil.get_group_id(cnx, clone_group_name)

        # Modify group name until we find one that isn't alrady used.

        ntry = 1
        while dup_id > 0:
            ntry += 1
            clone_group_name = 'Clone %d of %s' % (ntry, group_name)
            dup_id = dbutil.get_group_id(cnx, clone_group_name)

        # Now clone the group.

        clone_id = dbutil.clone_group(cnx, group_id, clone_group_name)

    # Generate redirect html document header to invoke the gropu editor for
    # the newly created document.

    url = ''
    if clone_id > 0:
        url = '%s/edit_group.py?id=%d&%s' % \
              (dbconfig.base_url, clone_id, dbargs.convert_args(qdict))
    else:
        url = '%s/query_groups.py?%s' % \
              (dbconfig.base_url, dbargs.convert_args(qdict))

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<meta http-equiv="refresh" content="0; url=%s" />' % url
    print '</head>'
    print '<body>'
    url = ''
    if clone_id > 0:
        print 'Cloned group %s' % group_name
    else:
        print 'Group not cloned.'
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
