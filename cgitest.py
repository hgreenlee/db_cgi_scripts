#!/bin/env python

#
#  This is a CGI test page.
#

import sys, os, getpass, subprocess
import dbargs
import cgi
import cgitb
cgitb.enable()

#
#  Signal this will be an HTML page.
#

print 'Content-type: text/html'
print

#
#  Put out document header and start body.
#

print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">'
print '<HTML>'
print '<HEAD>'
print '<TITLE>cgitest.py</TITLE>'
print '</HEAD>'
print '<BODY>'

print '<CENTER><H1>cgitest.py</H1></CENTER>'

#
#  Show OS information.
#

print '<P>'
print '<FONT SIZE="+3"><B>OS</B></FONT>'
print '<P>'

for word in os.uname():
        print word,
        print ' ',
print '<BR>'
print 'user: %s<br>' % getpass.getuser()

#
#  Show environment vars.
#

print '<P>'
print '<FONT SIZE="+3"><B>Environment</B></FONT>'
print '<P>'

tmp = os.environ.keys()
tmp.sort()

for key in tmp: print key + '=' + os.environ[key] + '<BR>'

#
#result = 'None'
#try:
#        result = subprocess.check_output(['echo', 'Hello'])
#except:
#        result = 'subprocess fail'
#print result

#from pip import main
#argv = sys.argv
#sys.argv=['',''install']
#main()
#sys.argv = argv

#
# Show python exe and version.
#
print '<P>'
print '<FONT SIZE="+3"><B>Python</B></FONT>'
print '<P>'
print 'Python exe = %s<br>' % sys.executable
print 'Python version = %s<br>' % sys.version

print 'Trying to import mysql.connector<br>'
try:
        import mysql.connector
        print 'Import successful.<br>'
except:
        print 'Import failed.<br>'

print 'Trying to import pycurl<br>'
try:
        import pycurl
        print 'Import successful.<br>'
except:
        print 'Import failed.<br>'

#
#  Show passed cgi arguments.
#

print '<P>'
print '<FONT SIZE="+3"><B>CGI Arguments</B></FONT>'
print '<P>'

args = dbargs.get()
for k in args:
        print '%s = %s<BR>' % (k, args[k])

#
#  Show passed form data.
#

#print '<P>'
#print '<FONT SIZE="+3"><B>Form Data</B></FONT><BR>'
#print '<P>'

#buf = sys.stdin.readline()
#if '' == buf:
#	print '[None]<BR>'
#else:
#	while buf != '':
#		print buf + '<BR>'
#		buf = sys.stdin.readline()

#
#  End document body and put out trailer.
#

print '</BODY>'
print '</HTML>'
