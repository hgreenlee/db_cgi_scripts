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
import cgi
import cgitb
cgitb.enable()

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
        k = kv[0]
        if k not in result:
            if len(arg) > 1:
                result[k] = kv[1]
            else:
                result[k] = ''

    # Done.

    return result


# Return argument dictionary consisting of only arguments used by query_projects.py.

def get_qdict():

    # Initialize return value argument dictionary.

    result = {}

    # Parse CGI arguments.

    args = cgi.FieldStorage()
    for k in args:
        if k == 'results_per_page' or k == 'page' or k == 'pattern':
            arg = args[k]
            if type(arg) == type([]):
                result[k] = arg[-1].value   # Give priority to last element of list.
            else:
                result[k] = arg.value

    # Parse CLI arguments.

    for arg in sys.argv[1:]:
        kv = arg.split('=')
        k = kv[0]
        if k == 'results_per_page' or k == 'page' or k == 'pattern':
            if k not in result:
                if len(arg) > 1:
                    result[k] = kv[1]
                else:
                    result[k] = ''

    # Done.

    return result

    
