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
import StringIO
import subprocess


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

    # Sample name.

    input = ''
    if 'input' in argdict:
        input = argdict['input']
    buf.write('Input dataset: %s\n' % input)

    # Experiment.

    exp = ''
    if 'exp' in argdict:
        exp = argdict['exp']
    buf.write('Experiment: %s\n' % exp)

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

    print '<form>'    

    # Generate document trailer.

    print '</body>'
    print '</html>'

    # Done.

    return


# Submit form data.

def submit(qdict, argdict):

    # This function is currently implemented to generate a text document containing
    # summary of the form data.

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

        # Scan files to determine new request id.

        reqid = 0
        for fn in os.listdir(dbconfig.request_dir):
            if fn.startswith('request_') and fn.endswith('.txt'):
                r = int(fn[8:-4])
                if reqid <= r:
                    reqid = r + 1

        # Make new request file.

        rfn = '%s/request_%d.txt' % (dbconfig.request_dir, reqid)
        f = open(rfn, 'w')
        f.write(gentext(argdict))
        f.close()

    # Maybe send email.

    if dbconfig.email != '':
        p = subprocess.Popen(['mail', '-s', 'Sample request', dbconfig.email], stdin=subprocess.PIPE)
        p.communicate(input=gentext(argdict))
        p.wait()

    # Generate message.

    print 'Sample request submitted.'
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

    numev = 0
    if 'num_events' in argdict:
        numev = int(argdict['num_events'])
    print '<tr>'
    print '<td><label for="num_events">Number of events: </label></td>'
    print '<td><input type="number" id="num_events" name="num_events" value=%d></td>' % numev
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
