#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import eq_
import WebTeX

WebTeX.app.testing = True
client = WebTeX.app.test_client()


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


def test_login():
    res = client.post('/login', data={
        'username': 'Admin',
        'password': 'webtex'
    })
    eq_(302, res.status_code)
    eq_('http://localhost/', res.headers['Location'])


def test_logout():
    with client.session_transaction() as sess:
        eq_(sess['username'], 'Admin')
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
