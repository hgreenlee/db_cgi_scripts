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
sys.path.append('/web/sites/m/microboone-exp.fnal.gov/cgi-bin/lib/python2.7/site-packages')
import mysql.connector
from dbpasswd import *

# Experiment.

samweb_url = {'sbnd': 'https://samweb.fnal.gov:8483/sam/sbnd/api',
              'icarus': 'https://samweb.fnal.gov:8483/sam/icarus/api'}
cgi_url = 'https://microboone-exp.fnal.gov/cgi-bin'
base_url = 'https://microboone-exp.fnal.gov/cgi-bin/sbndb'
rel_url = '/cgi-bin/sbndb'

# Connection parameters.

host_dev = 'vip-mariadbdev.fnal.gov'
host_prd = 'vip-mariadbprd.fnal.gov'
db_dev = 'sbndpro_dev'
db_prd = 'sbndpro_prod'
port = 3309
reader_user = 'sbnpro_reader'
writer_user = 'sbnpro_writer'

# Authentication files.

auth1 = '/web/sites/m/microboone-exp.fnal.gov/data/auth/sbn.txt'
auth2 = '/web/sites/m/microboone-exp.fnal.gov/data/auth/sbn_dm.txt'

# Pull downs.

pulldowns = {'physics_group':    ['', 'OSC', 'XS', 'APE', 'DPC', 'Common'],
             'status':           ['', 'Requested', 'Approved', 'Processing', 'Suspended', 'Completed'],
             'file_type':        ['', 'data', 'mc', 'overlay'],
             'campaign':         ['', 'MCP0.9', 'MCP1.0', 'MCP2.0', 'MCP2.1', 'MCP2.2', 'MCP2020A'],
             'type':             ['', 'input', 'output'],
             'override_type':    ['regular', 'test'],
             'experiment':       ['', 'uboone', 'sbnd', 'icarus'],
             'poms_role':        ['production', 'analysis'],
             'poms_completion_type': ['completed', 'located'],
             'poms_login_setup': {'sbnd': ['',
                                           'sbnd_setup',
                                           'sbnd_setup_fife_utils_v3_2_4',
                                           'sbnd_setup_fife_utils_v3_2_5',
                                           'sbnd_setup_fife_utils_v3_2_5_testproxy',
                                           'sbnd_setup_fife_utils_v3_2_8',
                                           'sbnd_setup_fife_utils_v3_2_9',
                                           'sbnd_setup_fife_utils_v3_3',
                                           'sbnd_setup_fife_utils_v3_3_test'],
                                  'icarus': ['']},
             'poms_job_type':    {'sbnd': ['',
                                           'sbnd_pre-production_MCP0.9',
                                           'sbnd_official_MCP1.0',
                                           'sbnd_official_MCP2.0',
                                           'sbnd_official_MCP2.1',
                                           'sbnd_official_MCP2.2',
                                           'sbnd_official_MCP2020A',
                                           'sbnd_official_MCP2020A_reco'],
                                  'icarus': ['']}}

# Status colors.

colors = {'Requested':  '#a0ffff',
          'Approved':   '#ffd090',
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
