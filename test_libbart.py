import pytest
# import os
import libbart as lb
from ipaddress import ip_address

# def test_function():
#     cmd = "echo hello"
#     expected = "hello"
#     got = lb.return_cmd(cmd)
#     assert got == expected


def test_isIp():
    cmd = "1.2.3.4"
    got = lb.isIp(cmd)
    assert got is True
    cmd = "2002::6"
    got = lb.isIp(cmd)
    assert got is True


def test_read_ips_from_file():
    file_path = "test_ipfile.txt"
    expected = ["1.2.3.4", "1.1.1.1", "238.39.39.39"]
    got = lb.read_ips_from_file(file_path)
    print(got)
    assert got == expected
    assert bool(got) is True
    assert len(got) == 3


def test_extract_path():
    vrfs = {
        'L3vpn': {
            'L3vpnVRF': {
                'VRF': {
                    'VRF': ''
                }
            }
        }
    }
    got = lb.extract_path(vrfs)
    expected = ['L3vpn', 'L3vpnVRF', 'VRF']
    assert got == expected


def test_deref_multi():
    vrfs = {
        'L3vpn': {
            'L3vpnVRF': {
                'VRF': {
                    "RD": "10.1.2.3:100",
                    "VRF": "mgmt"
                }
            }
        }
    }
    keys = ['L3vpn', 'L3vpnVRF', 'VRF']
    got = lb.deref_multi(data=vrfs, keys=keys)
    expected = {"RD": "10.1.2.3:100", "VRF": "mgmt"}
    assert got == expected


def test_clean_zero_values():
    d1 = {
        'a': 1,
        'b': '0',
        'c': 0,
        'd': 'abc',
        'e': ['some_value', 'another']
    }
    got = lb.clean_zero_values(d1)
    expected = {
        'a': 1,
        'c': 0,
        'd': 'abc',
        'e': ['some_value', 'another']
    }
    assert got == expected
