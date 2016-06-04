#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import eq_, ok_, with_setup
from WebTeX import app
import os
import json
from configparser import ConfigParser
import random
import sqlite3
from werkzeug.security import generate_password_hash as gen_pass_hash

app.testing = True
client = app.app.test_client()
webtex_path = os.path.dirname(os.path.abspath(__file__)) + '/../WebTeX/'
conf_path = webtex_path + 'WebTeX.ini'
db_path = webtex_path + 'WebTeX.db'
ldap_userlist = ['riemann', 'gauss', 'euler', 'euclid',
                 'einstein', 'newton', 'galieleo', 'tesla']


def setup():
    res = client.post('/login', data={
        'username': 'Admin',
        'password': 'webtex'
    })
    eq_(302, res.status_code)
    eq_('http://localhost/initialize', res.headers['Location'])

    conf_dict = {'user_name': 'test-user', 'user_password': 'test-pass',
                 'mode': 'local', 'ldap_address': '', 'ldap_port': '',
                 'ldap_basedn': '', 'java_home': '/usr/lib/jvm/java-8-oracle',
                 'redpen_conf_path': os.path.expanduser(
                     '~/redpen/conf/redpen-conf-en.xml')}
    client.post('/saveConfig',
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

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    sql = 'UPDATE user SET username=(?), password=(?) WHERE username=(?)'
    cur.execute(sql, ('Admin', gen_pass_hash('webtex'), 'test-user',))
    con.commit()
    cur.close()
    con.close()

    res = client.get('/')
    eq_(302, res.status_code)
    eq_('http://localhost/login', res.headers['Location'])

    res = client.get('/initialize')
    eq_(302, res.status_code)
    eq_('http://localhost/login', res.headers['Location'])

    res = client.get('/login')
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


def test_get_initialize_before_login():
    res = client.get('/initialize')
    eq_(302, res.status_code)
    eq_('http://localhost/login', res.headers['Location'])


@with_setup(change_initial_setup_to_true, change_initial_setup_to_false)
def test_initialize():
    res = client.post('/login', data={
        'username': 'test-user',
        'password': 'test-pass'
    })
    eq_(302, res.status_code)
    eq_('http://localhost/initialize', res.headers['Location'])

    conf_dict = {'user_name': 'test-user', 'user_password': 'test-pass',
                 'mode': 'local', 'ldap_address': '', 'ldap_port': '',
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
        'username': 'Admin',
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
        'username': 'test-user',
        'password': 'test-pass'
    })
    eq_(302, res.status_code)
    eq_('http://localhost/', res.headers['Location'])


def test_logout_local():
    with client.session_transaction() as sess:
        eq_(sess['username'], 'test-user')
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
