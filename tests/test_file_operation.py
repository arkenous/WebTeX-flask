#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import eq_, ok_
import os
from WebTeX import app
import json
from io import BytesIO
from configparser import ConfigParser

app.testing = True
client = app.app.test_client()
webtex_path = os.path.dirname(os.path.abspath(__file__)) + '/../WebTeX/'
conf_path = webtex_path + 'WebTeX.ini'
redpen_conf_path = os.path.expanduser('~/redpen/conf/redpen-conf-en.xml')
java_home = '/usr/lib/jvm/java-8-oracle'


def setup():
    conf_dict = {'mode': 'local', 'ldap_address': '', 'ldap_port': '',
                 'ldap_basedn': '', 'java_home': '/usr/lib/jvm/java-8-oracle',
                 'redpen_conf_path': os.path.expanduser(
                     '~/redpen/conf/redpen-conf-en.xml')}
    res = client.post('/saveConfig',
                      data=json.dumps(conf_dict),
                      content_type='application/json')
    eq_('http://localhost/login', res.headers['Location'])


def teardown():
    config = ConfigParser()
    config.read(conf_path)
    config['setup']['initial_setup'] = 'true'
    with open(conf_path, 'w') as configfile:
        config.write(configfile)

    res = client.get('/')
    eq_(302, res.status_code)
    eq_('http://localhost/initialize', res.headers['Location'])

    res = client.get('/login')
    eq_(302, res.status_code)
    eq_('http://localhost/initialize', res.headers['Location'])

    res = client.get('/initialize')
    eq_(200, res.status_code)
    eq_('http://localhost/initialize', res.headers['Location'])


def test_login():
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


def test_initial_read_directory():
    res = client.post('/readDirectory')
    data = json.loads(json.loads(res.data.decode('utf-8'))['ResultSet'])
    eq_(200, res.status_code)
    eq_('', data['name'])


def test_create_directory():
    res = client.post('/createDirectory',
                      data=json.dumps(dict(name='test')),
                      content_type='application/json')
    eq_(200, res.status_code)


def test_read_directory():
    res = client.post('/readDirectory')
    data = json.loads(json.loads(res.data.decode('utf-8'))['ResultSet'])
    eq_(200, res.status_code)
    eq_('test', data['name'][0])


def test_set_directory():
    res = client.post('/setDirectory',
                      data=json.dumps(dict(name='test')),
                      content_type='application/json')
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
    res = client.post('/setDirectory',
                      data=json.dumps(dict(name='test')),
                      content_type='application/json')
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
        eq_(sess['username'], 'Admin')
    res = client.get('/logout')
    with client.session_transaction() as sess:
        eq_(sess, {})
    eq_(302, res.status_code)
    eq_('http://localhost/login', res.headers['Location'])
