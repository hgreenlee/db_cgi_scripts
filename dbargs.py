#==============================================================================
#
# Name: dbargs.py
#
# Purpose: Python module argument parser, works for both CLI and CGI arguments.
#
# Created: 10-Nov-2020  H. Greenlee
#
# Usage:
#
# 1.  Returns parsed arguments in the form of a python dictionsry args[key]=value.
#     Key and value are strings.
#
#     import dbargs
#     args = dbargs.get()
#
# 2.  To use with CLI, pass arguments as space-separated "key=value" arguments 
#     on command line:
#
#     myscript.py x=1 y=2
#
# 3.  For use with CGI, pass arguments in the usual way using GET or POST:
#
#     https://path/to/myscript.py?x=1&y=2
#
#==============================================================================

import sys
import dbutil
import cgi
import cgitb
cgitb.enable()


# Convert argument dictionary to ampersand-separated list of key-value pairs.

def convert_args(argdict, k=None, v=None):

    result = ''

    for key in argdict:
        if result != '':
            result += '&'
        value = None
        if key == k:
            value = v
        else:
            value = argdict[key]
        result += '%s=%s' % (dbutil.convert_str(key), dbutil.convert_str(value))

    # Done

    return result


# Return argument dictionary consisting of all arguments.

def get():

    # Initialize return value argument dictionary.

    result = {}

    # Parse CGI arguments.

    args = cgi.FieldStorage()
    for k in args:
        arg = args[k]
        if type(arg) == type([]):
            result[k] = arg[-1].value   # Give priority to last element of list.
        else:
            result[k] = arg.value

    # Parse CLI arguments.

    for arg in sys.argv[1:]:
        kv = arg.split('=')
        if len(kv) > 1:
            k = kv[0]
            if k not in result:
                result[k] = kv[1]

    # If there is a 'debug' argument with any value other than '0', post a plain text header.

    if 'debug' in result and result['debug'] != '0':
        print 'Content-type: text/plain'
        print

    # Done.

    return result


# Extract dictionary arguments consisting only of arguments used by query_projects.py.
# All arguments get a default value.

def extract_qdict(argdict):

    # Initialize return value argument dictionary.

    result = {}

    # Parse arguments

    for k in argdict:

        # Integer arguments.

        if k == 'results_per_page' or k == 'page' or k == 'dev':
            result[k] = int(argdict[k])

        # String arguments.

        elif k == 'pattern' or k == 'group' or k == 'status' or k == 'sort':
            result[k] = argdict[k]

    # Parse CLI arguments.

    for arg in sys.argv[1:]:
        kv = arg.split('=')
        if len(kv) > 1:
            k = kv[0]

            # Integer arguments (convert to integer).

            if k == 'results_per_page' or k == 'page' or k == 'dev':
                if k not in result:
                    result[k] = int(kv[1])

            # String arguments.

            elif k == 'pattern' or k == 'group' or k == 'status' or k == 'sort':
                if k not in result:
                    result[k] = kv[1]

    # Add default values for certain arguments.

    if not 'results_per_page' in result:
        result['results_per_page'] = 20
    if not 'page' in result:
        result['page'] = 1
    if not 'dev' in result:
        result['dev'] = 0
    if not 'pattern' in result:
        result['pattern'] = ''
    if not 'group' in result:
        result['group'] = ''
    if not 'status' in result:
        result['status'] = ''
    if not 'sort' in result:
        result['sort'] = ''

    # Done.

    return result


