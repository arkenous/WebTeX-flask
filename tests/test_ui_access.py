#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from nose.tools import eq_


def test_get_index():
    driver = webdriver.PhantomJS()
    driver.get('http://localhost:8080/')
    eq_('http://localhost:8080/login', driver.current_url)
    driver.close()
