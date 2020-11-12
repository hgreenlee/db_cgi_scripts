#==============================================================================
#
# Name: dbutil.py
#
# Purpose: Python database utility module containing various useful functions.
#
# Created: 15-Oct-2020  H. Greenlee
#
#==============================================================================

import sys
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

    # Query projects from database.

    c = cnx.cursor()
    q = 'SELECT name FROM projects'
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        project_name = row[0]
        print project_name

    # Done.

    return


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


# Delete substage.

def delete_substage(cnx, substage_id):

    # Delete substage.

    c = cnx.cursor()
    q = 'DELETE FROM substages WHERE id=%d' % substage_id
    c.execute(q)

    # Done.

    cnx.commit()
    return


# Delete stage.

def delete_stage(cnx, stage_id):

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
    for n in range(2, len(cols)):
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


# Insert substage into database.
# Note that each substage is synonomous with one fcl file.
# Information relevant to each substage is stored in a project.py stage object.
# The final argument is the substage (aka fcl file) index.

def insert_substage(cnx, stage, stage_id, i):

    c = cnx.cursor()
    print 'Inserting substage %d for stage %s.' % (i, stage.name)

    # Count the number of existing substages belonging to this stage id.
    # Use this information to set the sequence number.

    q = 'SELECT COUNT(*) FROM substages WHERE stage_id=%d' % stage_id
    c.execute(q)
    row = c.fetchone()
    seqnum = row[0] + 1

    # Prepare query to insert substage row.

    q = '''INSERT INTO substages SET
            fclname=\'%s\',
            stage_id=%d,
            seqnum=%d,
            init_sources=%d,
            end_scripts=%d,
            projectname=\'%s\',
            stagename=\'%s\',
            version=\'%s\',
            output=\'%s\',
            exe=\'%s\'
            ''' % (stage.fclname[i],
                   stage_id,
                   seqnum,
                   update_strings(cnx, stage.mid_source[i]) if stage.mid_source.has_key(i) else 0,
                   update_strings(cnx, stage.mid_script[i]) if stage.mid_script.has_key(i) else 0,
                   stage.project_name[i] if len(stage.project_name) > i else '',
                   stage.stage_name[i] if len(stage.stage_name) > i else '',
                   stage.project_version[i] if len(stage.project_version) > i else '',
                   stage.output[i] if len(stage.output) > i else '',
                   stage.exe[i] if len(stage.exe) > i else '')
    c.execute(q)

    # Done.

    return


# Insert stage into database.
# The stage argument is a project.py stage object.

def insert_stage(cnx, stage, project_id):

    c = cnx.cursor()
    print 'Inserting stage %s.' % stage.name

    # Count the number of existing stages belonging to this project id.
    # Use this information to set the sequence number.

    q = 'SELECT COUNT(*) FROM stages WHERE project_id=%d' % project_id
    c.execute(q)
    row = c.fetchone()
    seqnum = row[0] + 1

    # Reverse engineer inputdef and recurdef.

    inputdef = stage.inputdef
    recurdef = ''
    if stage.basedef != '':
        inputdef = stage.basedef
        recurdef = stage.inputdef

    # Prepare query to insert stage row.

    q = '''INSERT INTO stages SET
            name=\'%s\',
            project_id=%d,
            seqnum=%d,
            batchname=\'%s\',
            poms_stage=\'%s\',
            outdir=\'%s\',
            logdir=\'%s\',
            workdir=\'%s\',
            bookdir=\'%s\',
            dirlevels=%d,
            dirsize=%d,
            inputdef=\'%s\',
            recurdef=\'%s\',
            ana=%d,
            recur=%d,
            recurtype=\'%s\',
            recurlimit=%d,
            filelistdef=%d,
            prestart=%d,
            activebase=\'%s\',
            dropboxwait=%g,
            prestagefraction=%g,
            maxfluxfilemb=%d,
            num_jobs=%d,
            num_events=%d,
            max_files_per_job=%d,
            target_size=%d,
            defname=\'%s\',
            ana_defname=\'%s\',
            data_tier=\'%s\',
            ana_data_tier=\'%s\',
            submit_script=\'%s\',
            merge=\'%s\',
            anamerge=\'%s\',
            resource=\'%s\',
            lines_=\'%s\',
            site=\'%s\',
            blacklist=\'%s\',
            cpu=%d,
            disk=\'%s\',
            memory=%d,
            TFileName=\'%s\',
            jobsub=\'%s\',
            jobsub_start=\'%s\',
            jobsub_timeout=%d,
            schema_=\'%s\',
            validate_on_worker=%d,
            copy_to_fts=%d,
            script=\'%s\',
            start_script=\'%s\',
            stop_script=\'%s\',
            data_streams=%d,
            ana_data_streams=%d,
            init_scripts=%d,
            init_sources=%d,
            end_scripts=%d
            ''' % (stage.name,
                   project_id,
                   seqnum,
                   stage.batchname,
                   stage.poms_stage,
                   stage.outdir,
                   stage.logdir,
                   stage.workdir,
                   stage.bookdir,
                   stage.dirlevels,
                   stage.dirsize,
                   inputdef,
                   recurdef,
                   stage.ana,
                   stage.recur,
                   stage.recurtype,
                   stage.recurlimit,
                   stage.filelistdef,
                   stage.prestart,
                   stage.activebase,
                   stage.dropboxwait,
                   stage.prestagefraction,
                   stage.maxfluxfilemb,
                   stage.num_jobs,
                   stage.num_events,
                   stage.max_files_per_job,
                   stage.target_size,
                   stage.defname,
                   stage.ana_defname,
                   stage.data_tier,
                   stage.ana_data_tier,
                   ' '.join(stage.submit_script),
                   stage.merge,
                   stage.anamerge,
                   stage.resource,
                   stage.lines,
                   stage.site,
                   stage.blacklist,
                   stage.cpu,
                   stage.disk,
                   stage.memory,
                   stage.TFileName,
                   stage.jobsub.replace("'", "\\'"),
                   stage.jobsub_start.replace("'", "\\'"),
                   stage.jobsub_timeout,
                   stage.schema,
                   stage.validate_on_worker,
                   stage.copy_to_fts,
                   stage.script,
                   stage.start_script,
                   stage.stop_script,
                   update_strings(cnx, stage.data_stream),
                   update_strings(cnx, stage.ana_data_stream),
                   update_strings(cnx, stage.init_script),
                   update_strings(cnx, stage.init_source),
                   update_strings(cnx, stage.end_script))
    c.execute(q)

    # Get id of inserted row.

    q = 'SELECT LAST_INSERT_ID()'
    c.execute(q)
    row = c.fetchone()
    stage_id = row[0]

    # Insert substages.

    n = len(stage.fclname)
    for i in range(n):
        insert_substage(cnx, stage, stage_id, i)

    # Done.

    return


# Insert project into database.
# The project argument is a project.py project object.

def insert_project(cnx, prj):

    c = cnx.cursor()

    # See if this project already exists.

    q = 'SELECT COUNT(*) FROM projects WHERE name=\'%s\'' % prj.name
    c.execute(q)
    row = c.fetchone()
    n = row[0]
    if n > 0:
        print 'Project %s already exists.' % prj.name
        return

    # Make sure database is writable.

    if is_readonly(cnx):
        print 'Project %s does not exist and database connection is read only.' % prj.name
        sys.exit(1)

    # Prepare query to insert project row.

    print 'Inserting project %s.' % prj.name
    q = '''INSERT INTO projects SET
           name=\'%s\',
           num_events=%d,
           num_jobs=%d,
           max_files_per_job=%d,
           os=\'%s\',
           resource=\'%s\',
           role=\'%s\',
           lines_=\'%s\',
           server=\'%s\',
           site=\'%s\',
           blacklist=\'%s\',
           cpu=%d,
           disk=\'%s\',
           memory=%d,
           merge=\'%s\',
           anamerge=\'%s\',
           release_tag=\'%s\',
           release_qual=\'%s\',
           version=\'%s\',
           local_release_tar=\'%s\',
           poms_login_setup=\'%s\',
           poms_job_type=\'%s\',
           poms_campaign=\'%s\',
           file_type=\'%s\',
           run_type=\'%s\',
           run_number=%d,
           script=\'%s\',
           validate_on_worker=%d,
           copy_to_fts=%d,
           start_script=\'%s\',
           stop_script=\'%s\',
           ups=%d,
           fcldir=%d
           ''' % (prj.name,
                  prj.num_events,
                  prj.num_jobs,
                  prj.max_files_per_job,
                  prj.os,
                  prj.resource,
                  prj.role,
                  prj.lines,
                  prj.server,
                  prj.site,
                  prj.blacklist,
                  prj.cpu,
                  prj.disk,
                  prj.memory,
                  prj.merge,
                  prj.anamerge,
                  prj.release_tag,
                  prj.release_qual,
                  prj.version,
                  prj.local_release_tar,
                  prj.poms_login_setup,
                  prj.poms_job_type,
                  prj.poms_campaign,
                  prj.file_type,
                  prj.run_type,
                  prj.run_number,
                  prj.script,
                  prj.validate_on_worker,
                  prj.copy_to_fts,
                  prj.start_script,
                  prj.stop_script,
                  update_strings(cnx, prj.ups),
                  update_strings(cnx, prj.fclpath))
    c.execute(q)

    # Get id of inserted row.

    q = 'SELECT LAST_INSERT_ID()'
    c.execute(q)
    row = c.fetchone()
    project_id = row[0]

    # Loop over stages.

    for stage in prj.stages:
        insert_stage(cnx, stage, project_id)

    # Done.

    cnx.commit()
    return


# Make sure the specified substage sequence number is not used.
# If it is already used, increment all sequence numbers equal or larger by one.

def free_seqnum_substage(cnx, stage_id, seqnum):

    c = cnx.cursor()

    # See if this sequence number is already used.

    q = 'SELECT COUNT(*) FROM substages WHERE stage_id=%d and seqnum=%d' % (stage_id, seqnum)
    c.execute(q)
    row = c.fetchone()
    n = row[0]
    if n > 0:

        # Got a match.
        # Query all sequence numbers equal or greater.

        q = 'SELECT id, stage_id, seqnum FROM substages WHERE stage_id=%d and seqnum>=%d' % \
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

    q = 'SELECT COUNT(*) FROM stages WHERE project_id=%d and seqnum=%d' % (project_id, seqnum)
    c.execute(q)
    row = c.fetchone()
    n = row[0]
    if n > 0:

        # Got a match.
        # Query all sequence numbers equal or greater.

        q = 'SELECT id, project_id, seqnum FROM stages WHERE project_id=%d and seqnum>=%d' % \
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

    q = '''INSERT INTO substages SET
            fclname=\'%s\',
            stage_id=%d,
            seqnum=%d,
            init_sources=%d,
            end_scripts=%d,
            projectname=\'%s\',
            stagename=\'%s\',
            version=\'%s\',
            output=\'%s\',
            exe=\'%s\'
            ''' % ('blank.fcl',
                   stage_id,
                   new_seqnum,
                   0,
                   0,
                   '',
                   '',
                   '',
                   '',
                   '')
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

    q = '''INSERT INTO stages SET
            name=\'%s\',
            project_id=%d,
            seqnum=%d,
            batchname=\'%s\',
            poms_stage=\'%s\',
            outdir=\'%s\',
            logdir=\'%s\',
            workdir=\'%s\',
            bookdir=\'%s\',
            dirlevels=%d,
            dirsize=%d,
            inputdef=\'%s\',
            recurdef=\'%s\',
            ana=%d,
            recur=%d,
            recurtype=\'%s\',
            recurlimit=%d,
            filelistdef=%d,
            prestart=%d,
            activebase=\'%s\',
            dropboxwait=%g,
            prestagefraction=%g,
            maxfluxfilemb=%d,
            num_jobs=%d,
            num_events=%d,
            max_files_per_job=%d,
            target_size=%d,
            defname=\'%s\',
            ana_defname=\'%s\',
            data_tier=\'%s\',
            ana_data_tier=\'%s\',
            submit_script=\'%s\',
            merge=\'%s\',
            anamerge=\'%s\',
            resource=\'%s\',
            lines_=\'%s\',
            site=\'%s\',
            blacklist=\'%s\',
            cpu=%d,
            disk=\'%s\',
            memory=%d,
            TFileName=\'%s\',
            jobsub=\'%s\',
            jobsub_start=\'%s\',
            jobsub_timeout=%d,
            schema_=\'%s\',
            validate_on_worker=%d,
            copy_to_fts=%d,
            script=\'%s\',
            start_script=\'%s\',
            stop_script=\'%s\',
            data_streams=%d,
            ana_data_streams=%d,
            init_scripts=%d,
            init_sources=%d,
            end_scripts=%d
            ''' % ('blank',
                   project_id,
                   new_seqnum,
                   '',
                   '',
                   '',
                   '',
                   '',
                   '',
                   1,
                   100,
                   '',
                   '',
                   0,
                   0,
                   'child',
                   0,
                   1,
                   1,
                   '',
                   3,
                   1,
                   0,
                   100,
                   1000000000,
                   1,
                   0,
                   '',
                   '',
                   'reconstructed',
                   'root-tuple',
                   '',
                   '',
                   '',
                   '',
                   '',
                   '',
                   '',
                   0,
                   '',
                   2000,
                   '',
                   '--append_condor_requirements=\\\'(TARGET.HAS_CVMFS_uboone_opensciencegrid_org==true)&amp;&amp;(TARGET.HAS_CVMFS_uboone_osgstorage_org==true)\\\' --subgroup=prod --expected-lifetime=long',
                   '--subgroup=prod --site=FermiGrid --expected-lifetime=long',
                   0,
                   'root',
                   1,
                   0,
                   'condor_lar.sh',
                   'condor_start_project.sh',
                   'condor_stop_project.sh',
                   0,
                   0,
                   0,
                   0,
                   0)
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

    q = '''INSERT INTO projects SET
           name=\'%s\',
           num_events=%d,
           num_jobs=%d,
           max_files_per_job=%d,
           os=\'%s\',
           resource=\'%s\',
           role=\'%s\',
           lines_=\'%s\',
           server=\'%s\',
           site=\'%s\',
           blacklist=\'%s\',
           cpu=%d,
           disk=\'%s\',
           memory=%d,
           merge=\'%s\',
           anamerge=\'%s\',
           release_tag=\'%s\',
           release_qual=\'%s\',
           version=\'%s\',
           local_release_tar=\'%s\',
           poms_login_setup=\'%s\',
           poms_job_type=\'%s\',
           poms_campaign=\'%s\',
           file_type=\'%s\',
           run_type=\'%s\',
           run_number=%d,
           script=\'%s\',
           validate_on_worker=%d,
           copy_to_fts=%d,
           start_script=\'%s\',
           stop_script=\'%s\',
           ups=%d,
           fcldir=%d
           ''' % (project_name,
                  1000000000,
                  100,
                  1,
                  'SL7',
                  'DEDICATED,OPPORTUNISTIC,OFFSITE',
                  'Production',
                  '',
                  '',
                  '',
                  '',
                  0,
                  '',
                  0,
                  '',
                  '',
                  'v08_00_00_xx',
                  'e17:prof',
                  'prof_v08_00_00_xx',
                  '',
                  '',
                  '',
                  '',
                  'data/mc/overlay',
                  'physics',
                  0,
                  'condor_lar.sh',
                  1,
                  0,
                  'condor_start_project.sh',
                  'condor_stop_project.sh',
                  0,
                  0)
    c.execute(q)

    # Get id of inserted row.

    q = 'SELECT LAST_INSERT_ID()'
    c.execute(q)
    row = c.fetchone()
    new_project_id = row[0]

    # Done.

    cnx.commit()
    return new_project_id


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
                        row = c.fetchone()
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

    for prj in root.iter('project'):

        # Extract project name attribute.

        name = ''
        if 'name' in prj.attrib:
            name = prj.attrib['name']

        # See if this project name alread exists.
        # Ignore this project if it does.

        q = 'SELECT COUNT(*) FROM projects WHERE name=\'%s\'' % name
        c.execute(q)
        row = c.fetchone()
        n = int(row[0])
        if n > 0:
            break

        # Prepare query to insert this project into database.

        q = 'INSERT INTO projects SET'
        if name != '':
            q += ' name=\'%s\'' % name

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
