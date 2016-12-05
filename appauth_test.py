#!/usr/bin/env python
# coding=utf8

# https client verification :
# http://stackoverflow.com/questions/22027418/openssl-python-requests-error-certificate-verify-failed

################################################################################
import sys
import requests
import collections
import unittest
from json import loads

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

################################################################################
def convert_str(data):
    """dict 혹은 list 멤버 등을 돌면서 다음과 같은 작업 수행
        - unicode 이면 utf8로 변환하여 리턴
        - 문자열이면 문자열 리턴
        - dict 이면 이를 해체하여 개별 키:값 쌍을 Recursive 하게 호출하여 재조립
        - list나 tuple 이면 이를 해체하여 개별 값 요소를 Recursive 하게 호출하여 재조립

    :param data: 변환을 위한 객체

    >>> d = { u'spam': u'eggs', u'foo': True, u'bar': { u'baz': 97 } }
    >>> print(d)
    {u'foo': True, u'bar': {u'baz': 97}, u'spam': u'eggs'}
    >>> d2 = convert_str(d)
    >>> print(d2)
    {'foo': True, 'bar': {'baz': 97}, 'spam': 'eggs'}
    """
    if sys.version_info[0] == 3:
        if isinstance(data, str):
            return data
        elif isinstance(data, collections.Mapping):
            return dict(map(convert_str, data.items()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(convert_str, data))
    else:
        if isinstance(data, unicode):
            return data.encode('utf-8')
        if isinstance(data, basestring):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(convert_str, data.items()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(convert_str, data))
    return data


################################################################################
class TU (unittest.TestCase):
    # ==========================================================================
    isFirst = True
    # #===========================================================================
    # @staticmethod
    # def myprint(rc, rj, msg):
    #     print('[%s]%s\nrc=%d, rj=%s' % (msg, '=' * 60, rc, pformat(rj)))

    # ==========================================================================
    def my_init(self):
        if TU.isFirst:
            TU.isFirst = False
            TU.host = '127.0.0.1'
            TU.port = 5000
            TU.session = requests.Session()

    # ==========================================================================
    def setUp(self): self.my_init()

    # ==========================================================================
    def tearDown(self):
        pass

    # ==========================================================================
    def test0000_init(self):
        self.assertTrue(True)

    # ==========================================================================
    def test0080_notauth_api_call(self):
        p_json = {
            'param10': 'param-03',
            'param11': 'param-04',
        }
        apipath = '/api/notauth_func'
        # not auth does not use cookies
        response = TU.session.post('https://%s:%s%s'
                                   % (TU.host, TU.port, apipath),
                                   json=p_json, verify=False)
        self.assertTrue(response.status_code == 200)
        r_json = convert_str(loads(response.text))
        self.assertTrue(r_json['ok'])
        print(str(r_json))

    # ==========================================================================
    def test0100_auth_api_call(self):
        p_json = {
            'param1': 'param-01',
            'param2': 'param-02',
        }
        apipath = '/api/auth_func'
        response = TU.session.post('https://%s:%s%s'
                                   % (TU.host, TU.port, apipath),
                                   json=p_json, verify=False)
        self.assertTrue(response.status_code == 401)  # authentication error

    # ==========================================================================
    def test0200_login(self):
        p_json = {
            'user_id': 'user01',
            'passwd_hash': 'user_01',
        }
        apipath = '/api/login'
        response = TU.session.post('https://%s:%s%s'
                                   % (TU.host, TU.port, apipath),
                                   json=p_json, verify=False)
        self.assertTrue(response.status_code == 200)
        r_json = convert_str(loads(response.text))
        self.assertTrue(r_json['ok'])
        print(str(r_json))

    # ==========================================================================
    def test0280_notauth_api_call(self):
        p_json = {
            'param12': 'param-03',
            'param13': 'param-04',
        }
        apipath = '/api/notauth_func'
        response = TU.session.post('https://%s:%s%s'
                                   % (TU.host, TU.port, apipath),
                                   json=p_json, verify=False)
        self.assertTrue(response.status_code == 200)
        r_json = convert_str(loads(response.text))
        self.assertTrue(r_json['ok'])
        print(str(r_json))

    # ==========================================================================
    def test0300_auth_api_call(self):
        p_json = {
            'param3': 'param-01',
            'param4': 'param-02',
        }
        apipath = '/api/auth_func'
        response = TU.session.post('https://%s:%s%s'
                                   % (TU.host, TU.port, apipath),
                                   json=p_json, verify=False)
        self.assertTrue(response.status_code == 200)
        r_json = convert_str(loads(response.text))
        self.assertTrue(r_json['ok'])
        print(str(r_json))

    # ==========================================================================
    def test0400_logout(self):
        apipath = '/api/logout'
        response = TU.session.post('https://%s:%s%s'
                                   % (TU.host, TU.port, apipath), verify=False)
        self.assertTrue(response.status_code == 200)
        r_json = convert_str(loads(response.text))
        self.assertTrue(r_json['ok'])
        print(str(r_json))

    # ==========================================================================
    def test0480_notauth_api_call(self):
        p_json = {
            'param14': 'param-03',
            'param15': 'param-04',
        }
        apipath = '/api/notauth_func'
        response = TU.session.post('https://%s:%s%s'
                                   % (TU.host, TU.port, apipath),
                                   json=p_json, verify=False)
        self.assertTrue(response.status_code == 200)
        r_json = convert_str(loads(response.text))
        self.assertTrue(r_json['ok'])
        print(str(r_json))

    # ==========================================================================
    def test0500_auth_api_call(self):
        p_json = {
            'param5': 'param-01',
            'param6': 'param-02',
        }
        apipath = '/api/auth_func'
        response = TU.session.post('https://%s:%s%s'
                                   % (TU.host, TU.port, apipath),
                                   json=p_json, verify=False)
        self.assertTrue(response.status_code == 401)  # authentication error


################################################################################
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TU)
    unittest.TextTestRunner(verbosity=2).run(suite)
