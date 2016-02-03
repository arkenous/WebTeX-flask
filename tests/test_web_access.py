#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import eq_, ok_
import WebTeX
import os
from configparser import ConfigParser
import random

WebTeX.app.testing = True
client = WebTeX.app.test_client()
conf_path = os.path.dirname(os.path.abspath(__file__)) + '/../WebTeX.ini'
ldap_userlist = ['riemann', 'gauss', 'euler', 'euclid',
                 'einstein', 'newton', 'galieleo', 'tesla']


def test_get_index():
    res = client.get('/')
    eq_(302, res.status_code)
    eq_('http://localhost/login', res.headers['Location'])


def test_get_login():
    res = client.get('/login')
    eq_(200, res.status_code)


def test_fail_login():
    res = client.post('/login', data={
        'username': 'admin',
        'password': 'webtex'
    })
    eq_(200, res.status_code)


def test_login_local():
    config = ConfigParser()
    config.read(conf_path)
    config['auth']['method'] = 'local'
    with open(conf_path, 'w') as configfile:
        config.write(configfile)

    res = client.post('/login', data={
        'username': 'Admin',
        'password': 'webtex'
    })
    eq_(302, res.status_code)
    eq_('http://localhost/', res.headers['Location'])


def test_logout_local():
    with client.session_transaction() as sess:
        eq_(sess['username'], 'Admin')
    res = client.get('/logout')
    with client.session_transaction() as sess:
        eq_(sess, {})
    eq_(302, res.status_code)
    eq_('http://localhost/login', res.headers['Location'])


def test_login_ldap():
    config = ConfigParser()
    config.read(conf_path)
    config['auth']['method'] = 'ldap'
    config['ldap']['server'] = 'ldap.forumsys.com'
    config['ldap']['port'] = '389'
    config['ldap']['base_dn'] = 'dc=example,dc=com'
    with open(conf_path, 'w') as configfile:
        config.write(configfile)

    username = random.choice(ldap_userlist)
    res = client.post('/login', data={
        'username': username,
        'password': 'password'
    })
    eq_(302, res.status_code)
    eq_('http://localhost/', res.headers['Location'])


def test_logout_ldap():
    with client.session_transaction() as sess:
        ok_(sess['username'] in ldap_userlist)
    res = client.get('/logout')
    with client.session_transaction() as sess:
        eq_(sess, {})
    eq_(302, res.status_code)
    eq_('http://localhost/login', res.headers['Location'])


def test_get_index_after_logout():
    with client.session_transaction() as sess:
        eq_(sess, {})
    res = client.get('/')
    eq_(302, res.status_code)
    eq_('http://localhost/login', res.headers['Location'])
