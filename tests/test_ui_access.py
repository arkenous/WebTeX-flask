#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from nose.tools import eq_


def test_login_logout():
    driver = webdriver.PhantomJS()
    driver.get('http://localhost:8080/')
    print(driver.current_url)
    eq_('http://localhost:8080/login', driver.current_url)
    show_signin = driver.find_element_by_id('showSignIn')
    show_signin.click()
    username = driver.find_element_by_id('username')
    username.send_keys('Admin')
    password = driver.find_element_by_id('password')
    password.send_keys('webtex')
    signin = driver.find_element_by_id('signIn')
    signin.click()
    print(driver.current_url)
    eq_('http://localhost:8080/', driver.current_url)
    logout = driver.find_element_by_id('logout')
    logout.click()
    print(driver.current_url)
    eq_('http://localhost:8080/login', driver.current_url)
    driver.close()
