#! /usr/bin/python
#==============================================================================
#
# Name: request.py
#
# Purpose: CGI script to generate a new sample request.
#
# CGI arguments:
#
# <qdict> - Standard query_projects.py arguments.
#
# Created: 9-Feb-2021  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbargs, dbutil
from dbdict import databaseDict
import StringIO
import subprocess
import datetime


# Convert arguments to text string.

def gentext(argdict):

    # This function generates a text document that summarizes form data contained in argdict.

    buf = StringIO.StringIO()

    # Requester.

    user = ''
    if 'user' in argdict:
        user = argdict['user']
    buf.write('Requester: %s\n' % user)

    # Sample name.

    name = ''
    if 'name' in argdict:
        name = argdict['name']
    buf.write('Sample name: %s\n' % name)

    # Sample description.

    description = ''
    if 'description' in argdict:
        description = argdict['description']
    buf.write('Sample description:\n')
    for line in description.splitlines():
        sline = line.rstrip()
        if sline != '':
            buf.write('%s\n' % sline)
    buf.write('\n')

    # Version.

    version = ''
    if 'version' in argdict:
        version = argdict['version']
    buf.write('Version: %s\n' % version)

    # Input dataset.

    input = ''
    if 'input' in argdict:
        input = argdict['input']
    buf.write('Input dataset: %s\n' % input)

    # Experiment.

    exp = ''
    if 'exp' in argdict:
        exp = argdict['exp']
    buf.write('Experiment: %s\n' % exp)

    # File type.

    ftype = ''
    if 'ftype' in argdict:
        ftype = argdict['ftype']
    buf.write('File type: %s\n' % ftype)

    # File type.

    role = ''
    if 'role' in argdict:
        role = argdict['role']
    buf.write('Role: %s\n' % role)

    # Campaign.

    camp = ''
    if 'camp' in argdict:
        camp = argdict['camp']
    buf.write('Campaign: %s\n' % camp)

    # Working group.

    wgroup = ''
    if 'wgroup' in argdict:
        wgroup = argdict['wgroup']
    buf.write('Working group: %s\n' % wgroup)

    # Target date.

    date = ''
    if 'date' in argdict:
        date = argdict['date']
    buf.write('Target date: %s\n' % date)

    # Priority.

    priority = ''
    if 'priority' in argdict:
        priority = argdict['priority']
    buf.write('Priority: %s\n' % priority)

    # Number of events.

    num_events = ''
    if 'num_events' in argdict:
        num_events = argdict['num_events']
    buf.write('Number of events: %s\n' % num_events)

    # Number of jobs.

    num_jobs = ''
    if 'num_jobs' in argdict:
        num_jobs = argdict['num_jobs']
    buf.write('Number of jobs: %s\n' % num_jobs)

    # Maximum files per job.

    max_files = ''
    if 'max_files' in argdict:
        max_files = argdict['max_files']
    buf.write('Maximum files per job: %s\n' % max_files)

    # Schema

    schema = ''
    if 'schema' in argdict:
        schema = argdict['schema']
    buf.write('Schema: %s\n' % schema)

    # Special instructions.

    instructions = ''
    if 'instructions' in argdict:
        instructions = argdict['instructions']
    buf.write('Special instructions:\n')
    for line in instructions.splitlines():
        sline = line.rstrip()
        if sline != '':
            buf.write('%s\n' % sline)
    buf.write('\n')

    # Generate an ordered list of stages and fcls.
    # Each element of the list will be a 2-tuple (stage, fcl).

    buf.write('\nFCL files:\n')
    buf.write('%-10s %-20s %10s %10s %10s\n' % ('Stage', 'FCL', 'Memory', 'Size/ev', 'Time/ev'))

    fcl_keys = []
    for key in argdict:
        if key.startswith('fcl_'):
            fcl_keys.append(key)

    fcllist = []
    for fcl_key in sorted(fcl_keys):
        stage_key = 'stage_%s' % fcl_key[4:]
        if stage_key in argdict:
            stage = argdict[stage_key]
            fcl = argdict[fcl_key]

            mem_key = 'memory_%s' % fcl_key[4:]
            memory = 0
            if mem_key in argdict:
                memory = int(argdict[mem_key])

            time_key = 'time_%s' % fcl_key[4:]
            time_event = 0
            if time_key in argdict:
                time_event = int(argdict[time_key])

            size_key = 'size_%s' % fcl_key[4:]
            size_event = 0
            if size_key in argdict:
                size_event = float(argdict[size_key])

            buf.write('%-10s %-20s %10d %10.2f %10d\n' % (stage, fcl, memory, time_event, size_event))

    # Done.

    return buf.getvalue()


# View form summary.

def view(qdict, argdict):

    # This function is currently implemented to generate a text document containing
    # summary of the form data.

    # Generate html document header.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<body>'

    # Generate preview.

    print '<pre>'
    for line in gentext(argdict).splitlines():
        sline = line.rstrip()
        print sline
    print '</pre>'

    # Add hidden form data with some buttons.

    print '<form action="%s/request.py" method="post" target="_self">' % dbconfig.rel_url

    # Add hidden form data.

    for key in qdict:
        print '<input type="hidden" name="%s" value="%s">' % (dbutil.convert_str(key),
                                                              dbutil.convert_str(qdict[key]))
    for key in argdict:
        if key != 'view':
            print '<input type="hidden" name="%s" value="%s">' % (dbutil.convert_str(key),
                                                                  dbutil.convert_str(argdict[key]))

    # Add buttons.

    print '<input type="submit" name="submit" value="Submit">'
    print '<input type="submit" name="reload" value="Back">'

    # Done with form.

    print '</form>'    

    # Generate document trailer.

    print '</body>'
    print '</html>'

    # Done.

    return


# Submit form data.

def submit(qdict, argdict):

    # This function is currently implemented to do the following actions.
    #
    # 1.  Add a project to the production database.
    # 2.  Optionally store a text document on the web server.
    # 3.  Optionally send an email containing a text summary.
    #
    # Whether actions 2 and 3 are taken depends on parameters "email" and "request_dir"
    # in dbconfig.py.

    # Generate a request name.
    # The request name is used to generate the name of the saved text file,
    # the subject of the email, and the project name in the database.
    # The request name is required to be different from any existing project name
    # in the database.  The request name is also required to be different from any
    # request file in the request directory.

    # Generate a base project name based on project name specified in form, if specified,
    # or based on a time stamp otherwise.

    base_name = ''
    if argdict.has_key('name'):
        base_name = argdict['name']
    else:
        base_name = 'request_%s' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    # Generate a non-existing project name based off base name.

    n = 0
    done = False
    request_name = ''
    cnx = dbconfig.connect(readonly = False, devel = qdict['dev'])
    c = cnx.cursor()

    while not done:

        if n == 0:
            request_name = base_name
        else:
            request_name = '%s_%d' % (base_name, n)

        # See if this candidate name already exists.

        q = 'SELECT COUNT(*) FROM projects WHERE name=%s'
        c.execute(q, (request_name,))
        row = c.fetchone()
        count = row[0]
        if count == 0:
            done = True
        else:
            n += 1

        # Check request directory.

        if done and dbconfig.request_dir != '':
            rfn = '%s/%s.txt' % (dbconfig.request_dir, request_name)
            if os.path.exists(rfn):
                done = False
                n += 1

    # Generate html document header.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<body>'

    # Maybe add request file.

    if dbconfig.request_dir != '':
        if not os.path.isdir(dbconfig.request_dir):
            os.makedirs(dbconfig.request_dir)

        # Make new request file.

        rfn = '%s/%s.txt' % (dbconfig.request_dir, request_name)
        f = open(rfn, 'w')
        f.write(gentext(argdict))
        f.close()

    # Maybe send email.

    if dbconfig.email != '':
        p = subprocess.Popen(['sendmail', dbconfig.email], stdin=subprocess.PIPE)
        message = 'Subject:Sample request %s\n%s' % (request_name, gentext(argdict))
        p.communicate(input=message)
        p.wait()

    # Construct query to add project.
    # Use values from form, or defaults.

    cols = databaseDict['projects']
    q = 'INSERT INTO projects SET name=%s'
    params = [request_name]

    # Loop over columns.

    for n in range(2, len(cols)):
        coltup = cols[n]
        colname = coltup[0]
        coltype = coltup[2]
        colarray = coltup[3]
        value = coltup[5]

        # Update default values.

        if colname == 'username' and argdict.has_key('user'):
            value = argdict['user']
        elif colname == 'description' and argdict.has_key('description'):
            value = argdict['description']
        elif colname == 'experiment' and argdict.has_key('exp'):
            value = argdict['exp']
        elif colname == 'file_type' and argdict.has_key('ftype'):
            value = argdict['ftype']
        elif colname == 'role' and argdict.has_key('role'):
            value = argdict['role']
        elif colname == 'campaign' and argdict.has_key('camp'):
            value = argdict['camp']
        elif colname == 'physics_group' and argdict.has_key('wgroup'):
            value = argdict['wgroup']
        elif colname == 'status':
            value = 'Requested'
        elif colname == 'num_events' and argdict.has_key('num_events'):
            value = argdict['num_events']
        elif colname == 'num_jobs' and argdict.has_key('num_jobs'):
            value = argdict['num_jobs']
        elif colname == 'max_files_per_job' and argdict.has_key('max_files'):
            value = argdict['max_files']
        elif colname == 'release_tag' and argdict.has_key('version'):
            value = argdict['version']
        elif colname == 'version' and argdict.has_key('version'):
            value = 'test_%s' % argdict['version']
        elif colname == 'validate_on_worker':
            value = 1

        # Update query to include this column

        if colarray:
            q += ',%s=%%s' % colname
            params.append(value)
        elif coltype[:3] == 'INT':
            q += ',%s=%%s' % colname
            params.append(value)
        elif coltype[:7] == 'VARCHAR':
            if value != None:
                q += ',%s=%%s' % colname
                params.append(value.replace('&', '&amp;'))
        elif coltype[:6] == 'DOUBLE':
            q += ',%s=%%s' % colname
            params.append(value)

    # Execute query.

    c.execute(q, params)

    # Get id of inserted row.

    q = 'SELECT LAST_INSERT_ID()'
    c.execute(q)
    row = c.fetchone()
    new_project_id = row[0]

    # Generate a list of stage keys in argdict.

    stage_keys = []
    for key in argdict:
        if key.startswith('stage_'):
            stage_keys.append(key)

    # Loop over stage keys in ascending order.

    stage_names = set()
    for stage_key in sorted(stage_keys):

        # Get the stage name for this key.

        stage_name = argdict[stage_key]

        # Only process this stage name if it hasn't already been seen.

        if stage_name not in stage_names:
            stage_names.add(stage_name)

            # Construct a query to insert a new stage row in database.

            stage_cols = databaseDict['stages']
            q = 'INSERT INTO stages SET name=%s,project_id=%s,seqnum=%s'
            params = [stage_name, new_project_id, len(stage_names)]

            # Loop over columns.

            for n in range(4, len(stage_cols)):
                stage_coltup = stage_cols[n]
                stage_colname = stage_coltup[0]
                stage_coltype = stage_coltup[2]
                stage_colarray = stage_coltup[3]
                value = stage_coltup[5]

                # Update default values.

                mem_key = 'memory_%s' % stage_key[6:]
                project_name = ''
                if argdict.has_key('name'):
                    project_name = argdict['name']
                else:
                    project_name = request_name
                if stage_colname == 'memory' and argdict.has_key(mem_key):
                    value = argdict[mem_key]
                elif stage_colname == 'inputdef' and len(stage_names) == 1 and argdict.has_key('input'):
                    value = argdict['input']
                elif (stage_colname == 'outdir' or stage_colname == 'logdir') and \
                     argdict.has_key('user') and argdict.has_key('exp'):
                    value = '/pnfs/%s/scratch/users/%s/output/%s/%s' % (
                        argdict['exp'], argdict['user'], project_name, stage_name)
                elif stage_colname == 'workdir' and argdict.has_key('user') and argdict.has_key('exp'):
                    value = '/pnfs/%s/resilient/users/%s/work/%s/%s' % (
                        argdict['exp'], argdict['user'], project_name, stage_name)
                elif stage_colname == 'bookdir' and argdict.has_key('user') and argdict.has_key('exp'):
                    value = '/%s/data/users/%s/book/%s/%s' % (
                        argdict['exp'], argdict['user'], project_name, stage_name)
                elif stage_colname == 'num_events' and argdict.has_key('num_events'):
                    value = argdict['num_events']
                elif stage_colname == 'num_jobs' and argdict.has_key('num_jobs'):
                    value = argdict['num_jobs']
                elif stage_colname == 'max_files_per_job' and argdict.has_key('max_files'):
                    value = argdict['max_files']
                elif stage_colname == 'schema_' and argdict.has_key('schema'):
                    value = argdict['schema']

                # Update query to include this column

                if stage_colarray:
                    q += ',%s=%%s' % stage_colname
                    params.append(value)
                elif stage_coltype[:3] == 'INT':
                    q += ',%s=%%s' % stage_colname
                    params.append(value)
                elif stage_coltype[:7] == 'VARCHAR':
                    if value != None:
                        q += ',%s=%%s' % stage_colname
                        params.append(value.replace('&', '&amp;'))
                elif stage_coltype[:6] == 'DOUBLE':
                    q += ',%s=%%s' % stage_colname
                    params.append(value)

            # Execute query.

            c.execute(q, params)

            # Get id of inserted row.

            q = 'SELECT LAST_INSERT_ID()'
            c.execute(q)
            row = c.fetchone()
            new_stage_id = row[0]

            # Find fcl files associated with this stage name.

            fcl_keys = []
            for key in argdict.keys():
                if key.startswith('stage_') and argdict[key] == stage_name:
                    fcl_key = 'fcl_%s' % key[6:]
                    if argdict.has_key(fcl_key):
                        fcl_keys.append(fcl_key)

            # Loop over fcl keys in ascending order.

            seq = 0
            for fcl_key in sorted(fcl_keys):
                seq += 1

                # Get fcl name for this key.

                fcl_name = argdict[fcl_key]

                # Construct a query to insert a new substage row in the database.

                substage_cols = databaseDict['substages']
                q = 'INSERT INTO substages SET fclname=%s,stage_id=%s,seqnum=%s'
                params = [fcl_name, new_stage_id, seq]

                # Loop over columns.

                for n in range(4, len(substage_cols)):
                    substage_coltup = substage_cols[n]
                    substage_colname = substage_coltup[0]
                    substage_coltype = substage_coltup[2]
                    substage_colarray = substage_coltup[3]
                    value = substage_coltup[5]

                    # Update query to include this column

                    if substage_colarray:
                        q += ',%s=%%s' % substage_colname
                        params.append(value)
                    elif substage_coltype[:3] == 'INT':
                        q += ',%s=%%s' % substage_colname
                        params.append(value)
                    elif substage_coltype[:7] == 'VARCHAR':
                        if value != None:
                            q += ',%s=%%s' % substage_colname
                            params.append(value.replace('&', '&amp;'))
                    elif substage_coltype[:6] == 'DOUBLE':
                        q += ',%s=%%s' % substage_colname
                        params.append(value)

                # Execute query.

                c.execute(q, params)

    # Commit database updates.

    cnx.commit()

    # Generate message.

    print 'Sample request %s submitted.' % request_name
    print '<br><br>'

    # Add hidden form data with some buttons.

    print '<form action="%s/request.py" method="post" target="_self">' % dbconfig.rel_url

    # Add hidden form data.

    for key in qdict:
        print '<input type="hidden" name="%s" value="%s">' % (dbutil.convert_str(key),
                                                              dbutil.convert_str(qdict[key]))
    for key in argdict:
        if key != 'submit':
            print '<input type="hidden" name="%s" value="%s">' % (dbutil.convert_str(key),
                                                                  dbutil.convert_str(argdict[key]))

    # Add buttons.

    print '<input type="submit" name="reload" value="Back">'

    # Done with form.

    print '<form>'    

    # Generate document trailer.

    print '</body>'
    print '</html>'

    # Done.

    return


# Generate sample request form.
 
def request_form(cnx, qdict, argdict):

    # Construct global disabled option for restricted controls.

    disabled = ''
    if not dbconfig.restricted_access_allowed() and dbutil.restricted_access(cnx, 'projects', id):
        disabled = 'disabled'

    #for key in qdict:
    #    print '%s = %s' % (key, qdict[key])
    #    print '<br>'

    #print '<br>'

    #for key in argdict:
    #    print '%s = %s' % (key, argdict[key])
    #    print '<br>'

    #print '<br>'

    # Generate form.

    print '<h2>Sample Request</h2>'
    print '<form action="%s/request.py" method="post" target="_self">' % dbconfig.rel_url
    print '<input type="submit" name="reload" value="Reload">'
    print '<br>'
    print '<br>'

    # Put input fields in a table.

    print '<table border=1 style="border-collapse:collapse">'

    # Add hidden qdict input fields.

    for key in qdict:
        print '<input type="hidden" name="%s" value="%s">' % (dbutil.convert_str(key),
                                                              dbutil.convert_str(qdict[key]))
    # Add readonly requester field.

    user = ''
    if 'SSO_USERID' in os.environ:
        user = os.environ['SSO_USERID']
    print '<tr>'
    print '<td><label for="user">Requester: </label></td>'
    print '<td><input type="text" id="user" name="user" value="%s" readonly></td>' % user
    print '</tr>'

    # Sample name field.

    name = ''
    if 'name' in argdict:
        name = argdict['name']
    print '<tr>'
    print '<td><label for="name">Sample name: </label></td>'
    print '<td><input type="text" id="name" name="name" size=80 value="%s"></td>' % name
    print '</tr>'

    # Sample description field.

    desc = ''
    if 'description' in argdict:
        desc = argdict['description']
    print '<tr>'
    print '<td><label for="description">Sample description: </label></td>'
    print '<td><textarea id="description" name="description" rows=2 cols=80>'
    print desc,
    print '</textarea></td>'
    print '</tr>'

    # Version field.

    version = ''
    if 'version' in argdict:
        version = argdict['version']
    print '<tr>'
    print '<td><label for="version">Release version: </label></td>'
    print '<td><input type="text" id="version" name="version" size=80 value="%s"></td>' % version
    print '</tr>'

    # Input dataset field.

    input = ''
    if 'input' in argdict:
        input = argdict['input']
    print '<tr>'
    print '<td><label for="input">Input dataset: </label></td>'
    print '<td><input type="text" id="input" name="input" size=80 value="%s"></td>' % input
    print '</tr>'

    # Experiment field.

    selexp = ''
    if 'exp' in argdict:
        selexp = argdict['exp']
    print '<tr>'
    print '<td><label for="exp">Experiment: </label></td>'
    print '<td><select id="exp" name="exp" size=0>'
    for experiment in dbconfig.pulldowns['experiment']:
        sel = ''
        if experiment == selexp:
            sel = 'selected'
        print '<option value="%s" %s>%s</option>' % (experiment, sel, experiment)
    print '</select></td>'
    print '</tr>'

    # File type field.

    selftype = ''
    if 'ftype' in argdict:
        selftype = argdict['ftype']
    print '<tr>'
    print '<td><label for="ftype">File type: </label></td>'
    print '<td><select id="ftype" name="ftype" size=0>'
    for file_type in dbconfig.pulldowns['file_type']:
        sel = ''
        if file_type == selftype:
            sel = 'selected'
        print '<option value="%s" %s>%s</option>' % (file_type, sel, file_type)
    print '</select></td>'
    print '</tr>'

    # Role field.

    selrole = ''
    if 'role' in argdict:
        selrole = argdict['role']
    print '<tr>'
    print '<td><label for="role">Role: </label></td>'
    print '<td><select id="role" name="role" size=0>'
    for role in dbconfig.pulldowns['role']:
        sel = ''
        if role == selrole:
            sel = 'selected'
        print '<option value="%s" %s>%s</option>' % (role, sel, role)
    print '</select></td>'
    print '</tr>'

    # Campaign field.

    selcamp = ''
    if 'camp' in argdict:
        selcamp = argdict['camp']
    print '<tr>'
    print '<td><label for="camp">Campaign: </label></td>'
    print '<td><select id="camp" name="camp" size=0>'
    for campaign in dbconfig.pulldowns['campaign']:
        sel = ''
        if campaign == selcamp:
            sel = 'selected'
        print '<option value="%s" %s>%s</option>' % (campaign, sel, campaign)
    print '</select></td>'
    print '</tr>'

    # Working group field.

    selgrp = ''
    if 'wgroup' in argdict:
        selgrp = argdict['wgroup']
    print '<tr>'
    print '<td><label for="wgroup">Working group: </label></td>'
    print '<td><select id="wgroup" name="wgroup" size=0>'
    for group in dbconfig.pulldowns['physics_group']:
        sel = ''
        if group == selgrp:
            sel = 'selected'
        print '<option value="%s" %s>%s</option>' % (group, sel, group)
    print '</select></td>'
    print '</tr>'

    # Target date field.

    date = ''
    if 'date' in argdict:
        date = argdict['date']
    print '<tr>'
    print '<td><label for="date">Target date: </label></td>'
    print '<td><input type="date" id="date" name="date" value="%s"></td>' % date
    print '</tr>'

    # Priority field.

    selpri = 'low'
    if 'priority' in argdict:
        selpri = argdict['priority']
    print '<tr>'
    print '<td><label for="priority">Priority: </label></td>'
    print '<td><select id="priority" name="priority" size=0>'
    for priority in ('low', 'medium', 'high'):
        sel = ''
        if priority == selpri:
            sel = 'selected'
        print '<option value="%s" %s>%s</option>' % (priority, sel, priority)
    print '</select></td>'
    print '</tr>'

    # Number of events field.

    num_events = 0
    if 'num_events' in argdict:
        num_events = int(argdict['num_events'])
    print '<tr>'
    print '<td><label for="num_events">Number of events: </label></td>'
    print '<td><input type="number" id="num_events" name="num_events" value=%d></td>' % num_events
    print '</tr>'

    # Number of jobs.

    num_jobs = 0
    if 'num_jobs' in argdict:
        num_jobs = int(argdict['num_jobs'])
    print '<tr>'
    print '<td><label for="num_jobs">Number of jobs: </label></td>'
    print '<td><input type="number" id="num_jobs" name="num_jobs" value=%d></td>' % num_jobs
    print '</tr>'

    # Maximum files per job.

    max_files = 0
    if 'max_files' in argdict:
        max_files = int(argdict['max_files'])
    print '<tr>'
    print '<td><label for="max_files">Maximum files per job: </label></td>'
    print '<td><input type="number" id="max_files" name="max_files" value=%d></td>' % max_files
    print '</tr>'

    # Schema field.

    selschema = ''
    if 'schema' in argdict:
        selschema = argdict['schema']
    print '<tr>'
    print '<td><label for="schema">Schema: </label></td>'
    print '<td><select id="schema" name="schema" size=0>'
    for schema in dbconfig.pulldowns['schema']:
        sel = ''
        if schema == selschema:
            sel = 'selected'
        print '<option value="%s" %s>%s</option>' % (schema, sel, schema)
    print '</select></td>'
    print '</tr>'

    # Sample instructions field.

    inst = ''
    if 'instructions' in argdict:
        inst = argdict['instructions']
    print '<tr>'
    print '<td><label for="instructions">Special instructions: </label></td>'
    print '<td><textarea id="instructions" name="instructions" rows=2 cols=80>'
    print inst,
    print '</textarea></td>'
    print '</tr>'

    # End of main table.

    print '</table>'

    # Generate an ordered list of existing fcls.
    # Each element of the list will be a 5-tuple (stage, fcl, memory, time, size).

    empty_tuple = ('', '', 0, 0, 0)
    fcl_keys = []
    for key in argdict:
        if key.startswith('fcl_'):
            fcl_keys.append(key)

    fcllist = []
    for fcl_key in sorted(fcl_keys):
        stage_key = 'stage_%s' % fcl_key[4:]
        if stage_key in argdict:
            stage = argdict[stage_key]
            fcl = argdict[fcl_key]

            mem_key = 'memory_%d' % len(fcllist)
            memory = 0
            if mem_key in argdict:
                memory = int(argdict[mem_key])

            time_key = 'time_%d' % len(fcllist)
            time_event = 0
            if time_key in argdict:
                time_event = int(argdict[time_key])

            size_key = 'size_%d' % len(fcllist)
            size_event = 0
            if size_key in argdict:
                size_event = float(argdict[size_key])

            fcl_tuple = (stage, fcl, memory, time_event, size_event)

            # Check for insert fcl.

            insert_key = 'insert_%d' % len(fcllist)
            if insert_key in argdict:
                fcllist.append(empty_tuple)

            # Check for clone fcl.

            clone_key = 'clone_%d' % len(fcllist)
            if clone_key in argdict:
                fcllist.append(fcl_tuple)

            # Check for delete fcl.

            delete_key = 'delete_%d' % len(fcllist)
            if delete_key in argdict:

                # Only process this delete action once.

                del argdict[delete_key]
                continue

            # Check move up/down.

            if len(fcllist) > 0:
                up_key = 'up_%d' % len(fcllist)
                down_key = 'down_%d' % (len(fcllist)-1)
                if up_key in argdict or down_key in argdict:

                    # Insert this (stage, key) in the next to last position.

                    fcllist.insert(len(fcllist)-1, fcl_tuple)
                    continue

            # Add this (stage, fcl).

            fcllist.append(fcl_tuple)

    # If the number of fcl files is zero, or the last stage is not blank,
    # add a new blank stage at the end.

    if len(fcllist) == 0 or fcllist[-1][0] != '':
        fcllist.append(empty_tuple)

    # Generate FCL table.

    print '<h3>FCL Files</h3>'
    print '<table border=1 style="border-collapse:collapse">'
    print '<tr>'
    print '<th>Stage</th>'
    print '<th>FCL File</th>'
    print '<th>&nbsp;Memory (MB)&nbsp;</th>'
    print '<th>&nbsp;Time/ev (sec)&nbsp;</th>'
    print '<th>&nbsp;Size/ev (MB)&nbsp;</th>'
    print '</tr>'

    # Add editable fields for existing fcl files.

    n = 0
    for fcltuple in fcllist:
        stage = fcltuple[0]
        fcl = fcltuple[1]
        memory = fcltuple[2]
        time_event = fcltuple[3]
        size_event = fcltuple[4]

        print '<tr>'
        print '<td><input type="text" id="stage_%d" name="stage_%d" size-20 value="%s"></td>' % (n, n, stage)
        print '<td><input type="text" id="fcl_%d" name="fcl_%d" size=80 value="%s"></td>' % (n, n, fcl)
        print '<td><input type="number" id="memory_%d" name="memory_%d" size=12 value=%d></td>' % (n, n, memory)
        print '<td><input type="number" id="time_%d" name="time_%d" size=12 value=%d></td>' % (n, n, time_event)
        print '<td><input type="number" id="size_%d" name="size_%d" size=12 step=0.01 value=%8.2f></td>' % (n, n, size_event)

        # Add insert button.

        print '<td>'
        print '<div title="Insert FCL">'
        print '<input type="submit" id="insert_%d" name="insert_%d" value="&#x2795;">' % (n, n)
        print '</div>'
        print '</td>'

        # Add clone button.

        print '<td>'
        print '<div title="Clone FCL">'
        print '<input type="submit" id="clone_%d" name="clone_%d" value="&#x2398;">' % (n, n)
        print '</div>'
        print '</td>'

        # Add delete button.

        print '<td>'
        print '<div title="Delete FCL">'
        print '<input type="submit" id="delete_%d" name="delete_%d" value="&#x1f5d1;">' % (n, n)
        print '</div>'
        print '</td>'        

        # Add Up button.

        print '<td>'
        print '<div title="Move up">'
        print '<input type="submit" id="up_%d" name="up_%d" value="&#x25b2;">' % (n, n)
        print '</div>'
        print '</td>'        

        # Add Down button.

        print '<td>'
        print '<div title="Move down">'
        print '<input type="submit" id="down_%d" name="down_%d" value="&#x25bc;">' % (n, n)
        print '</div>'
        print '</td>'        

        print '</tr>'
        n += 1

    # End of FCL table.

    print '</table>'

    # Add submit and cancel buttons.

    print '<br>'
    print '<input type="submit" name="submit" value="Submit" %s>' % disabled
    print '<input type="submit" name="view" value="View" %s>' % disabled
    print '<input type="submit" name="clear" value="Clear">'
    print '<input type="submit" name="cancel" value="Cancel">'

    # End of form.

    print '</form>'

    # Done.

    return


# Main procedure.

def main(qdict, argdict):

    # Open database connection.

    cnx = dbconfig.connect(readonly = True, devel = qdict['dev'])

    # Generate html document header.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<title>Sample Request</title>'
    print '</head>'
    print '<body>'
    print '<a href=%s/query_projects.py?%s>Project list</a><br>' % \
        (dbconfig.base_url, dbargs.convert_args(qdict))

    # Generate main part of html document.

    request_form(cnx, qdict, argdict)

    # Generate html document trailer.
    
    print '</body>'
    print '</html>'

    # Done.

    return


# End of definitions.  Executable code starts here.

if __name__ == "__main__":

    # Parse arguments.

    argdict = dbargs.get()
    qdict = dbargs.extract_qdict(argdict)
    for key in qdict:
        if key in argdict:
            del argdict[key]

    # Maybe clear form.

    if 'clear' in argdict:
        argdict = {}

    # Maybe submit form.

    if 'submit' in argdict:
        submit(qdict, argdict)
        sys.exit(0)

    # Maybe view form summary.

    if 'view' in argdict:
        view(qdict, argdict)
        sys.exit(0)

    # If the user hit the cancel button, redirect to project list.

    if 'cancel' in argdict:

        # Calculate redirect url.

        url = '%s/query_projects.py?%s' % (dbconfig.base_url, dbargs.convert_args(qdict))

        # Generate redirect html document.

        print 'Content-type: text/html'
        print 'Status: 303 See Other'
        print 'Location: %s' % url
        print
        print '<!DOCTYPE html>'
        print '<html>'
        print '<body>'
        print 'If page does not automatically reload click this <a href=%s>link</a>' % url
        print '</body>'
        print '</html>'
        sys.exit(0)

    # Call main procedure.

    main(qdict, argdict)
