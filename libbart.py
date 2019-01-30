'''
This library is used for all network scripts.
It lists different functions that are used by several scripts.

'''
import re
import os
import sys
from collections import OrderedDict
from getpass import getpass


def checkip(ip):
    ipre = re.compile('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
                      '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    if ipre.match(ip):
        return ip
    else:
        return None


def readipfile(iparg):
    '''This module will return a list with the ip addresses and a list with
    errors. It can handle a single ip address or a file containing ip addresses.'''
    iplist = []
    iperror = []
    ipre = re.compile('((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
                      '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
    # subnet mask option /8 - /32 possibilities.
    # ipresubnet = re.compile('((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
    #                   '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/'
    #                   '([1-2][0-9]|3[0-2]|[8-9])')
    # First check if it is an ip address. If so, add it to the list
    # if ipresubnet.match(iparg):
    #     iplist = [x for x in IP(iparg)]
    if ipre.match(iparg):
        iplist.append(iparg)
    elif os.path.isfile(iparg):
        # open the file and see if it is a HPOV csv or just IPs.
        # Add them to the list
        with open(iparg, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or line.startswith("!") or not line:
                    continue
                elif line.startswith("Status"):
                    # print("line starts with a #")
                    continue
                elif ipre.search(line):
                    ip = ipre.search(line).group(0)
                    iplist.append(ip)
                else:
                    iperror.append("This line is not used: {}".format(line))
    else:
        iperror.append("Not an IP or an existing file: {}".format(iparg))

    return iplist, iperror


def envvariable(*args, prefix=None):
    '''Read the information either from the bash environment variables or use
    the input() function to retrieve it from the user.
    It returns a string with the variable information.'''
    l1 = list()
    for variable in args:
        if prefix:
            variable = prefix+variable
        try:
            envvar = os.environ[variable]
        except KeyError:
            # envvar = input(
            print(
                '[-] No environment variable was found for the ' +
                'environment variable: {}.\n'.format(variable) +
                '[-] Add it to your environment variables and restart the ' +
                'session or provide it manually.\n')
            envvar = getpass(prompt='variable {}: '.format(variable))
            os.environ[variable] = envvar
        l1.append(envvar)
    return l1
    if len(l1) == 1:
        return l1[0]
    else:
        return l1


def atoptr(iplist):
    from dns import reversename
    ptrlist = []
    for ip in iplist:
        ptrlist.append(reversename.from_address(ip).to_text())
    return ptrlist


def maxlength(l1):
    '''Getting the max length value of an iterable'''
    i = 0
    for x in l1:
        if len(x) > i:
            i = len(x)
    return i


def conf_range_gen(lines, step, debug=False):
    '''Generator to split the code while making sure it doesn't
    interrupt code blocks. 'lines' should be a long piece of text.
    Retrieved with f.readlines() for example.'''
    startincrease = 0
    totallines = len(lines)
    for x in range(0, totallines, step):
        start = x + startincrease
        configlines = lines[start:x + step]
        if debug:
            print('x, start, startincrease:', x, start, startincrease)
        if start + step >= totallines:
            # this is to catch the last part, to not be stuck in the while loop
            yield configlines
        else:
            i = 0
            while (configlines[-1] != '!\n' and
                   configlines[-1] != '!\r' and
                   configlines[-1] != '!' and
                   configlines[-1] != '\n' and
                   configlines[-1] != '\r' and
                   configlines[-1] != '\n\r'):
                # If the code doesn't end on a line that starts and ends with !
                # We will increase the length until we find one.
                # The next run of the for loop will have to increase with that
                # number to avoid errors of duplicate code.
                if debug:
                    print(configlines[-1])
                i += 1
                configlines = lines[start: x + step + i]
                if debug:
                    print('while configlines: %r' % configlines[-1])
                    print(len(configlines))
            startincrease = i
            yield configlines


def split_ip(ip):
    return tuple(int(part) for part in ip.split('.'))
