import argparse
import pyodbc


def print_headline():
    print'''
                                sqinner
    A SQL service login bruteforcer and MSSQL xp_cmdshell wrapper
                  Frank Allenby - frank@sensepost.com
    '''


def make_db_connection(driver, server, port, uid, pwd):
    return pyodbc.connect(
        'DRIVER={%(driver)s};\
        SERVER=%(server)s;\
        Port=%(port)d\
        UID=%(uid)s;\
        PWD=%(pwd)s;'
        %
        {
            'driver': driver,
            'server': server,
            'port': port,
            'uid': uid,
            'pwd': pwd
        }
    )


# Convert a file to an array
# Each line in the file becomes an item in the array, removing newlines
def file_to_array(filename):
    with open(filename) as file:
        return [line.rstrip('\n') for line in file]


# Convert an argument to an array
# If there is a list of items, this will be recursive to allow for multiple
# files of arguments, etc
# e.g. users.txt,sally,tom,other_users.txt
#   will return a list of all lines in users.txt and other_users.txt as well
#   as 'sally' and 'tom
def arg_to_array(argument):
    if ',' in argument:
        arguments = []
        for item in argument.split(','):
            arguments += arg_to_array(item)
        return arguments
    elif '.' in argument:
        return file_to_array(argument)
    else:
        return [argument]

parser = argparse.ArgumentParser(description='sqinner - SQL login bruteforcer\
                                 and MSSQL xp_cmdshell wrapper')

parser.add_argument(
    'target',
    type=str,
    help='The target SQL instance you wish to bruteforce. Should be a hostname\
    or IP address.'
)

parser.add_argument(
    'port',
    type=int,
    help='The port you wish to use to connect to the SQL instance. Usually 445 \
    or 1433.'
)

parser.add_argument(
    '-u',
    '--usernames',
    help='The username(s) you wish to bruteforce. Specify a single username, a\
    list of comma-separated files and/or usernames, or a wordlist to use.',
    required=True
)

parser.add_argument(
    '-p',
    '--passwords',
    help='The password(s) you wish to bruteforce. Specify a single password,\
    a list of comma-separated files and/or passwords, or a wordlist to use.',
    required=True
)

parser.add_argument(
    '-s',
    '--service',
    default='SQL Server',
    help='The service you wish to bruteforce. This should be used if you wish\
    to use something other than MSSQL. Note that anything other than "SQL\
    Server" will disable the xp_cmdshell functionality.',
    required=False
)

parser.add_argument(
    '--horizontal',
    action='store_true',
    help='Perform the bruteforce in a horizontal manner, iterating over\
    passwords and then usernames, rather than usernames and then passwords'
)

print_headline()

args = parser.parse_args()

shell_service = 'SQL Server'
shell_enabled = (args.service == shell_service)

usernames = arg_to_array(args.usernames)
passwords = arg_to_array(args.passwords)
