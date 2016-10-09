#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import eq_, ok_
import os
from WebTeX import app
import json
from io import BytesIO
from configparser import ConfigParser
import sqlite3
from werkzeug.security import generate_password_hash as gen_pass_hash

app.testing = True
client = app.app.test_client()
webtex_path = os.path.dirname(os.path.abspath(__file__)) + '/../WebTeX/'
conf_path = webtex_path + 'WebTeX.ini'
db_path = webtex_path + 'WebTeX.db'
redpen_conf_path = os.path.expanduser('~/redpen/conf/redpen-conf-en.xml')
java_home = '/usr/lib/jvm/java-8-oracle'


def setup():
    config = ConfigParser()
    config.read(conf_path)
    config['dev']['check_csrf'] = 'false'
    with open(conf_path, 'w') as configfile:
        config.write(configfile)

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


def teardown():
    config = ConfigParser()
    config.read(conf_path)
    config['setup']['initial_setup'] = 'true'
    config['auth']['method'] = 'local'
    config['ldap']['server'] = ''
    config['ldap']['port'] = ''
    config['ldap']['base_dn'] = ''
    config['redpen']['java_home'] = ''
    config['redpen']['conf'] = ''
    config['dev']['check_csrf'] = 'true'
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


def test_login():
    config = ConfigParser()
    config.read(conf_path)
    config['auth']['method'] = 'local'
    f = open(conf_path, 'w')
    config.write(f)
    f.close()

    res = client.post('/login', data={
        'username': 'test-user',
        'password': 'test-pass'
    })
    eq_(302, res.status_code)
    eq_('http://localhost/', res.headers['Location'])


def test_read_directory():
    res = client.post('/readDirectory')
    eq_(200, res.status_code)


def test_set_directory():
    res = client.post('/setDirectory')
    data = json.loads(json.loads(res.data.decode('utf-8'))['ResultSet'])
    eq_(200, res.status_code)
    eq_('Success', data['result'])


def test_read_filelist():
    res = client.post('/readFilelist')
    data = json.loads(json.loads(res.data.decode('utf-8'))['ResultSet'])
    eq_(200, res.status_code)
    eq_('Success', data['result'])


def test_upload_file():
    sample_tex_file_bytes = (
        r'\documentclass{jarticle}''\n'
        r'\begin{document}''\n'
        r'This is sample tex file.''\n'
        r'\end{document}''\n'
    ).encode('utf-8')
    res = client.post(
        '/upload',
        data={
            'file': (BytesIO(sample_tex_file_bytes), 'document.tex')
        })
    data = json.loads(json.loads(res.data.decode('utf-8'))['ResultSet'])
    eq_(200, res.status_code)
    eq_('Success', data['result'])


def test_set_directory_uploaded_tex():
    res = client.post('/setDirectory')
    data = json.loads(json.loads(res.data.decode('utf-8'))['ResultSet'])
    eq_(200, res.status_code)
    eq_('Success', data['result'])
    eq_('True', data['exist'])
    ok_('' != data['text'])


def test_read_filelist_uploaded_tex():
    res = client.post('/readFilelist')
    data = json.loads(json.loads(res.data.decode('utf-8'))['ResultSet'])
    eq_(200, res.status_code)
    eq_('Success', data['result'])
    ok_(len(data['list']) != 0)
    eq_('True', data['tex'])


def test_compile_tex():
    config = ConfigParser()
    config.read(conf_path)
    config['redpen']['conf'] = redpen_conf_path
    config['redpen']['java_home'] = java_home
    with open(conf_path, 'w') as configfile:
        config.write(configfile)
    sample_tex_text = (
        r'\documentclass{jarticle}''\n'
        r'\begin{document}''\n'
        r'This is sample tex file.''\n'
        r'\end{document}''\n'
    )
    res = client.post('/compile',
                      data=json.dumps(dict(text=sample_tex_text)),
                      content_type='application/json')
    data = json.loads(json.loads(res.data.decode('utf-8'))['ResultSet'])
    eq_(200, res.status_code)
    eq_('Success', data['result'])
    print(data['texlog'])
    eq_('True', data['existpdf'])


def test_logout():
    with client.session_transaction() as sess:
        eq_(sess['username'], 'test-user')
    res = client.get('/logout')
    with client.session_transaction() as sess:
        eq_('username' in sess, False)
    eq_(302, res.status_code)
    eq_('http://localhost/login', res.headers['Location'])
