#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from nose.tools import eq_


def test_login_logout():
    driver = webdriver.PhantomJS()
    driver.get('http://localhost:8080/')
    print(driver.current_url)
    eq_('http://localhost:8080/login', driver.current_url)
    driver.find_element_by_id('showSignIn').click()
    driver.find_element_by_id('username').send_keys('Admin')
    driver.find_element_by_id('password').send_keys('webtex')
    driver.find_element_by_id('signIn').click()
    print(driver.current_url)
    eq_('http://localhost:8080/', driver.current_url)
    driver.find_element_by_id('logout').click()
    print(driver.current_url)
    eq_('http://localhost:8080/login', driver.current_url)
    driver.close()
