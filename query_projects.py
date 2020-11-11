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
# results_per_page - Number of projects to display on each page.
# page             - Current page (starts at 1).
# pattern          - Search pattern.
#
# Created: 15-Oct-2020  H. Greenlee
#
#==============================================================================

import sys, os
import dbconfig, dbargs


# Return list of projects.

def list_projects(cnx, pattern):

    result = []

    # Query projects from database.

    c = cnx.cursor()
    q = 'SELECT id, name FROM projects'
    if pattern != '':
        q += ' WHERE name LIKE \'%%%s%%\'' % pattern
    q += ' ORDER BY id'
    c.execute(q)
    rows = c.fetchall()
    for row in rows:
        id = row[0]
        name = row[1]
        result.append((id, name))

    # Done.

    return result


# Generate search panel.

def search_panel(results_per_page, pattern):

    # Add form for pattern match and results per page.

    print '<form action="/cgi-bin/query_projects.py" method="post">'
    print '<label for="pattern">Match:</label>'
    print '<input type="text" id="pattern" name="pattern" size=30 value="%s">' % pattern
    print '<label for="rpp">Projects per page:</label>'
    print '<input type="text" id="rpp" name="results_per_page" size=6 value=%d><br>' % \
        results_per_page
    print '<input type="submit" value="Search">'
    print '</form>'

    # Done.

    return


# Generate page links.

def page_links(results_per_page, current_page, max_page, pattern):

    # Base url.

    url = 'https://microboone-exp.fnal.gov/cgi-bin/query_projects.py'

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
    print '<form action="/cgi-bin/query_projects.py?results_per_page=%d&page=%d&pattern=%s" method="post">' % \
        (results_per_page, 1, pattern)
    print '<input type="submit" value="<<" %s>' % disabled
    print '</form>'
    print '</td>'

    # Add button for previous page.

    prev_page = max(current_page-1, 1)
    print '<td>'
    print '<form action="/cgi-bin/query_projects.py?results_per_page=%d&page=%d&pattern=%s" method="post">' % \
        (results_per_page, prev_page, pattern)
    print '<input type="submit" value="<" %s>' % disabled
    print '</form>'
    print '</td>'

    # Links to specific pages.

    for page in range(min_link, max_link+1):
        if page != current_page:
            print '<td align="center" style="width:25px;"><a href="%s?results_per_page=%d&page=%d&pattern=%s">%d</a></td>' % \
                (url, results_per_page, page, pattern, page)
        else:
            print '<th align="center" style="width:25px;">%d</th>' % page


    # Link to next page.

    disabled = ''
    if current_page == max_page:
        disabled = 'disabled'
    next_page = min(current_page+1, max_page)
    print '<td>'
    print '<form action="/cgi-bin/query_projects.py?results_per_page=%d&page=%d&pattern=%s" method="post">' % \
        (results_per_page, next_page, pattern)
    print '<input type="submit" value=">" %s>' % disabled
    print '</form>'
    print '</td>'

    # Link to last page.

    print '<td>'
    print '<form action="/cgi-bin/query_projects.py?results_per_page=%d&page=%d&pattern=%s" method="post">' % \
        (results_per_page, max_page, pattern)
    print '<input type="submit" value=">>" %s >' % disabled
    print '</form>'
    print '</td>'

    # Finish table.

    print '</tr>'
    print '</table>'

    # Done.

    return


# Main procedure.

def main(results_per_page, current_page, pattern):

    # Open database connection and query projects.

    cnx = dbconfig.connect(readonly = True)

    # Get list of projects.

    prjs = list_projects(cnx, pattern)
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

    # Generate main part of html document.

    print '<h1>Projects</h1>'

    # Add button to create new project.

    print '<form action="/cgi-bin/add_project.py?results_per_page=%d&page=%d&pattern=%s" method="post" target="_blank" rel="noopener noreferer">' % \
        (results_per_page, current_page, pattern)
    print '<label for="submit">Generate a new empty project: </label>'
    print '<input type="submit" id="submit" value="New Project">'
    print '</form>'
    print '<p>'

    # Add button to import a project from local xml file.

    print '<form action="/cgi-bin/import_project.py?results_per_page=%d&page=%d&pattern=%s" method="post" target="_blank" rel="noopener noreferer">' % \
        (results_per_page, current_page, pattern)
    print '<label for="submit">Import project from local XML file: </label>'
    print '<input type="submit" id="submit" value="Import Project">'
    print '</form>'
    print '<p>'

    # Generate search panel form.

    search_panel(results_per_page, pattern)

    # Display number of results.

    print '<p>%d projects found</p>' % len(prjs)

    # Generate upper navigation panel.

    page_links(results_per_page, current_page, max_page, pattern)

    # Project table.

    print '<table border=1 style="border-collapse:collapse">'
    print '<tr>'
    print '<th>Project ID</th>'
    print '<th>Project Name</th>'
    print '</tr>'
    for i in range((current_page-1) * results_per_page, 
                   min(current_page * results_per_page, len(prjs))):
        prj = prjs[i]
        print '<tr>'
        id = prj[0]
        name = prj[1]
        print '<td align="center">%d</td>' % id
        print '<td>&nbsp;<a target=_blank rel="noopener noreferer" href=https://microboone-exp.fnal.gov/cgi-bin/edit_project.py?id=%d&results_per_page=%d&page=%d&pattern=%s>%s</a>&nbsp;</td>' % \
            (id, results_per_page, current_page, pattern, name)

        # Add XML button/column

        print '<td>'
        print '<form target="_blank" rel="noopener noreferer" action="/cgi-bin/export_project.py?id=%d&results_per_page=%d&page=%d&pattern=%s" method="post">' % \
            (id, results_per_page, current_page, pattern)
        print '<input type="submit" value="XML">'
        print '</form>'
        print '</td>'        

        # Add Clone button/column

        print '<td>'
        print '<form target="_blank" rel="noopener noreferer" action="/cgi-bin/clone_project.py?id=%d&results_per_page=%d&page=%d&pattern=%s" method="post">' % \
            (id, results_per_page, current_page, pattern)
        print '<input type="submit" value="Clone">'
        print '</form>'
        print '</td>'        

        # Add Delete button/column

        print '<td>'
        print '<form action="/cgi-bin/delete_project.py?id=%d&results_per_page=%d&page=%d&pattern=%s" method="post">' % \
            (id, results_per_page, current_page, pattern)
        print '<input type="submit" value="Delete">'
        print '</form>'
        print '</td>'        
        print '</tr>'
    print '</table>'

    # Add lower navigation panel.

    page_links(results_per_page, current_page, max_page, pattern)

    # Generate html document trailer.
    
    print '</body>'
    print '</html>'


# End of definitions.  Executable code starts here.

if __name__ == "__main__":

    # Parse arguments.

    results_per_page = 20
    current_page = 1
    pattern = ''
    args = dbargs.get()
    if 'results_per_page' in args:
        results_per_page = int(args['results_per_page'])
    if 'page' in args:
        current_page = int(args['page'])
    if 'pattern' in args:
        pattern = args['pattern']

    # Call main procedure.

    main(results_per_page, current_page, pattern)
