#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import eq_, ok_, with_setup
from WebTeX import app
import os
import json
from configparser import ConfigParser
import random

app.testing = True
client = app.app.test_client()
webtex_path = os.path.dirname(os.path.abspath(__file__)) + '/../WebTeX/'
conf_path = webtex_path + 'WebTeX.ini'
ldap_userlist = ['riemann', 'gauss', 'euler', 'euclid',
                 'einstein', 'newton', 'galieleo', 'tesla']


def setup():
    conf_dict = {'mode': 'local', 'ldap_address': '', 'ldap_port': '',
                 'ldap_basedn': '', 'java_home': '/usr/lib/jvm/java-8-oracle',
                 'redpen_conf_path': os.path.expanduser(
                     '~/redpen/conf/redpen-conf-en.xml')}
    res = client.post('/saveConfig',
                      data=json.dumps(conf_dict),
                      content_type='application/json')
    eq_(200, res.status_code)


def teardown():
    config = ConfigParser()
    config.read(conf_path)
    config['setup']['initial_setup'] = 'true'
    f = open(conf_path, 'w')
    config.write(f)
    f.close()

    res = client.get('/')
    eq_(302, res.status_code)
    eq_('http://localhost/initialize', res.headers['Location'])

    res = client.get('/login')
    eq_(302, res.status_code)
    eq_('http://localhost/initialize', res.headers['Location'])

    res = client.get('/initialize')
    eq_(200, res.status_code)


def change_initial_setup_to_true():
    config = ConfigParser()
    config.read(conf_path)
    config['setup']['initial_setup'] = 'true'
    f = open(conf_path, 'w')
    config.write(f)
    f.close()


def change_initial_setup_to_false():
    config = ConfigParser()
    config.read(conf_path)
    config['setup']['initial_setup'] = 'false'
    f = open(conf_path, 'w')
    config.write(f)
    f.close()


@with_setup(change_initial_setup_to_true, change_initial_setup_to_false)
def test_get_index_before_initialize():
    res = client.get('/')
    eq_(302, res.status_code)
    eq_('http://localhost/initialize', res.headers['Location'])


@with_setup(change_initial_setup_to_true, change_initial_setup_to_false)
def test_get_login_before_initialize():
    res = client.get('/login')
    eq_(302, res.status_code)
    eq_('http://localhost/initialize', res.headers['Location'])


@with_setup(change_initial_setup_to_true, change_initial_setup_to_false)
def test_get_initialize():
    res = client.get('/initialize')
    eq_(200, res.status_code)


@with_setup(change_initial_setup_to_true, change_initial_setup_to_false)
def test_initialize():
    conf_dict = {'mode': 'local', 'ldap_address': '', 'ldap_port': '',
                 'ldap_basedn': '', 'java_home': '/usr/lib/jvm/java-8-oracle',
                 'redpen_conf_path': os.path.expanduser(
                     '~/redpen/conf/redpen-conf-en.xml')}
    res = client.post('/saveConfig',
                      data=json.dumps(conf_dict),
                      content_type='application/json')
    eq_(200, res.status_code)

    config = ConfigParser()
    config.read(conf_path)
    eq_('false', config['setup']['initial_setup'])
    eq_('local', config['auth']['method'])
    eq_('', config['ldap']['server'])
    eq_('', config['ldap']['port'])
    eq_('', config['ldap']['base_dn'])
    eq_('/usr/lib/jvm/java-8-oracle', config['redpen']['java_home'])
    eq_(os.path.expanduser('~/redpen/conf/redpen-conf-en.xml'),
        config['redpen']['conf'])


def test_get_index():
    res = client.get('/')
    eq_(302, res.status_code)
    eq_('http://localhost/login', res.headers['Location'])


def test_get_login():
    res = client.get('/login')
    eq_(200, res.status_code)


def test_fail_login_local_invalid_username():
    res = client.post('/login', data={
        'username': 'admin',
        'password': 'webtex'
    })
    eq_(200, res.status_code)


def test_fail_login_local_invalid_password():
    res = client.post('/login', data={
        'username': 'Admin',
        'password': 'WebTeX'
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


def test_fail_login_ldap():
    config = ConfigParser()
    config.read(conf_path)
    config['auth']['method'] = 'ldap'
    config['ldap']['server'] = 'ldap.forumsys.com'
    config['ldap']['port'] = '389'
    config['ldap']['base_dn'] = 'dc=example,dc=com'
    with open(conf_path, 'w') as configfile:
        config.write(configfile)

    username = 'test'
    res = client.post('/login', data={
        'username': username,
        'password': 'password'
    })
    eq_(200, res.status_code)


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


def test_get_index_after_login():
    res = client.get('/')
    eq_(200, res.status_code)


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
