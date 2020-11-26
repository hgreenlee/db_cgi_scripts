#==============================================================================
#
# Name: dbutil.py
#
# Purpose: Python database utility module containing various useful functions.
#
# Created: 15-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig
from dbdict import databaseDict
import xml.etree.ElementTree as ET


# Convert bytes or unicode to default python str type.
# Works on python 2 and python 3.

def convert_str(s):

    result = ''

    if type(s) == type(''):

        # Already a default str.
        # Just return the original.

        result = s

    elif type(s) == type(u''):

        # Unicode and not str.
        # Convert to bytes.

        result = s.encode()

    elif type(s) == type(b''):

        # Bytes and not str.
        # Convert to unicode.

        result = s.decode()

    else:

        # Last resort, use standard str conversion.

        result = str(s)

    return result


# Check whether connection is read only or read/write.

def is_readonly(cnx):

    result = cnx.user.endswith('reader')
    return result


# Get list of defined tables.

def get_tables(cnx):

    result = []

    # Query table names.

    c = cnx.cursor()
    q = 'SELECT table_name FROM information_schema.tables WHERE table_schema="%s";' % cnx.database
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        table_name = convert_str(row[0])
        result.append(table_name)

    # Done.

    return result


# List projects.

def list_projects(cnx):

    result = []

    # Query projects from database.

    c = cnx.cursor()
    q = 'SELECT name FROM projects'
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        project_name = row[0]
        result.append(project_name)

    # Done.

    return result


# List datasets.

def list_datasets(cnx):

    result = []

    # Query datasets from database.

    c = cnx.cursor()
    q = 'SELECT name FROM datasets'
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        dataset_name = row[0]
        result.append(dataset_name)

    # Done.

    return result


# Get project id.

def get_project_id(cnx, project_name):

    result = 0

    # Query project id from database.

    c = cnx.cursor()
    q = 'SELECT id, name FROM projects WHERE name=\'%s\'' % project_name
    c.execute(q)
    rows = c.fetchall()
    if len(rows) > 0:
        result = rows[0][0]

    # Done.

    return result


# Get project name.

def get_project_name(cnx, id):

    result = ''

    # Query project name from database.

    c = cnx.cursor()
    q = 'SELECT id, name FROM projects WHERE id=%d' % id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) > 0:
        result = rows[0][1]

    # Done.

    return result


# Get string array.

def get_strings(cnx, array_id):

    result = []

    # Query database.

    c = cnx.cursor()
    q = 'SELECT array_id, value FROM strings WHERE array_id=%d' % array_id
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        result.append(row[1])

    # Done.

    return result


# Insert string array.

def insert_strings(cnx, strings):

    array_id = 0
    if strings != None and len(strings) > 0:

        c = cnx.cursor()

        # Get next array id.

        q = 'SELECT MAX(array_id) FROM strings'
        c.execute(q)
        row = c.fetchone()
        n = row[0]
        if n == None:
            array_id = 1
        else:
            array_id = n + 1

        # Insert values.

        for value in strings:
            q = 'INSERT INTO strings SET array_id=%d, value=\'%s\'' % (array_id, value)
            c.execute(q)

    # Done.

    return array_id


# Update string array.
# Check is specified string array already exists.  If so return existing array id.
# Otherwise insert new string array.

def update_strings(cnx, strings):

    result = 0

    # Make sure we are comparing standard python strings.

    std_strings = []
    for s in strings:
        std_strings.append(convert_str(s))

    if strings != None and len(strings) > 0:

        c = cnx.cursor()

        # Look for candidate array ids matching first string element.

        c_array_ids = []
        q = 'SELECT array_id, value FROM strings WHERE value=\'%s\'' % strings[0]
        c.execute(q)
        rows = c.fetchall()
        for row in rows:
            c_array_ids.append(row[0])

        # Loop over candidate array ids to look for matches.

        for array_id in c_array_ids:
            q = 'SELECT array_id, value FROM strings WHERE array_id=%d' % array_id
            c.execute(q)
            rows = c.fetchall()
            values = []
            for row in rows:
                values.append(convert_str(row[1]))
            if values == std_strings:
                result = array_id
                break

        # If we didn't find a match, insert this string array.

        if result == 0:
            result = insert_strings(cnx, strings)

    # Done.

    return result


# Find number of references to a particular array_id.

def refcount_strings(cnx, array_id):

    result = 0
    if array_id != 0:

        c = cnx.cursor()

        # Loop over tables.

        for table in databaseDict:

            # Loop over array columns

            cols = databaseDict[table]
            for n in range(len(cols)):
                coltup = cols[n]
                colname = coltup[0]
                colarray = coltup[3]
                if colarray:

                    # Construct query to count matching rows.

                    q = 'SELECT COUNT(*) FROM %s WHERE %s=%d' % (table, colname, array_id)
                    c.execute(q)
                    row = c.fetchone()
                    result += row[0]

    # Done.

    return result


# Delete string array.

def delete_strings(cnx, array_id):

    # Delete string array.

    c = cnx.cursor()
    q = 'DELETE FROM strings WHERE array_id=%d' % array_id
    c.execute(q)

    # Done.

    return


# Delete unreferenced string arrays.

def clean_strings(cnx):

    # Query all string array_ids.

    array_ids = []
    c = cnx.cursor()
    q = 'SELECT DISTINCT array_id FROM strings'
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        array_ids.append(row[0])

    # Loop over array ids.

    for array_id in array_ids:
        n = refcount_strings(cnx, array_id)
        if n == 0:
            delete_strings(cnx, array_id)


# Export substage.

def export_substage(cnx, substage_id, xml):

    # Query substage from database.

    c = cnx.cursor()
    q = 'SELECT * FROM substages WHERE id=%d' % substage_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch substage id %d' % substage_id)
    row = rows[0]
    xml.write('    <fcl>\n      %s\n' % row[1])

    # Loop over remaining columns/elements.

    cols = databaseDict['substages']
    for n in range(len(cols)):
        coltup = cols[n]
        element = coltup[1]
        if element != '':
            if coltup[3]:

                # This a repeated string element.

                for st in get_strings(cnx, row[n]):
                    xml.write('      <%s>%s</%s>\n' % (element, st.replace('&', '&amp;'), element))

            else:

                # Scalar element.

                if coltup[2][:3] == 'INT':
                    xml.write('      <%s>%d</%s>\n' % (element, row[n], element))
                elif coltup[2][:7] == 'VARCHAR' and row[n] != '':
                    xml.write('      <%s>%s</%s>\n' % (element, row[n].replace('&', '&amp;'),
                                                     element))
                elif coltup[2][:6] == 'DOUBLE':
                    xml.write('      <%s>%8.6f</%s>\n' % (element, row[n], element))

    # Done

    xml.write('    </fcl>\n')
    return


# Export stage.

def export_stage(cnx, stage_id, xml):

    # Query stage from database.

    c = cnx.cursor()
    q = 'SELECT * FROM stages WHERE id=%d' % stage_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch stage id %d' % stage_id)
    row = rows[0]
    xml.write('  <stage name="%s">\n' % row[1])

    # Loop over remaining columns/elements.

    cols = databaseDict['stages']
    for n in range(len(cols)):
        coltup = cols[n]
        element = coltup[1]
        if element != '':
            if coltup[3]:

                # This a repeated string element.

                for st in get_strings(cnx, row[n]):
                    xml.write('    <%s>%s</%s>\n' % (element, st.replace('&', '&amp;'), element))

            else:

                # Scalar element.

                if coltup[2][:3] == 'INT':
                    xml.write('    <%s>%d</%s>\n' % (element, row[n], element))
                elif coltup[2][:7] == 'VARCHAR' and row[n] != '':
                    xml.write('    <%s>%s</%s>\n' % (element, row[n].replace('&', '&amp;'),
                                                     element))
                elif coltup[2][:6] == 'DOUBLE':
                    xml.write('    <%s>%8.6f</%s>\n' % (element, row[n], element))

    # Query substage ids for this stage.

    q = 'SELECT id FROM substages WHERE stage_id=%d ORDER BY seqnum' % stage_id
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        substage_id = row[0]
        export_substage(cnx, substage_id, xml)

    # Done.

    xml.write('  </stage>\n')
    return


# Export project.

def export_project(cnx, project_id, xml):

    # Open xml file.

    xml.write('<?xml version="1.0"?>\n')
    xml.write('<!DOCTYPE project>\n')
    xml.write('<job>\n')

    # Query project from database.

    c = cnx.cursor()
    q = 'SELECT * FROM projects WHERE id=%d' % project_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch project id %d' % project_id)
    row = rows[0]
    xml.write('<project name="%s">\n' % row[1])

    # Loop over remaining columns/elements.

    cols = databaseDict['projects']
    subelement = ''
    indent = ''
    for n in range(len(cols)):
        coltup = cols[n]
        elements = coltup[1].split('/')
        element = elements[-1]
        if element != '':
            new_subelement = ''
            if len(elements) > 1:
                new_subelement = elements[0]

            if new_subelement != subelement:
                if subelement != '':
                    xml.write('  </%s>\n' % subelement)
                    indent = ''
                subelement = new_subelement
                if subelement != '':
                    xml.write('  <%s>\n' % subelement)
                    indent = '  '

            if coltup[3]:

                # This a repeated string element.

                for st in get_strings(cnx, row[n]):
                    xml.write('  %s<%s>%s</%s>\n' % (indent, element,
                                                     st.replace('&', '&amp;'), element))

            else:

                # Scalar element.

                if coltup[2][:3] == 'INT':
                    xml.write('  %s<%s>%d</%s>\n' % (indent, element, row[n], element))
                elif coltup[2][:7] == 'VARCHAR' and row[n] != '':
                    xml.write('  %s<%s>%s</%s>\n' % (indent, element,
                                                     row[n].replace('&', '&amp;'), element))
                elif coltup[2][:6] == 'DOUBLE':
                    xml.write('  %s<%s>%8.6f</%s>\n' % (indent, element, row[n], element))

    if subelement != '':
        xml.write('  </%s>\n' % subelement)

    # Query and loop over stage ids for this project.

    q = 'SELECT id FROM stages WHERE project_id=%d ORDER BY seqnum' % project_id
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        stage_id = row[0]
        export_stage(cnx, stage_id, xml)

    # Done.

    xml.write('</project>\n')
    xml.write('</job>\n')
    return


# Export poms ini file corresponding to project.

def export_poms_project(cnx, project_id, dev, ini):

    # Query information about this project.

    c = cnx.cursor()
    q = '''SELECT name, release_tag, poms_campaign, poms_login_setup, poms_job_type 
           FROM projects WHERE id=%d''' % project_id
    c.execute(q)
    rows = c.fetchall()
    row = rows[0]
    name = row[0]
    version = row[1]
    poms_campaign = row[2]
    poms_login_setup = row[3]
    poms_job_type = row[4]
    if poms_campaign == '':
        poms_campaign = name

    # Query stage names and ids corresonding to this project.

    stage_ids = []
    stage_names = []
    q = 'SELECT id, name FROM stages WHERE project_id=%d' % project_id
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        stage_ids.append(row[0])
        stage_names.append(row[1])

    # Campaign section.

    ini.write('[campaign]\n')
    ini.write('experiment=%s\n' % dbconfig.experiment)
    ini.write('poms_role=production\n')
    ini.write('name=%s\n' % poms_campaign)
    ini.write('stage=Active\n')
    ini.write('campaign_keywords={}\n')
    ini.write('campaign_stage_list=%s\n' % ','.join(stage_names))
    ini.write('\n')

    # Campaign defaults section.

    ini.write('[campaign_defaults]\n')
    ini.write('vo_role=Production\n')
    ini.write('software_version=v1_0\n')
    ini.write('dataset_or_split_data=\n')
    ini.write('cs_split_type=\n')
    ini.write('completion_type=located\n')
    ini.write('completion_pct=95\n')
    ini.write('param_overrides=[]\n')
    ini.write('test_param_overrides=[]\n')
    ini.write('merge_overrides=\n')
    ini.write('login_setup=generic\n')
    ini.write('job_type=generic\n')
    ini.write('stage_type=regular\n')
    ini.write('output_ancestor_depth=1\n')
    ini.write('\n')

    # Loop over stages.

    for stage_id in stage_ids:

        # Query information about this stage.

        q = 'SELECT name, poms_stage FROM stages WHERE id=%d' % stage_id
        c.execute(q)
        rows = c.fetchall()
        row = rows[0]
        stage_name = row[0]
        poms_stage = row[1]
        if poms_stage == '':
            poms_stage = stage_name

        # Campaign stage section.

        url = '%s/export.py?id=%d' % (dbconfig.cgi_url, project_id)
        if dev != 0:
            url += '&dev=%d' % dev
        ini.write('[campaign_stage %s]\n' % poms_stage)
        ini.write('software_version=%s\n' % version)
        ini.write('dataset_or_split_data=\n')
        ini.write('cs_split_type=draining\n')
        ini.write('completion_type=located\n')
        ini.write('param_overrides=[["--xml", "%s"], ["--stage", "%s"]]\n' % (url, stage_name))
        ini.write('login_setup=%s\n' % poms_login_setup)
        ini.write('job_type=%s\n' % poms_job_type)
        ini.write('merge_overrides=False\n')
        ini.write('stage_type=regular\n')
        ini.write('\n')

        
        

# Delete substage.

def delete_substage(cnx, substage_id):

    # Check access.

    if not dbconfig.restricted_access_allowed() and restricted_access(cnx, 'substages', substage_id):
        restricted_error()

    # Delete substage.

    c = cnx.cursor()
    q = 'DELETE FROM substages WHERE id=%d' % substage_id
    c.execute(q)

    # Done.

    cnx.commit()
    return


# Delete stage.

def delete_stage(cnx, stage_id):

    # Check access.

    if not dbconfig.restricted_access_allowed() and restricted_access(cnx, 'stages', stage_id):
        restricted_error()

    # Delete substages belonging to this stage.

    c = cnx.cursor()
    q = 'SELECT id FROM substages WHERE stage_id=%d' % stage_id
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        substage_id = row[0]
        delete_substage(cnx, substage_id)

    # Delete stage.

    q = 'DELETE FROM stages WHERE id=%d' % stage_id
    c.execute(q)

    # Done.

    cnx.commit()
    return


# Delete project.

def delete_project(cnx, project_id):

    # Check access.

    if not dbconfig.restricted_access_allowed() and restricted_access(cnx, 'projects', project_id):
        restricted_error()

    # Delete stages belonging to this project.

    c = cnx.cursor()
    q = 'SELECT id FROM stages WHERE project_id=%d' % project_id
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        stage_id = row[0]
        delete_stage(cnx, stage_id)

    # Delete project.

    q = 'DELETE FROM projects WHERE id=%d' % project_id
    c.execute(q)

    # Delete unreferenced string arrays.

    clean_strings(cnx)

    # Done.

    cnx.commit()
    return


# Clone substage.

def clone_substage(cnx, substage_id, stage_id):

    # Query substage from database.

    c = cnx.cursor()
    q = 'SELECT * FROM substages WHERE id=%d' % substage_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch substage id %d' % substage_id)
    row = rows[0]
    fclname = row[1]
    seqnum = row[3]

    # Check access.

    if not dbconfig.restricted_access_allowed() and restricted_access(cnx, 'stages', stage_id):
        restricted_error()

    # Increment sequence number, and make sure the new sequence number of free.

    seqnum += 1
    free_seqnum_substage(cnx, stage_id, seqnum)

    # Construct query to insert a new row into substages table that is
    # a copy of the row that we just read.

    cols = databaseDict['substages']
    q = 'INSERT INTO substages SET fclname=\'%s\',stage_id=%d,seqnum=%d' % \
        (fclname, stage_id, seqnum)
    for n in range(4, len(cols)):
        coltup = cols[n]
        colname = coltup[0]
        coltype = coltup[2]
        colarray = coltup[3]
        if colarray:
            q += ',%s=%d' % (colname, row[n])
        elif coltype[:3] == 'INT':
            q += ',%s=%d' % (colname, row[n])
        elif coltype[:7] == 'VARCHAR':
            q += ',%s=\'%s\'' % (colname, row[n].replace('&', '&amp;').replace("'", "\\'"))
        elif coltype[:6] == 'DOUBLE':
            q += ',%s=%8.6f' % (colname, row[n])
    c.execute(q)

    # Get id of inserted row.

    q = 'SELECT LAST_INSERT_ID()'
    c.execute(q)
    row = c.fetchone()
    new_substage_id = row[0]

    # Done.

    cnx.commit()
    return new_substage_id


# Clone stage.

def clone_stage(cnx, stage_id, project_id):

    # Query stage from database.

    c = cnx.cursor()
    q = 'SELECT * FROM stages WHERE id=%d' % stage_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch stage id %d' % stage_id)
    row = rows[0]
    stage_name = row[1]
    seqnum = row[3]

    # Check access.

    if not dbconfig.restricted_access_allowed() and restricted_access(cnx, 'projects', project_id):
        restricted_error()

    # Increment sequence number, and make sure the new sequence number of free.

    seqnum += 1
    free_seqnum_stage(cnx, project_id, seqnum)

    # Construct query to insert a new row into stages table that is
    # a copy of the row that we just read.

    cols = databaseDict['stages']
    q = 'INSERT INTO stages SET name=\'%s\',project_id=%d,seqnum=%d' % \
        (stage_name, project_id, seqnum)
    for n in range(4, len(cols)):
        coltup = cols[n]
        colname = coltup[0]
        coltype = coltup[2]
        colarray = coltup[3]
        if colarray:
            q += ',%s=%d' % (colname, row[n])
        elif coltype[:3] == 'INT':
            q += ',%s=%d' % (colname, row[n])
        elif coltype[:7] == 'VARCHAR':
            q += ',%s=\'%s\'' % (colname, row[n].replace('&', '&amp;').replace("'", "\\'"))
        elif coltype[:6] == 'DOUBLE':
            q += ',%s=%8.6f' % (colname, row[n])
    c.execute(q)

    # Get id of inserted row.

    q = 'SELECT LAST_INSERT_ID()'
    c.execute(q)
    row = c.fetchone()
    new_stage_id = row[0]

    # Clone substages belonging to this stage.

    q = 'SELECT id FROM substages WHERE stage_id=%d' % stage_id
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        substage_id = row[0]
        clone_substage(cnx, substage_id, new_stage_id)

    # Done.

    cnx.commit()
    return new_stage_id


# Clone project.
# Return newly created project id.

def clone_project(cnx, project_id, project_name):

    # See if the new project already exists.

    c = cnx.cursor()
    q = 'SELECT COUNT(*) FROM projects WHERE name=\'%s\'' % project_name
    c.execute(q)
    row = c.fetchone()
    n = row[0]
    if n > 0:
        print 'Project %s already exists.' % project_name
        return

    # Query project from database.

    q = 'SELECT * FROM projects WHERE id=%d' % project_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch project id %d' % project_id)
    row = rows[0]

    # Construct query to insert a new row into projects table that is
    # a copy of the row that we just read.

    cols = databaseDict['projects']
    q = 'INSERT INTO projects SET name=\'%s\'' % project_name
    user = dbconfig.getuser()
    if user != '':
        q += ',username=\'%s\'' % user
    for n in range(3, len(cols)):
        coltup = cols[n]
        colname = coltup[0]
        coltype = coltup[2]
        colarray = coltup[3]
        value = row[n]

        # Reset status of cloned dataset to blank ('').

        if colname == 'status':
            value = ''

        if colarray:
            q += ',%s=%d' % (colname, value)
        elif coltype[:3] == 'INT':
            q += ',%s=%d' % (colname, value)
        elif coltype[:7] == 'VARCHAR':
            q += ',%s=\'%s\'' % (colname, value.replace('&', '&amp;').replace("'", "\\'"))
        elif coltype[:6] == 'DOUBLE':
            q += ',%s=%8.6f' % (colname, value)
    c.execute(q)

    # Get id of inserted row.

    q = 'SELECT LAST_INSERT_ID()'
    c.execute(q)
    row = c.fetchone()
    new_project_id = row[0]

    # Clone stages belonging to this project.
    # Cloned stages will have the same names as the original stages.

    q = 'SELECT id FROM stages WHERE project_id=%d' % project_id
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        stage_id = row[0]
        clone_stage(cnx, stage_id, new_project_id)

    # Done.

    cnx.commit()
    return new_project_id


# Make sure the specified substage sequence number is not used.
# If it is already used, increment all sequence numbers equal or larger by one.

def free_seqnum_substage(cnx, stage_id, seqnum):

    c = cnx.cursor()

    # See if this sequence number is already used.

    q = 'SELECT COUNT(*) FROM substages WHERE stage_id=%d AND seqnum=%d' % (stage_id, seqnum)
    c.execute(q)
    row = c.fetchone()
    n = row[0]
    if n > 0:

        # Got a match.
        # Query all sequence numbers equal or greater.

        q = 'SELECT id, stage_id, seqnum FROM substages WHERE stage_id=%d AND seqnum>=%d' % \
            (stage_id, seqnum)
        c.execute(q)
        rows = c.fetchall()
        for row in rows:
            substage_id = row[0]
            seq = row[2]

            # Increment sequence number.

            q = 'UPDATE substages SET seqnum=%d WHERE id=%d' % (seq+1, substage_id)
            c.execute(q)

    # Done.

    return


# Make sure the specified substage sequence number is not used.
# If it is already used, increment all sequence numbers equal or larger by one.

def free_seqnum_stage(cnx, project_id, seqnum):

    c = cnx.cursor()

    # See if this sequence number is already used.

    q = 'SELECT COUNT(*) FROM stages WHERE project_id=%d AND seqnum=%d' % (project_id, seqnum)
    c.execute(q)
    row = c.fetchone()
    n = row[0]
    if n > 0:

        # Got a match.
        # Query all sequence numbers equal or greater.

        q = 'SELECT id, project_id, seqnum FROM stages WHERE project_id=%d AND seqnum>=%d' % \
            (project_id, seqnum)
        c.execute(q)
        rows = c.fetchall()
        for row in rows:
            stage_id = row[0]
            seq = row[2]

            # Increment sequence number.

            q = 'UPDATE stages SET seqnum=%d WHERE id=%d' % (seq+1, stage_id)
            c.execute(q)

    # Done.

    return


# Import substage from substage xml element.
# Returns newly inserted substage id.

def import_substage(cnx, substage, stage_id, seqnum):

    result = 0
    c = cnx.cursor()

    # Extract fcl name attribute.

    fclname = substage.text

    # Prepare query to insert this substage into database.

    q = 'INSERT INTO substages SET stage_id=%d,seqnum=%d' % (stage_id, seqnum)
    if fclname != '':
        q += ',fclname=\'%s\'' % fclname

    # Loop over dictionary elements for table stages.

    for coltup in databaseDict['substages']:
        colname = coltup[0]
        coltag = coltup[1]
        coltype = coltup[2]
        colarray = coltup[3]
        coldefault = coltup[5]
        #print colname, coltag, coltype, colarray

        # Hunt for subelements with matching tag.

        if coltag != '':
            if colarray == 0:

                # Scalar types handled here.
                # Get one subelement with matching tag, if any.

                xmlpath = './%s' % coltag
                child = substage.find(xmlpath)
                if child != None:
                    value = child.text
                    if coltype[:3] == 'INT':
                        q += ',%s=%d' % (colname, int(value))
                    elif coltype[:6] == 'DOUBLE':
                        q += ',%s=%8.6f' % (colname, float(value))
                    elif coltype[:7] == 'VARCHAR':
                        q += ',%s=\'%s\'' % (colname, value.replace("'", "\\'"))
                else:
                    if coltype[:3] == 'INT':
                        q += ',%s=%d' % (colname, coldefault)
                    elif coltype[:6] == 'DOUBLE':
                        q += ',%s=%8.6f' % (colname, coldefault)
                    elif coltype[:7] == 'VARCHAR':
                        q += ',%s=\'%s\'' % (colname, coldefault)

            else:

                # Arrays handled here.
                # Get multiple subelements with matching tag.

                values = []
                children = substage.findall(coltag)
                for child in children:
                    values.append(child.text)
                string_id = update_strings(cnx, values)
                q += ',%s=%d' % (colname, string_id)
                    
    # Execute query.

    c.execute(q)

    # Get id of inserted row.

    q = 'SELECT LAST_INSERT_ID()'
    c.execute(q)
    row = c.fetchone()
    substage_id = row[0]
    result = substage_id

    # Done

    cnx.commit()
    return result


# Import stage from stage xml element.
# Returns newly inserted stage id.

def import_stage(cnx, stage, project_id, seqnum):

    result = 0
    c = cnx.cursor()

    # Extract stage name attribute.

    name = ''
    if 'name' in stage.attrib:
        name = stage.attrib['name']

    # Prepare query to insert this stage into database.

    q = 'INSERT INTO stages SET project_id=%d,seqnum=%d' % (project_id, seqnum)
    if name != '':
        q += ',name=\'%s\'' % name

    # Loop over dictionary elements for table stages.

    for coltup in databaseDict['stages']:
        colname = coltup[0]
        coltag = coltup[1]
        coltype = coltup[2]
        colarray = coltup[3]
        coldefault = coltup[5]
        #print colname, coltag, coltype, colarray, coldefault, type(coldefault)

        # Hunt for subelements with matching tag.

        if coltag != '':
            if colarray == 0:

                # Scalar types handled here.
                # Get one subelement with matching tag, if any.

                xmlpath = './%s' % coltag
                child = stage.find(xmlpath)
                if child != None:
                    value = child.text
                    if coltype[:3] == 'INT':
                        q += ',%s=%d' % (colname, int(value))
                    elif coltype[:6] == 'DOUBLE':
                        q += ',%s=%8.6f' % (colname, float(value))
                    elif coltype[:7] == 'VARCHAR':
                        q += ',%s=\'%s\'' % (colname, value.replace("'", "\\'"))

                        # Add datasets.

                        if (colname == 'defname' or colname == 'ana_defname') and value != '':
                            add_dataset(cnx, project_id, 'output', value)
                        if colname == 'inputdef' and value != '':
                            add_dataset(cnx, project_id, 'input', value)

                else:

                    # If this same tag exists in the project definition, 
                    # get the default value from the project id.

                    inherit = False
                    for ptup in databaseDict['projects']:
                        if ptup[1] == coltag:
                            inherit = True
                            break
                    if inherit:
                        q2 = 'SELECT %s FROM projects WHERE id=%d' % (colname, project_id)
                        c.execute(q2)
                        rows = c.fetchall()
                        row = rows[0]
                        coldefault = row[0]

                    if coltype[:3] == 'INT':
                        q += ',%s=%d' % (colname, coldefault)
                    elif coltype[:6] == 'DOUBLE':
                        q += ',%s=%8.6f' % (colname, coldefault)
                    elif coltype[:7] == 'VARCHAR':
                        q += ',%s=\'%s\'' % (colname, coldefault)

            else:

                # Arrays handled here.
                # Get multiple subelements with matching tag.

                values = []
                children = stage.findall(coltag)
                for child in children:
                    values.append(child.text)
                string_id = update_strings(cnx, values)
                q += ',%s=%d' % (colname, string_id)
                    
    # Execute query.

    c.execute(q)

    # Get id of inserted row.

    q = 'SELECT LAST_INSERT_ID()'
    c.execute(q)
    row = c.fetchone()
    stage_id = row[0]
    result = stage_id

    # Insert substage subelements of this project.

    seqnum = 0
    for substage in stage.findall('fcl'):
        seqnum += 1
        import_substage(cnx, substage, stage_id, seqnum)

    # Done

    cnx.commit()
    return result


# Import project(s) from xml string.
# Returns a list of newly inserted project ids.
# Projects with matching names will not be reinserted.

def import_project(cnx, xmlstring):

    result = []
    c = cnx.cursor()

    # Parse the xml string, and extract the root element.

    root = ET.fromstring(xmlstring)

    # Loop over project elements in this xml file.

    for prj in root.getiterator('project'):

        # Extract project name attribute.

        name = ''
        if 'name' in prj.attrib:
            name = prj.attrib['name']

        # See if this project name already exists.
        # Ignore this project if it does.

        id = get_project_id(cnx, name)
        if id > 0:
            break

        # Prepare query to insert this project into database.

        q = 'INSERT INTO projects SET'
        if name != '':
            q += ' name=\'%s\'' % name
        user = dbconfig.getuser()
        if user != '':
            q += ',username=\'%s\'' % user

        # Loop over dictionary elements for table projects.

        for coltup in databaseDict['projects']:
            colname = coltup[0]
            coltag = coltup[1]
            coltype = coltup[2]
            colarray = coltup[3]
            coldefault = coltup[5]
            #print colname, coltag, coltype, colarray

            # Hunt for subelements with matching tag.

            if coltag != '':
                if colarray == 0:

                    # Scalar types handled here.
                    # Get one subelement with matching tag, if any.

                    xmlpath = './%s' % coltag
                    child = prj.find(xmlpath)
                    if child != None:
                        value = child.text
                        if coltype[:3] == 'INT':
                            q += ',%s=%d' % (colname, int(value))
                        elif coltype[:6] == 'DOUBLE':
                            q += ',%s=%8.6f' % (colname, float(value))
                        elif coltype[:7] == 'VARCHAR':
                            q += ',%s=\'%s\'' % (colname, value.replace("'", "\\'"))
                    else:
                        if coltype[:3] == 'INT':
                            q += ',%s=%d' % (colname, coldefault)
                        elif coltype[:6] == 'DOUBLE':
                            q += ',%s=%8.6f' % (colname, coldefault)
                        elif coltype[:7] == 'VARCHAR':
                            q += ',%s=\'%s\'' % (colname, coldefault)

                else:

                    # Arrays handled here.
                    # Get multiple subelements with matching tag.

                    values = []
                    children = prj.findall(coltag)
                    for child in children:
                        values.append(child.text)
                    string_id = update_strings(cnx, values)
                    q += ',%s=%d' % (colname, string_id)
                    
        # Execute query.

        c.execute(q)

        # Get id of inserted row.

        q = 'SELECT LAST_INSERT_ID()'
        c.execute(q)
        row = c.fetchone()
        project_id = row[0]
        result.append(project_id)

        # Insert stage subelements of this project.

        seqnum = 0
        for stage in prj.findall('stage'):
            seqnum += 1
            import_stage(cnx, stage, project_id, seqnum)

    # Done

    cnx.commit()
    return result


# Extract project names from xml string.
# Return list of project names.

def xml_project_names(xmlstring):

    result = []

    # Parse the xml string, and extract the root element.

    root = ET.fromstring(xmlstring)

    # Loop over project elements in this xml file.

    for prj in root.getiterator('project'):

        # Extract project name attribute.

        name = ''
        if 'name' in prj.attrib:
            name = prj.attrib['name']

        if name != '':
            result.append(name)

    # Done

    return result


# Add dataset assicuated with project.
# Duplicates are allowed.

def add_dataset(cnx, project_id, dataset_type, dataset_name):

    result = 0

    # Check access.

    if not dbconfig.restricted_access_allowed() and restricted_access(cnx, 'projects', project_id):
        restricted_error()

    # Query the maximum sequence number for this stage.

    c = cnx.cursor()
    q = 'SELECT MAX(seqnum) FROM datasets WHERE project_id=%d AND type=\'%s\'' % \
        (project_id, dataset_type)
    c.execute(q)
    row = c.fetchone()
    seqnum = row[0]
    new_seqnum = 0
    if seqnum == None:
        new_seqnum = 1
    else:
        new_seqnum = seqnum + 1

    # Construct a query to insert dataset.

    q = 'INSERT INTO datasets SET project_id=%d,type=\'%s\',name=\'%s\',seqnum=%d' % \
        (project_id, dataset_type, dataset_name, new_seqnum)

    # Loop over remaining fields.

    cols = databaseDict['datasets']
    for n in range(5, len(cols)):
        coltup = cols[n]
        colname = coltup[0]
        coltype = coltup[2]
        coldefault = coltup[5]
        if coltype[:3] == 'INT':
            q += ',%s=%d' % (colname, coldefault)
        elif coltype[:7] == 'VARCHAR':
            q += ',%s=\'%s\'' % (colname, coldefault)
        elif coltype[:6] == 'DOUBLE':
            q += ',%s=%8.6f' % (colname, coldefault)

    c.execute(q)

    # Get id of inserted row.

    q = 'SELECT LAST_INSERT_ID()'
    c.execute(q)
    row = c.fetchone()
    result = row[0]

    # Done.

    cnx.commit()
    return result


# Delete dataset.

def delete_dataset(cnx, dataset_id):

    # Check access.

    if not dbconfig.restricted_access_allowed() and restricted_access(cnx, 'datasets', dataset_id):
        restricted_error()

    # Delete dataset.

    c = cnx.cursor()
    q = 'DELETE FROM datasets WHERE id=%d' % dataset_id
    c.execute(q)

    # Done.

    cnx.commit()
    return


# Insert blank substage into database.
# Fields are filled with default values.
# Substage id of newly added substage is returned.

def insert_blank_substage(cnx, stage_id):

    c = cnx.cursor()

    # Query the maximum sequence number for this stage.

    q = 'SELECT MAX(seqnum) FROM substages WHERE stage_id=%d' % stage_id
    c.execute(q)
    row = c.fetchone()
    seqnum = row[0]
    new_seqnum = 0
    if seqnum == None:
        new_seqnum = 1
    else:
        new_seqnum = seqnum + 1

    # Prepare query to insert stage row.

    q = 'INSERT INTO substages SET fclname=\'blank.fcl\', stage_id=%d, seqnum=%d' % (stage_id, new_seqnum)

    # Loop over remaining fields.

    cols = databaseDict['substages']
    for n in range(4, len(cols)):
        coltup = cols[n]
        colname = coltup[0]
        coltype = coltup[2]
        coldefault = coltup[5]
        if coltype[:3] == 'INT':
            q += ',%s=%d' % (colname, coldefault)
        elif coltype[:7] == 'VARCHAR':
            q += ',%s=\'%s\'' % (colname, coldefault)
        elif coltype[:6] == 'DOUBLE':
            q += ',%s=%8.6f' % (colname, coldefault)

    c.execute(q)

    # Get id of inserted row.

    q = 'SELECT LAST_INSERT_ID()'
    c.execute(q)
    row = c.fetchone()
    new_substage_id = row[0]

    # Done.

    cnx.commit()
    return new_substage_id


# Insert blank stage into database.
# Fields are filled with default values.
# Stage id of newly added stage is returned.

def insert_blank_stage(cnx, project_id):

    c = cnx.cursor()

    # Query the maximum sequence number for this stage.

    q = 'SELECT MAX(seqnum) FROM stages WHERE project_id=%d' % project_id
    c.execute(q)
    row = c.fetchone()
    seqnum = row[0]
    new_seqnum = 0
    if seqnum == None:
        new_seqnum = 1
    else:
        new_seqnum = seqnum + 1

    # Prepare query to insert stage row.

    q = 'INSERT INTO stages SET name=\'blank\', project_id=%d, seqnum=%d' % (project_id, new_seqnum)

    # Loop over remaining fields.

    cols = databaseDict['stages']
    for n in range(4, len(cols)):
        coltup = cols[n]
        colname = coltup[0]
        coltype = coltup[2]
        coldefault = coltup[5]
        if coltype[:3] == 'INT':
            q += ',%s=%d' % (colname, coldefault)
        elif coltype[:7] == 'VARCHAR':
            q += ',%s=\'%s\'' % (colname, coldefault)
        elif coltype[:6] == 'DOUBLE':
            q += ',%s=%8.6f' % (colname, coldefault)

    c.execute(q)

    # Get id of inserted row.

    q = 'SELECT LAST_INSERT_ID()'
    c.execute(q)
    row = c.fetchone()
    new_stage_id = row[0]

    # Done.

    cnx.commit()
    return new_stage_id


# Insert blank project into database.
# Fields are filled with default values.
# Project id of newly added project is returned.

def insert_blank_project(cnx):

    c = cnx.cursor()

    # Generate unique project name.

    n = 1
    done = False
    project_name = ''
    while not done:

        if n == 1:
            project_name = 'blank'
        else:
            project_name = 'blank%d' % n

        # See if this candidate name already exists.

        q = 'SELECT COUNT(*) FROM projects WHERE name=\'%s\'' % project_name
        c.execute(q)
        row = c.fetchone()
        count = row[0]
        if count == 0:
            done = True
        else:
            n += 1

    # Prepare query to insert project row.

    q = 'INSERT INTO projects SET name=\'%s\'' % project_name
    user = dbconfig.getuser()
    if user != '':
        q += ',username=\'%s\'' % user

    # Loop over remaining fields.

    cols = databaseDict['projects']
    for n in range(3, len(cols)):
        coltup = cols[n]
        colname = coltup[0]
        coltype = coltup[2]
        coldefault = coltup[5]
        if coltype[:3] == 'INT':
            q += ',%s=%d' % (colname, coldefault)
        elif coltype[:7] == 'VARCHAR':
            q += ',%s=\'%s\'' % (colname, coldefault)
        elif coltype[:6] == 'DOUBLE':
            q += ',%s=%8.6f' % (colname, coldefault)

    c.execute(q)

    # Get id of inserted row.

    q = 'SELECT LAST_INSERT_ID()'
    c.execute(q)
    row = c.fetchone()
    new_project_id = row[0]

    # Done.

    cnx.commit()
    return new_project_id


# Make sure the specified dataset sequence number is not used.
# If it is already used, increment all sequence numbers equal or larger by one.

def free_seqnum_dataset(cnx, project_id, dataset_type, seqnum):

    c = cnx.cursor()

    # See if this sequence number is already used.

    q = 'SELECT COUNT(*) FROM datasets WHERE project_id=%d AND type=\'%s\' AND seqnum=%d' % \
        (project_id, dataset_type, seqnum)
    c.execute(q)
    row = c.fetchone()
    n = row[0]
    if n > 0:

        # Got a match.
        # Query all sequence numbers equal or greater.

        q = 'SELECT id, project_id, type, seqnum FROM datasets WHERE project_id=%d AND type=\'%s\' AND seqnum>=%d' % \
            (project_id, dataset_type, seqnum)
        c.execute(q)
        rows = c.fetchall()
        for row in rows:
            dataset_id = row[0]
            seq = row[3]

            # Increment sequence number.

            q = 'UPDATE datasets SET seqnum=%d WHERE id=%d' % (seq+1, dataset_id)
            c.execute(q)

    # Done.

    return


# Clone dataset row.

def clone_dataset(cnx, dataset_id):

    # Check access.

    if not dbconfig.restricted_access_allowed() and restricted_access(cnx, 'datasets', dataset_id):
        restricted_error()

    # Query full dataset row from database.

    c = cnx.cursor()
    q = 'SELECT * FROM datasets WHERE id=%d' % dataset_id
    c.execute(q)
    rows = c.fetchall()
    if len(rows) == 0:
        raise IOError('Unable to fetch dataset id %d' % dataset_id)
    row = rows[0]
    dataset_name = row[1]
    project_id = row[2]
    seqnum = row[3]
    dataset_type = row[4]

    # Increment sequence number, and make sure the new sequence number of free.

    seqnum += 1
    free_seqnum_dataset(cnx, project_id, dataset_type, seqnum)

    # Construct query to insert a new row into datasets table that is
    # a copy of the row that we just read.

    cols = databaseDict['datasets']
    q = 'INSERT INTO datasets SET name=\'%s\',project_id=%d,seqnum=%d,type=\'%s\'' % \
        (dataset_name, project_id, seqnum, dataset_type)
    for n in range(5, len(cols)):
        coltup = cols[n]
        colname = coltup[0]
        coltype = coltup[2]
        colarray = coltup[3]
        if colarray:
            q += ',%s=%d' % (colname, row[n])
        elif coltype[:3] == 'INT':
            q += ',%s=%d' % (colname, row[n])
        elif coltype[:7] == 'VARCHAR':
            q += ',%s=\'%s\'' % (colname, row[n])
        elif coltype[:6] == 'DOUBLE':
            q += ',%s=%8.6f' % (colname, row[n])
    c.execute(q)

    # Get id of inserted row.

    q = 'SELECT LAST_INSERT_ID()'
    c.execute(q)
    row = c.fetchone()
    new_dataset_id = row[0]

    # Done.

    cnx.commit()
    return new_dataset_id


# Check whether the specified table and row is restricted access.
# Restricted access depends on the status of the parent project.
# Any status other that blank ('') or 'Requested' means restricted access.

def restricted_access(cnx, table, id):

    c = cnx.cursor()

    # Default result is that access is restricted.

    result = True

    # Table substages, check parent stage.

    if table == 'substages':
        q = 'SELECT stage_id FROM substages WHERE id=%d' % id
        c.execute(q)
        rows = c.fetchall()
        if len(rows) > 0:
            stage_id = rows[0][0]
            result = restricted_access(cnx, 'stages', stage_id)

    # Tables stages and datasets, check parent project.

    elif table == 'stages' or table == 'datasets':
        q = 'SELECT project_id FROM %s WHERE id=%d' % (table, id)
        c.execute(q)
        rows = c.fetchall()
        if len(rows) > 0:
            project_id = rows[0][0]
            result = restricted_access(cnx, 'projects', project_id)

    # Projects table, check status.
    
    elif table == 'projects':
        q = 'SELECT status FROM projects WHERE id=%d' % id
        c.execute(q)
        rows = c.fetchall()
        if len(rows) > 0:
            status = rows[0][0]
            if status == '' or status == 'Requested':
                result = False

    # Done.

    return result


# Function to generate restricted content error page.

def restricted_error():
    print 'Content-type: text/html'
    print 'Status: 403 Forbidden'
    print
    print '<html>'
    print '<title>403 Forbidden</title>'
    print '<body>'
    print '<h1>403 Forbidden</h1>'
    print 'You are not authorized to make this update.'
    print '</body>'
    print '</html>'
    sys.exit(0)
