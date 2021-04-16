#==============================================================================
#
# Name: dbconfig.py
#
# Purpose: Python module containing database connection parameters.
#          Includes a functino for returning a database connection.
#
# Created: 16-Oct-2020  H. Greenlee
#
#==============================================================================

# Import mysql api.

import sys, os, getpass
from dbpasswd import *

# E-mail recipients (comma-separated list).

#email = 'greenlee@fnal.gov'
email = ''

# Directories.

base_dir = os.path.dirname(os.path.abspath(__file__))
cgi_dir = os.path.dirname(base_dir)
top_dir = os.path.dirname(cgi_dir)
data_dir = '%s/data' % top_dir
auth_dir = '%s/auth' % data_dir
request_dir = '%s/requests' % data_dir

# Import mysql

sys.path.append('%s/lib/python2.7/site-packages' % cgi_dir)
import mysql.connector

# Urls.

samweb_url = {'uboone': 'https://samweb.fnal.gov:8483/sam/uboone/api'}
top_url = 'https://%s' % os.path.basename(top_dir)
cgi_url = '%s/%s' % (top_url, os.path.basename(cgi_dir))
base_url = '%s/%s' % (cgi_url, os.path.basename(base_dir))
rel_url = '/%s/%s' % (os.path.basename(cgi_dir), os.path.basename(base_dir))

# Connection parameters.

host_dev = 'vip-mariadbdev.fnal.gov'
host_prd = 'vip-mariadbprd.fnal.gov'
db_dev = 'ubprod'
db_prd = 'ubprod'
port = 3309
reader_user = 'ubprod_reader'
writer_user = 'ubprod_writer'

# Authentication files.

auth1 = '%s/uboone.txt' % auth_dir
auth2 = '%s/dm.txt' % auth_dir

# Pull downs.

pulldowns = {'physics_group':    ['', 'OSC', 'XS', 'APE', 'DPC', 'DL', 'Wire Cell','gLEE', 'PeLEE', 'Common'],
             'status':           ['', 'Requested', 'Approved', 'Rejected', 'Processing', 'Suspended', 'Completed'],
             'file_type':        ['', 'data', 'mc', 'overlay'],
             'campaign':         ['', 'MCC8', 'MCC9', 'MCC 9.reco1', 'MCC 9.0', 'MCC 9.1', 'swizzle'],
             'type':             ['', 'input', 'output'],
             'override_type':    ['regular', 'test'],
             'experiment':       ['', 'uboone', 'sbnd', 'icarus'],
             'role':             ['', 'Production', 'Analysis'],
             'schema':           ['', 'root', 'gsiftp'],
             'poms_role':        ['production', 'analysis'],
             'poms_completion_type': ['completed', 'located'],
             'poms_login_setup': {'uboone': ['',
                                             'swizzle_crt_merge',
                                             'wizzle_crt_merge_mcc9',
                                             'MCC9_validation_could_kill',
                                             'MCC9_validation_could_kill_06',
                                             'MCC9_validation_could_kill_07',
                                             'MCC9_validation_could_kill_07_eLeeLow',
                                             'MCC9_validation_could_kill_07_temp',
                                             'MCC9_validation_could_kill_07 XTEST',
                                             'MCC9_validation_could_kill_08',
                                             'MCC9_validation_could_kill_09',
                                             'MCC9_validation_could_kill_10',
                                             'uboone template']},
             'poms_job_type':    {'uboone': ['', 
                                             'uBooNE Electron Lefetime',
                                             'uBooNE SPErate',
                                             'swlzzle_crt_merge',
                                             'MCC8 Reconstruction',
                                             'MCC9 Reconstruction']}}

# Status colors.

colors = {'Requested':  '#a0ffff',
          'Approved':   '#ffd090',
          'Rejected':   '#c0c0c0',
          'Processing': '#ffff90',
          'Suspended':  '#ffc0c0',
          'Completed':  '#c0ffb0'}


# Get user name.

def getuser():
    result = ''

    # First try environment variable SSO_USERID.
    # This method works for web server with SSO.

    if 'SSO_USERID' in os.environ:
        result = os.environ['SSO_USERID']

    # Next try use getpass.getuser().
    # This works for normal interactive environment.

    if result == '':
        result = getpass.getuser()

    # Done.

    return result


# Open database connection.
# Returns a MySQLConnection object or posts error if not authorized.

def connect(readonly=True, devel=False):

    # Check user.

    if not readonly:
        username=''
        auth = False
        username = getuser()
        if username != '':
            f = open(auth1)
            for line in f.readlines():
                words = line.strip().split(':')
                if words[0] == username:
                    auth = True
                    break
        if not auth:
            print 'Content-type: text/html'
            print 'Status: 403 Forbidden'
            print
            print '<html>'
            print '<title>403 Forbidden</title>'
            print '<body>'
            print '<h1>403 Forbidden</h1>'
            print 'You are not authorized to access this content.'
            print '</body>'
            print '</html>'
            sys.exit(0)

    # Open connection.

    user = ''
    pw = ''
    if readonly:
        user = reader_user
        pw = reader_pw
    else:
        user = writer_user
        pw = writer_pw

    host = ''
    if devel:
        host = host_dev
    else:
        host = host_prd

    db = ''
    if devel:
        db = db_dev
    else:
        db = db_prd

    cnx = mysql.connector.connect(database=db,
                                  host=host,
                                  port=port,
                                  user=user,
                                  password=pw)

    # Done.

    return cnx


# Check whether the user is allowed to have restricted access.

def restricted_access_allowed():

    # Check userid against allowed restricted users.

    username=''
    auth = False
    username = getuser()
    if username != '':
        f = open(auth2)
        for line in f.readlines():
            words = line.strip().split(':')
            if words[0] == username:
                auth = True
                break

    # Done.

    return auth


