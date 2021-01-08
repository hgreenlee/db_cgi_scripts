#! /usr/bin/python
#==============================================================================
#
# Name: add_override.py
#
# Purpose: CGI script to add an override.
#
# CGI arguments:
#
# id      - Override id.
# name    - Override name.
# value   - Override value.
# <qdict> - Standard query_projects.py arguments.
#
# Created: 7-Jan-2021  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbutil, dbargs
from dbdict import databaseDict


# Main procedure.

def main(stage_id, name, value, qdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])

    # Add override and redirect to stage editor.

    override_id = dbutil.add_override(cnx, stage_id, name, value)
    url = '%s/edit_stage.py?id=%d&%s' % \
          (dbconfig.base_url, stage_id, dbargs.convert_args(qdict))

    # Generate redirect page.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<meta http-equiv="refresh" content="0; url=%s" />' % url
    print '</head>'
    print '<body>'
    print 'Add override.'
    print '<br><br>'
    print 'If page does not automatically reload click this <a href=%s>link</a>' % url
    print '</body>'
    print '</html>'

    # Done.

    return

# End of definitions.  Executable code starts here.

if __name__ == "__main__":

    # Parse arguments.

    argdict = dbargs.get()
    qdict = dbargs.extract_qdict(argdict)
    stage_id = 0
    name = ''
    value = ''
    if 'id' in argdict:
        stage_id = int(argdict['id'])
    if 'name' in argdict:
        name = argdict['name']
    if 'value' in argdict:
        value = argdict['value']

    # Call main procedure.

    main(stage_id, name, value, qdict)
