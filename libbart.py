'''
This library is used for all network scripts.
It lists different functions that are used by several scripts.

'''
import functools
import json
import logging
import os
import pprint
import re
from ipaddress import ip_address
from time import time

import xmltodict
from dns import reversename


def isIp(ip: str) -> bool:
    try:
        return bool(ip_address(ip))
    except ValueError:
        return None


def read_ips_from_file(file_path: object) -> list:
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


def atoptr(iplist: list) -> list:
    ptrlist = []
    for ip in iplist:
        ptrlist.append(reversename.from_address(ip).to_text())
    return ptrlist


def maxlength(list_obj: list) -> int:
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
                   and configlines[-1] != '!' and configlines[-1] != '\n'
                   and configlines[-1] != '\r' and configlines[-1] != '\n\r'):
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


def beautify(value: object, indent: int = 0, **kwargs):
    """Using pprint to beautify the output.

    Args:
        value: The input to be beautified
        indent (int): Set the indentation spaces, default = 0
        **kwargs: Any known key/values for the pprint.PrettyPrinter function

    """
    pp = pprint.PrettyPrinter(indent=indent, **kwargs)
    pp.pprint(value)


def enable_debug() -> None:
    """Enabling debug."""
    logging.basicConfig(level=logging.DEBUG)


def is_int(val: object) -> bool:
    """Returns True if it is an Integer or a String containing integers.

    Args:
        val: The input to be validated

    Returns:
        boolean.

    """
    if isinstance(val, (str, int)) and (isinstance(val, int) or val.isdigit()):
        return True
    else:
        return False


def save_file(data: object, filename: str) -> None:
    """Save data to a file
    filename is expected to be a string.
    the file is stored in the root of this project/output.

    Args:
        data: the data to be stored
        filename: the filename to be used

    """
    output_file = os.path.abspath(filename)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(str(data))
    print(f"Successfully written to: '{output_file}'")


def xml2json(xml_str: str, indent: int = 2):
    """Convert xml to json.

    Args:
        xml_str: the xml string
        indent: amount of spaces to indent. Default = 2.

    Returns:
        json format of the xml

    """
    parsed = xmltodict.parse(xml_str.replace(']]>]]>', ''))
    return json.dumps(parsed,
                      sort_keys=True,
                      indent=indent,
                      separators=(',', ': '))


def minimal_recurring(character: str, string: str) -> str:
    """Find the minimal length of a recurring character
    Regular expression is used to find the minimal repeated set of characters.

    example:
    minimal_recurring("\n", '\n\n\nabc_abc\n\nabc_abc_abc\n\n\n\n')
    would return: '\n\n'

    Args:
        character: The repeated character to be found
        string: the text to be found in

    :Returns:
        the smallest group of found characters if found. Else the character itself.
    """
    amount_new_lines = re.compile(r'(%s+)' % character)
    found = amount_new_lines.findall(string)
    return min(found) if found else character


def timer(func):
    """Functools makes sure the function identification is correct.
    e.g. with functools:
    func
    <function func at 0x7f7bbc020620>

    without functools:
    func
    <function timer.<locals>.wrapper at 0x7faaf999d378>

    https://realpython.com/python-timer/#a-python-timer-decorator
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        before = time()
        rv = func(*args, **kwargs)
        print('time required (%s): %s' % (func.__name__, time() - before))
        return rv

    return wrapper


def extract_path(data: object, list_obj: list = None) -> list:
    """Extra the provided dictionary path to a list.

    Args:
        data: The dictionary with the desired filter. Example:
        vrfs = {
            'L3vpn': {
                'L3vpnVRF': {
                    'VRF': {
                        'VRF': ''
                    }
                }
            }
        }
        list_obj: Not to be filled when calling the function initially.

    :returns
        ['L3vpn', 'L3vpnVRF', 'VRF']

    therefore taking every single dict within another until it reaches the end and the
    path is presented as a list.
    """
    if list_obj is None:
        list_obj = list()
    if isinstance(data[list(data)[0]], dict) and len(tuple(data)) == 1:
        list_obj.append(list(data)[0])
        extract_path(data[list(data)[0]],
                     list_obj) if data[list(data)[0]] else None
    return list_obj


def deref_multi(data: dict, keys: list) -> dict:
    """Extract the dict given the keys as a path
    :param data: dict
    :param keys: list
    :return:

    Given a dict:
    {
        "L3vpn": {
            "L3vpnVRF": {
                "VRF": {
                    "RD": "10.1.2.3:100",
                    "VRF": "mgmt"
                }
            }
        }
    }

    the keys will present a path to extract the desired values.

    Where keys is:
    ['L3vpn', 'L3vpnVRF', 'VRF']

    return all values below the last matching dict. In this case
    {
        "RD": "10.1.2.3:100",
        "VRF": "mgmt"
    }
    """
    return deref_multi(data.get(keys[0]), keys[1:]) if keys and data else data


def clean_zero_values(dict_obj: dict) -> dict:
    return {x: y for x, y in dict_obj.items() if y != '0'}
