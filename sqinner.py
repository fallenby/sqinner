import argparse
import _mssql

program_info = {
    'name': 'sqinner',
    'description': 'A MSSQL service login bruteforcer xp_cmdshell wrapper',
    'author': {
        'name': 'Frank Allenby',
        'email': 'frank@sensepost.com'
    }
}

program_defaults = {
    'service': 'SQL Server'
}

notices = {
    'success': '[!]',
    'fail': '[!]',
    'info': '[?]'
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
    -
    | %(name)s
    |
    | %(description)s
    |
    | %(author_name)s - %(author_email)s
    -
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


def brute(usernames, passwords, verbose):
    notice_info('Starting bruteforce with %(username_count)d username(s) and %(password_count)d password(s)' % {'username_count': len(usernames), 'password_count': len(passwords)})
    print ' |'
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
                print ' |'
            notice_success('Login succeeded with %(username)s : %(password)s' % {'username': username, 'password': password})


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
