#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from nose.tools import eq_


def test_login_logout():
    driver = webdriver.PhantomJS()
    wait = WebDriverWait(driver, 5)

    driver.get('http://localhost:8080/')
    wait.until(ec.presence_of_all_elements_located)
    print(driver.current_url)
    eq_('http://localhost:8080/login', driver.current_url)

    show_signin = driver.find_element_by_id('showSignIn')
    show_signin.click()

    wait.until(ec.visibility_of_element_located((By.ID, 'username')))
    username = driver.find_element_by_id('username')
    username.send_keys('Admin')

    wait.until(ec.visibility_of_element_located((By.ID, 'password')))
    password = driver.find_element_by_id('password')
    password.send_keys('webtex')

    wait.until(ec.visibility_of_element_located((By.ID, 'signIn')))
    signin = driver.find_element_by_id('signIn')
    signin.click()

    wait.until(ec.presence_of_all_elements_located)
    print(driver.current_url)
    eq_('http://localhost:8080/', driver.current_url)
    logout = driver.find_element_by_id('logout')
    logout.click()

    wait.until(ec.presence_of_all_elements_located)
    print(driver.current_url)
    eq_('http://localhost:8080/login', driver.current_url)
    driver.close()
