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

def get():

    # Initialize return value argument dictionary.

    result = {}

    # Parse CGI arguments.

    args = cgi.FieldStorage()
    for k in args:
        result[k] = args[k].value

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

    
