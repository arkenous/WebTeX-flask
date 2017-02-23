#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from configparser import ConfigParser
import sqlite3
from werkzeug.security import generate_password_hash as gen_pass_hash

webtex_path = os.path.dirname(os.path.abspath(__file__))
conf_path = webtex_path + '/WebTeX.ini'
db_path = webtex_path + '/WebTeX.db'


def init():
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
    sql = 'DELETE FROM user'
    cur.execute(sql)
    con.commit()
    sql = 'INSERT INTO user VALUES(?,?)'
    cur.execute(sql, ('Admin', gen_pass_hash('webtex')))
    con.commit()
    cur.close()
    con.close()

if __name__ == '__main__':
    init()
