#! /usr/bin/python
#==============================================================================
#
# Name: query_groups.py
#
# Purpose: CGI script to query project groups from production database.
#          Returns an html form containing editable query parameters
#          and links to other pages.
#
# CGI arguments:
#
# <qdict> - Standard query_groups.py arguments.
#
# Created: 3-Dec-2020  H. Greenlee
#
#==============================================================================

import sys, os, copy
import dbconfig, dbargs, dbutil
from dbconfig import pulldowns
from dbconfig import colors


# Return list of groups.

def list_groups(cnx, pattern, sort):

    result = []

    # Query groups from database.

    c = cnx.cursor()
    q = 'SELECT id, name FROM groups'
    params = []
    con = 'WHERE'
    if pattern != '':
        q += ' %s name LIKE %%s' % con
        params.append('%%%s%%' % pattern)
        con = 'AND'
    if sort == '' or sort == 'id_u':
        q += ' ORDER BY id'
    elif sort == 'id_d':
        q += ' ORDER BY id DESC'
    elif sort == 'name_u':
        q += ' ORDER BY name'
    elif sort == 'name_d':
        q += ' ORDER BY name DESC'
    c.execute(q, params)
    rows = c.fetchall()
    for row in rows:
        id = row[0]
        name = row[1]
        result.append((id, name))

    # Done.

    return result


# Generate search panel.

def search_panel(results_per_page, pattern, devel):

    # Add form for pattern match and results per page.

    print '<form action="%s/query_groups.py" method="post">' % dbconfig.rel_url

    # Add hidden input for db instance.

    print '<input type="hidden" id="dev" name="dev" value=%d>' % devel

    # Add pattern wildcard input.

    print '<label for="pattern">Match: </label>'
    print '<input type="text" id="pattern" name="pattern" size=30 value="%s">' % pattern

    # Add results per page input.

    print '<label for="rpp">Groups per page: </label>'
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

    url = '%s/query_groups.py' % dbconfig.base_url

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
    print '<form action="%s/query_groups.py?%s" method="post">' % \
        (dbconfig.rel_url, dbargs.convert_args(new_qdict))
    print '<input type="submit" value="&#x25c4;&#x25c4;" %s>' % disabled
    print '</form>'
    print '</td>'

    # Add button for previous page.

    prev_page = max(current_page-1, 1)
    print '<td>'
    new_qdict = copy.deepcopy(qdict)
    new_qdict['page'] = prev_page
    print '<form action="%s/query_groups.py?%s" method="post">' % \
        (dbconfig.rel_url, dbargs.convert_args(new_qdict))
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
    print '<form action="%s/query_groups.py?%s" method="post">' % \
        (dbconfig.rel_url, dbargs.convert_args(new_qdict))
    print '<input type="submit" value="&#x25ba;" %s>' % disabled
    print '</form>'
    print '</td>'

    # Link to last page.

    print '<td>'
    new_qdict = copy.deepcopy(qdict)
    new_qdict['page'] = max_page
    print '<form action="%s/query_groups.py?%s" method="post">' % \
        (dbconfig.rel_url, dbargs.convert_args(new_qdict))
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
    devel = qdict['dev']
    sort = qdict['sort']

    # Open database connection and query groups.

    cnx = dbconfig.connect(readonly = True, devel = qdict['dev'])

    # Get list of project groups.

    groups = list_groups(cnx, pattern, sort)
    max_page = (len(groups) + results_per_page - 1) / results_per_page

    # Generate html document header.

    print 'Content-type: text/html'
    print
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<title>Project Groups</title>'
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

    # Add link to project full list.

    print '<a href=%s/query_projects.py?%s>Project list</a><br>' % \
        (dbconfig.base_url, dbargs.convert_args(qdict, 'gid', 0))

    # Generate main part of html document.

    print '<h1>Project Groups</h1>'

    # Add button to create new group.

    print '<form action="%s/add_group.py?%s" method="post" target="_self">' % \
        (dbconfig.rel_url, dbargs.convert_args(qdict))
    print '<label for="submit">Generate a new empty project group: </label>'
    print '<input type="submit" id="submit" value="New Group">'
    print '</form>'
    print '<p>'

    # Generate search panel form.

    search_panel(results_per_page, pattern, devel)

    # Display number of results.

    print '<p>%d project groups found</p>' % len(groups)

    # Generate upper navigation panel.

    page_links(qdict, max_page)

    # Group table.

    print '<table border=1 style="border-collapse:collapse">'
    print '<tr>'
    print '<th nowrap>'
    print '&nbsp;Group ID&nbsp;'

    # Add sort buttons.

    print '<div style="display:inline-block">'
    print '<form action="%s/query_groups.py?%s" method="post">' % \
        (dbconfig.rel_url, dbargs.convert_args(qdict, 'sort', 'id_u'))
    if sort == 'id_u':
        print '<input class="small-btn" type="submit" value="&#x25b2;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25b3;">'
    print '</form>'
    print '<form action="%s/query_groups.py?%s" method="post">' % \
        (dbconfig.rel_url, dbargs.convert_args(qdict, 'sort', 'id_d'))
    if sort == 'id_d':
        print '<input class="small-btn" type="submit" value="&#x25bc;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25bd;">'
    print '</form>'
    print '</div>'
    print '</th>'

    print '<th nowrap>'
    print '&nbsp;Group Name&nbsp;'

    # Add sort buttons.

    print '<div style="display:inline-block">'
    print '<form action="%s/query_groups.py?%s" method="post">' % \
        (dbconfig.rel_url, dbargs.convert_args(qdict, 'sort', 'name_u'))
    if sort == 'name_u':
        print '<input class="small-btn" type="submit" value="&#x25b2;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25b3;">'
    print '</form>'
    print '<form action="%s/query_groups.py?%s" method="post">' % \
        (dbconfig.rel_url, dbargs.convert_args(qdict, 'sort', 'name_d'))
    if sort == 'name_d':
        print '<input class="small-btn" type="submit" value="&#x25bc;">'
    else:
        print '<input class="small-btn" type="submit" value="&#x25bd;">'
    print '</form>'
    print '</div>'
    print '</th>'

    print '</tr>'

    # Loop over groups.

    for i in range((current_page-1) * results_per_page, 
                   min(current_page * results_per_page, len(groups))):
        group = groups[i]
        print '<tr>'
        id = group[0]
        name = group[1]
        print '<td align="center">%d</td>' % id

        # Construct disabled option for restricted controls.

        disabled = ''
        if not dbconfig.restricted_access_allowed():
            disabled = 'disabled'
        

        # Add group name with link to projects page.

        url = '%s/query_projects.py?%s' % \
              (dbconfig.base_url, dbargs.convert_args(qdict, 'gid', id))
        print '<td>&nbsp;<a href="%s">%s</a>&nbsp;</td>' % (url, name)

        # Add Edit button/column

        print '<td>'
        print '<form target="_self" action="%s/edit_group.py?id=%d&%s" method="post">' % \
            (dbconfig.rel_url, id, dbargs.convert_args(qdict))
        print '<div title="Edit group">'
        print '<input type="submit" value="&#x270e;">'
        print '</div>'
        print '</form>'
        print '</td>'        

        # Add Clone button/column

        print '<td>'
        print '<form target="_self" action="%s/clone_group.py?id=%d&%s" method="post">' % \
            (dbconfig.rel_url, id, dbargs.convert_args(qdict))
        print '<div title="Clone group">'
        print '<input type="submit" value="&#x2398;">'
        print '</div>'
        print '</form>'
        print '</td>'        

        # Add Delete button/column

        print '<td>'
        print '<form action="%s/delete_group.py?id=%d&%s" method="post">' % \
            (dbconfig.rel_url, id, dbargs.convert_args(qdict))
        print '<div title="Delete group">'
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
