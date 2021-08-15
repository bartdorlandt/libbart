'''
This library is used for all network scripts.
It lists different functions that are used by several scripts.

'''
import os
from ipaddress import ip_address

from dns import reversename


def isIp(ip):
    try:
        if ip_address(ip):
            return True
    except ValueError:
        return None


def read_ips_from_file(file_path):
    iplist = []
    if not os.path.isfile(file_path):
        return False
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or line.startswith("!") or not line:
                continue
            if isIp(line):
                iplist.append(line)
    return iplist


def atoptr(iplist):
    ptrlist = []
    for ip in iplist:
        ptrlist.append(reversename.from_address(ip).to_text())
    return ptrlist


def maxlength(list_obj):
    '''Getting the max length value of an iterable'''
    return len(max(list_obj, key=len))


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
            while (configlines[-1] != '!\n' and configlines[-1] != '!\r'
                   and configlines[-1] != '!' and configlines[-1] != '\n'  # noqa
                   and configlines[-1] != '\r' and configlines[-1] != '\n\r'):  # noqa
                # If the code doesn't end on a line that starts and ends with !
                # We will increase the length until we find one.
                # The next run of the for loop will have to increase with that
                # number to avoid errors of duplicate code.
                if debug:
                    print(configlines[-1])
                i += 1
                configlines = lines[start:x + step + i]
                if debug:
                    print('while configlines: %r' % configlines[-1])
                    print(len(configlines))
            startincrease = i
            yield configlines
