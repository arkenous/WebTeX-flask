#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from nose.tools import eq_
import os
from configparser import ConfigParser
import sqlite3
from werkzeug.security import generate_password_hash as gen_pass_hash

webtex_path = os.path.dirname(os.path.abspath(__file__)) + '/../WebTeX/'
conf_path = webtex_path + 'WebTeX.ini'
db_path = webtex_path + 'WebTeX.db'


def test_login_logout():
    driver = webdriver.PhantomJS()
    wait = WebDriverWait(driver, 5)

    driver.get('http://localhost:8080/')
    wait.until(ec.presence_of_all_elements_located)
    eq_('http://localhost:8080/login', driver.current_url)

    driver.get('http://localhost:8080/initialize')
    wait.until(ec.presence_of_all_elements_located)
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
    eq_('http://localhost:8080/initialize', driver.current_url)

    user_name = driver.find_element_by_id('user-name')
    user_name.send_keys('test-user')
    user_pass = driver.find_element_by_id('user-password')
    user_pass.send_keys('test-pass')

    java_home = driver.find_element_by_id('java_home')
    java_home.send_keys('/usr/lib/jvm/java-8-oracle')

    redpen_path = driver.find_element_by_id('redpen_path')
    redpen_path.send_keys(
        os.path.expanduser('~/redpen/conf/redpen-conf-en.xml'))

    initialize_ok = driver.find_element_by_id('OK')
    initialize_ok.click()
    wait.until(ec.presence_of_all_elements_located)
    eq_('http://localhost:8080/login', driver.current_url)

    show_signin = driver.find_element_by_id('showSignIn')
    show_signin.click()

    wait.until(ec.visibility_of_element_located((By.ID, 'username')))
    username = driver.find_element_by_id('username')
    username.send_keys('test-user')

    wait.until(ec.visibility_of_element_located((By.ID, 'password')))
    password = driver.find_element_by_id('password')
    password.send_keys('test-pass')

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

