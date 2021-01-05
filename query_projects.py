#! /usr/bin/python
#==============================================================================
#
# Name: query_projects.py
#
# Purpose: CGI script to query projects from production database.
#          Returns an html form containing editable query parameters
#          and links to other pages.
#
# CGI arguments:
#
# <qdict> - Standard query_projects.py arguments.
#
# Created: 15-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os, copy
import dbconfig, dbargs, dbutil
from dbconfig import pulldowns
from dbconfig import colors


# Return list of projects.

def list_projects(cnx, pattern, group, status, gid, experiment, file_type, campaign, sort):

    result = []

    # Query projects from database.

    c = cnx.cursor()
    q = 'SELECT projects.id, name, file_type, experiment, campaign, physics_group, status FROM projects'
    if gid != 0:
        q += ',group_project'
    con = 'WHERE'
    if pattern != '':
        q += ' %s name LIKE \'%%%s%%\'' % (con, pattern)
        con = 'AND'
    if group != '':
        q += ' %s physics_group=\'%s\'' % (con, group)
        con = 'AND'
    if status != '':
        q += ' %s status=\'%s\'' % (con, status)
        con = 'AND'
    if gid != 0:
        q += ' %s group_id=%d and project_id=projects.id' % (con, gid)
    if file_type != '':
        q += ' %s file_type=\'%s\'' % (con, file_type)
        con = 'AND'
    if experiment != '':
        q += ' %s experiment=\'%s\'' % (con, experiment)
        con = 'AND'
    if campaign != '':
        q += ' %s campaign=\'%s\'' % (con, campaign)
        con = 'AND'
    if sort == '' or sort == 'id_u':
        q += ' ORDER BY id'
    elif sort == 'id_d':
        q += ' ORDER BY id DESC'
    elif sort == 'name_u':
        q += ' ORDER BY name'
    elif sort == 'name_d':
        q += ' ORDER BY name DESC'
    elif sort == 'file_type_u':
        q += ' ORDER BY file_type'
    elif sort == 'file_type_d':
        q += ' ORDER BY file_type DESC'
    elif sort == 'experiment_u':
        q += ' ORDER BY experiment'
    elif sort == 'experiment_d':
        q += ' ORDER BY experiment DESC'
    elif sort == 'campaign_u':
        q += ' ORDER BY campaign'
    elif sort == 'campaign_d':
        q += ' ORDER BY campaign DESC'
    elif sort == 'group_u':
        q += ' ORDER BY physics_group'
    elif sort == 'group_d':
        q += ' ORDER BY physics_group DESC'
    elif sort == 'status_u':
        q += ' ORDER BY status'
    elif sort == 'status_d':
        q += ' ORDER BY status DESC'
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        id = row[0]
        name = row[1]
        file_type = row[2]
        experiment = row[3]
        campaign = row[4]
        physics_group = row[5]
        status = row[6]
        result.append((id, name, file_type, experiment, campaign, physics_group, status))

    # Done.

    return result


# Generate search panel.

def search_panel(results_per_page, pattern, group, status, gid, experiment, file_type, campaign, devel):

    # Add form for pattern match and results per page.

    print '<form action="/cgi-bin/db/query_projects.py" method="post">'

    # Add hidden input for db instance.

    print '<input type="hidden" id="dev" name="dev" value=%d>' % devel

    # Add pattern wildcard input.

    print '<label for="pattern">Match: </label>'
    print '<input type="text" id="pattern" name="pattern" size=30 value="%s">' % pattern

    # Add group id input.

    print '<label for="gid">Group ID: </label>'
    print '<input type="text" id="gid" name="gid" size=6 value=%d>' % gid

    # Add experiment drop down.

    print '<label for="experiment">Experiment: </label>'
    print '<select id="experiment" name="experiment">'
    for value in pulldowns['experiment']:
        sel = ''
        if value == experiment:
            sel = 'selected'
        print '<option value="%s" %s>%s</option>' % (value, sel, value)
    print '</select>'

    # Add file type drop down.

    print '<label for="file_type">File Type: </label>'
    print '<select id="file_type" name="file_type">'
    for value in pulldowns['file_type']:
        sel = ''
        if value == file_type:
            sel = 'selected'
        print '<option value="%s" %s>%s</option>' % (value, sel, value)
    print '</select>'

    # Add campaign drop down.

    print '<label for="campaign">Campaign: </label>'
    print '<select id="campaign" name="campaign">'
    for value in pulldowns['campaign']:
        sel = ''
        if value == campaign:
            sel = 'selected'
        print '<option value="%s" %s>%s</option>' % (value, sel, value)
    print '</select>'

    # Add physics group drop down.

    print '<label for="group">Physics Group: </label>'
    print '<select id="group" name="group">'
    for value in pulldowns['physics_group']:
        sel = ''
        if value == group:
            sel = 'selected'
        print '<option value="%s" %s>%s</option>' % (value, sel, value)
    print '</select>'

    # Add status drop down.

    print '<label for="status">Status: </label>'
    print '<select id="status" name="status">'
    for value in pulldowns['status']:
        sel = ''
        if value == status:
            sel = 'selected'
        print '<option value="%s" %s>%s</option>' % (value, sel, value)
    print '</select>'

    # Add results per page input.

    print '<label for="rpp">Projects per page: </label>'
    print '<input type="text" id="rpp" name="results_per_page" size=6 value=%d>' % \
        results_per_page

    # Second line, search button.

    print '<br>'
    print '<input type="submit" value="Search">'
    print '</form>'

    # Done.

    return


# Generate page links.

def page_links(qdict, max_page):

    current_page = qdict['page']

    # Base url.

    url = '%s/query_projects.py' % dbconfig.base_url

    # Calculate which pages to display.
    # Display some number of links centered around the current page.

    offset = 4  # The maximum number of links to display.
    min_link = current_page - offset
    max_link = current_page + offset
    if min_link < 1:
        min_link = 1
        max_link = min(2*offset + 1, max_page)
    if max_link > max_page:
        min_link = max(max_page - 2*offset, 1)
        max_link = max_page

    # Add page links.

    print '<table>'
    print '<tr>'
    print '<td>Go to page:&nbsp;</td>'

    # Add button for first page.

    disabled = ''
    if current_page == 1:
        disabled = 'disabled'
    print '<td>'
    new_qdict = copy.deepcopy(qdict)
    new_qdict['page'] = 1
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        dbargs.convert_args(new_qdict)
    print '<input type="submit" value="&#x25c4;&#x25c4;" %s>' % disabled
    print '</form>'
    print '</td>'

    # Add button for previous page.

    prev_page = max(current_page-1, 1)
    print '<td>'
    new_qdict = copy.deepcopy(qdict)
    new_qdict['page'] = prev_page
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        dbargs.convert_args(new_qdict)
    print '<input type="submit" value="&#x25c4;" %s>' % disabled
    print '</form>'
    print '</td>'

    # Links to specific pages.

    for page in range(min_link, max_link+1):
        if page != current_page:
            new_qdict = copy.deepcopy(qdict)
            new_qdict['page'] = page
            print '<td align="center" style="width:25px;"><a href="%s?%s">%d</a></td>' % \
                (url, dbargs.convert_args(new_qdict), page)
        else:
            print '<th align="center" style="width:25px;">%d</th>' % page

    # Link to next page.

    disabled = ''
    if current_page == max_page:
        disabled = 'disabled'
    next_page = min(current_page+1, max_page)
    print '<td>'
    new_qdict = copy.deepcopy(qdict)
    new_qdict['page'] = next_page
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        dbargs.convert_args(new_qdict)
    print '<input type="submit" value="&#x25ba;" %s>' % disabled
    print '</form>'
    print '</td>'

    # Link to last page.

    print '<td>'
    new_qdict = copy.deepcopy(qdict)
    new_qdict['page'] = max_page
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        dbargs.convert_args(new_qdict)
    print '<input type="submit" value="&#x25ba;&#x25ba;" %s >' % disabled
    print '</form>'
    print '</td>'

    # Finish table.

    print '</tr>'
    print '</table>'

    # Done.

    return


# Main procedure.

def main(qdict):

    # Extract arguments.

    results_per_page = qdict['results_per_page']
    current_page = qdict['page']
    pattern = qdict['pattern']
    group = qdict['group']
    status = qdict['status']
    devel = qdict['dev']
    gid = qdict['gid']
    file_type = qdict['file_type']
    campaign = qdict['campaign']
    sort = qdict['sort']
    experiment = qdict['experiment']

    # Open database connection and query projects.

    cnx = dbconfig.connect(readonly = True, devel = qdict['dev'])

    # Get list of projects.

    prjs = list_projects(cnx, pattern, group, status, gid, experiment, file_type, campaign, sort)
    max_page = (len(prjs) + results_per_page - 1) / results_per_page

    # Generate html document header.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<title>Projects</title>'
    print '</head>'
    print '<body>'

    # Add styles.

    print '<style>'
    print '.small-btn {'
    print '  padding:0 5px;'
    print '  text-decoration:none;'
    print '  border:none;'
    print '  background-color:white;'
    print '}'
    print '</style>'

    # Add link to project group list.

    print '<a href=%s/query_groups.py?%s>Group list</a><br>' % \
        (dbconfig.base_url, dbargs.convert_args(qdict))

    # Generate main part of html document.

    print '<h1>Projects</h1>'

    # Add button to create new project.

    print '<form action="/cgi-bin/db/add_project.py?%s" method="post" target="_self">' % \
        dbargs.convert_args(qdict)
    print '<label for="submit">Generate a new empty project: </label>'
    print '<input type="submit" id="submit" value="New Project">'
    print '</form>'
    print '<p>'

    # Add button to import a project from local xml file.

    print '<form action="/cgi-bin/db/import_project.py?%s" method="post" target="_self">' % \
        dbargs.convert_args(qdict)
    print '<label for="submit">Import project from local XML file: </label>'
    print '<input type="submit" id="submit" value="Import Project">'
    print '</form>'
    print '<p>'

    # Generate search panel form.

    search_panel(results_per_page, pattern, group, status, gid, experiment, file_type, campaign, devel)

    # Display number of results.

    print '<p>%d projects found</p>' % len(prjs)

    # Generate upper navigation panel.

    page_links(qdict, max_page)

    # Project table.

    print '<table border=1 style="border-collapse:collapse">'
    print '<tr>'

    # Project ID column.

    print '<th nowrap>'
    print '&nbsp;Project ID&nbsp;'

    # Add sort buttons.

    print '<div style="display:inline-block">'
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        (dbargs.convert_args(qdict, 'sort', 'id_u'))
    if sort == 'id_u':
        print '<input class="small-btn" type="submit" value="&#x25b2;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25b3;">'
    print '</form>'
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        (dbargs.convert_args(qdict, 'sort', 'id_d'))
    if sort == 'id_d':
        print '<input class="small-btn" type="submit" value="&#x25bc;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25bd;">'
    print '</form>'
    print '</div>'
    print '</th>'

    # Project name column.

    print '<th nowrap>'
    print '&nbsp;Project Name (Datasets)&nbsp;'

    # Add sort buttons.

    print '<div style="display:inline-block">'
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        (dbargs.convert_args(qdict, 'sort', 'name_u'))
    if sort == 'name_u':
        print '<input class="small-btn" type="submit" value="&#x25b2;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25b3;">'
    print '</form>'
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        (dbargs.convert_args(qdict, 'sort', 'name_d'))
    if sort == 'name_d':
        print '<input class="small-btn" type="submit" value="&#x25bc;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25bd;">'
    print '</form>'
    print '</div>'
    print '</th>'

    # Experiment column.

    print '<th nowrap>'
    print '&nbsp;Experiment&nbsp;'

    # Add sort buttons.

    print '<div style="display:inline-block">'
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        (dbargs.convert_args(qdict, 'sort', 'experiment_u'))
    if sort == 'experiment_u':
        print '<input class="small-btn" type="submit" value="&#x25b2;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25b3;">'
    print '</form>'
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        (dbargs.convert_args(qdict, 'sort', 'experiment_d'))
    if sort == 'experiment_d':
        print '<input class="small-btn" type="submit" value="&#x25bc;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25bd;">'
    print '</form>'
    print '</div>'
    print '</th>'

    # File type column.

    print '<th nowrap>'
    print '&nbsp;File Type&nbsp;'

    # Add sort buttons.

    print '<div style="display:inline-block">'
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        (dbargs.convert_args(qdict, 'sort', 'file_type_u'))
    if sort == 'file_type_u':
        print '<input class="small-btn" type="submit" value="&#x25b2;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25b3;">'
    print '</form>'
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        (dbargs.convert_args(qdict, 'sort', 'file_type_d'))
    if sort == 'file_type_d':
        print '<input class="small-btn" type="submit" value="&#x25bc;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25bd;">'
    print '</form>'
    print '</div>'
    print '</th>'

    # Campaign column.

    print '<th nowrap>'
    print '&nbsp;Campaign&nbsp;'

    # Add sort buttons.

    print '<div style="display:inline-block">'
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        (dbargs.convert_args(qdict, 'sort', 'campaign_u'))
    if sort == 'campaign_u':
        print '<input class="small-btn" type="submit" value="&#x25b2;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25b3;">'
    print '</form>'
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        (dbargs.convert_args(qdict, 'sort', 'campaign_d'))
    if sort == 'campaign_d':
        print '<input class="small-btn" type="submit" value="&#x25bc;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25bd;">'
    print '</form>'
    print '</div>'
    print '</th>'

    # Physics group column.

    print '<th nowrap>'
    print '&nbsp;Physics&nbsp;'

    # Add sort buttons.

    print '<div style="display:inline-block">'
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        (dbargs.convert_args(qdict, 'sort', 'group_u'))
    if sort == 'group_u':
        print '<input class="small-btn" type="submit" value="&#x25b2;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25b3;">'
    print '</form>'
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        (dbargs.convert_args(qdict, 'sort', 'group_d'))
    if sort == 'group_d':
        print '<input class="small-btn" type="submit" value="&#x25bc;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25bd;">'
    print '</form>'
    print '</div>'
    print '</th>'

    # Status column.

    print '<th nowrap>'
    print '&nbsp;Status&nbsp;'

    # Add sort buttons.

    print '<div style="display:inline-block">'
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        (dbargs.convert_args(qdict, 'sort', 'status_u'))
    if sort == 'status_u':
        print '<input class="small-btn" type="submit" value="&#x25b2;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25b3;">'
    print '</form>'
    print '<form action="/cgi-bin/db/query_projects.py?%s" method="post">' % \
        (dbargs.convert_args(qdict, 'sort', 'status_d'))
    if sort == 'status_d':
        print '<input class="small-btn" type="submit" value="&#x25bc;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25bd;">'
    print '</form>'
    print '</div>'
    print '</th>'
    print '</tr>'

    # Loop over projects.

    for i in range((current_page-1) * results_per_page, 
                   min(current_page * results_per_page, len(prjs))):
        prj = prjs[i]
        print '<tr>'
        id = prj[0]
        name = prj[1]
        file_type = prj[2]
        experiment = prj[3]
        campaign = prj[4]
        physics_group = prj[5]
        status = prj[6]
        color_style = ''
        if status in colors:
            color_style = 'style="background-color: %s"' % colors[status]
        print '<td align="center" %s>%d</td>' % (color_style, id)

        # Construct disabled option for restricted controls.

        disabled = ''
        if not dbconfig.restricted_access_allowed() and dbutil.restricted_access(cnx, 'projects', id):
            disabled = 'disabled'
        

        # Add link to datasets page with project name.

        print '<td %s>&nbsp;<a target=_self href=%s/edit_datasets.py?id=%d&%s>%s</a>&nbsp;</td>' % \
            (color_style, dbconfig.base_url, id, dbargs.convert_args(qdict), name)

        # Add middle columns

        print '<td align="center" %s>&nbsp;%s&nbsp;</td>' % (color_style, experiment)
        print '<td align="center" %s>&nbsp;%s&nbsp;</td>' % (color_style, file_type)
        print '<td align="center" %s>&nbsp;%s&nbsp;</td>' % (color_style, campaign)
        print '<td align="center" %s>&nbsp;%s&nbsp;</td>' % (color_style, physics_group)
        print '<td align="center" %s>&nbsp;%s&nbsp;</td>' % (color_style, status)

        # Add XML button/column

        print '<td>'
        print '<form target="_self" action="/cgi-bin/db/export_project.py?id=%d&%s" method="post">' % \
            (id, dbargs.convert_args(qdict))
        print '<div title="Generate XML">'
        print '<input type="submit" value="XML">'
        print '</div>'
        print '</form>'
        print '</td>'        

        # Add POMS button/column

        print '<td>'
        print '<form target="_self" action="/cgi-bin/db/export_poms.py?id=%d&%s" method="post">' % \
            (id, dbargs.convert_args(qdict))
        print '<div title="Generate POMS .ini file">'
        print '<input type="submit" value="POMS">'
        print '</form>'
        print '</td>'        

        # Add Edit button/column

        print '<td>'
        print '<form target="_self" action="/cgi-bin/db/edit_project.py?id=%d&%s" method="post">' % \
            (id, dbargs.convert_args(qdict))
        print '<div title="Edit project">'
        print '<input type="submit" value="&#x270e;">'
        print '</div>'
        print '</form>'
        print '</td>'        

        # Add Clone button/column

        print '<td>'
        print '<form target="_self" action="/cgi-bin/db/clone_project.py?id=%d&%s" method="post">' % \
            (id, dbargs.convert_args(qdict))
        print '<div title="Clone project">'
        print '<input type="submit" value="&#x2398;">'
        print '</div>'
        print '</form>'
        print '</td>'        

        # Add Delete button/column

        print '<td>'
        print '<form action="/cgi-bin/db/delete_project.py?id=%d&%s" method="post">' % \
            (id, dbargs.convert_args(qdict))
        print '<div title="Delete project">'
        print '<input type="submit" value="&#x1f5d1;" %s>' % disabled
        print '</div>'
        print '</form>'
        print '</td>'        
        print '</tr>'
    print '</table>'

    # Add lower navigation panel.

    page_links(qdict, max_page)

    # Generate html document trailer.
    
    print '</body>'
    print '</html>'


# End of definitions.  Executable code starts here.

if __name__ == "__main__":

    # Parse arguments.

    argdict = dbargs.get()
    qdict = dbargs.extract_qdict(argdict)

    # Call main procedure.

    main(qdict)
