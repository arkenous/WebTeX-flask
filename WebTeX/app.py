#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import json
import sqlite3
import subprocess

import os
from base64 import b64encode
from flask import Flask, render_template, session, request, redirect, \
    jsonify, abort
from ldap3 import Server, Connection, \
    AUTH_SIMPLE, STRATEGY_SYNC, GET_ALL_INFO, LDAPBindError
from werkzeug import utils
from werkzeug.security import generate_password_hash as generate, \
    check_password_hash as check

app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = os.urandom(24)

base = os.path.dirname(os.path.abspath(__file__))
conf = base + '/WebTeX.ini'
db = base + '/WebTeX.db'
storage = base + '/static/storage/'


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = b64encode(os.urandom(32)).decode('utf-8')
    return session['_csrf_token']
app.jinja_env.globals['csrf_token'] = generate_csrf_token


def check_csrf(request_):
    config = configparser.ConfigParser()
    config.read(conf)
    if config['dev']['check_csrf'] == 'true':
        token = session['_csrf_token']
        if not token or token != request_.json['_csrf_token']:
            return False
    return True


@app.before_request
def before_request():
    if 'username' not in session and request.path != '/login':
        return redirect('/login')
    elif 'username' not in session and request.path == '/login':
        return

    config = configparser.ConfigParser()
    config.read(conf)
    initial_setup = config['setup']['initial_setup']
    initial_setup_path = ['/initialize', '/readConfig', '/saveConfig']
    only_initial_setup = ['/initialize', '/saveConfig']
    if initial_setup == 'true' and request.path not in initial_setup_path:
        return redirect('/initialize')
    if initial_setup == 'false' and request.path in only_initial_setup:
        return redirect('/logout')

    return


@app.route('/initialize', methods=['GET'])
def initialize():
    return render_template('initialize.html')


@app.route('/readConfig', methods=['POST'])
def read_config():
    if not check_csrf(request):
        abort(403)

    dictionary = {}
    config = configparser.ConfigParser()
    config.read(conf)
    dictionary['mode'] = config['auth']['method']
    dictionary['ldap_address'] = config['ldap']['server']
    dictionary['ldap_port'] = config['ldap']['port']
    dictionary['ldap_basedn'] = config['ldap']['base_dn']
    dictionary['java_home'] = config['redpen']['java_home']
    dictionary['redpen_conf_path'] = config['redpen']['conf']
    dictionary['result'] = 'Success'
    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/saveConfig', methods=['POST'])
def save_config():
    if not check_csrf(request):
        abort(403)

    dictionary = {}

    user_name = utils.secure_filename(request.json['user_name'])
    user_password = request.json['user_password']

    config = configparser.ConfigParser()
    config.read(conf)
    config['setup']['initial_setup'] = 'false'
    config['auth']['method'] = request.json['mode']
    config['ldap']['server'] = request.json['ldap_address']
    config['ldap']['port'] = request.json['ldap_port']
    config['ldap']['base_dn'] = request.json['ldap_basedn']
    config['redpen']['java_home'] = request.json['java_home']
    config['redpen']['conf'] = request.json['redpen_conf_path']
    f = open(conf, 'w')
    config.write(f)
    f.close()

    con = sqlite3.connect(db)
    cur = con.cursor()
    sql = 'UPDATE user SET username=(?), password=(?) WHERE username="Admin"'
    cur.execute(sql, (user_name, generate(user_password),))
    con.commit()
    cur.close()
    con.close()

    session.pop('username', None)
    session.pop('cwd', None)

    dictionary['result'] = 'Success'
    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/preference')
def preference():
    return render_template('preference.html')


@app.route('/registerUser', methods=['POST'])
def register_user():
    dictionary = {}

    username = request.json['username']
    password = request.json['password']

    con = sqlite3.connect(db)
    cur = con.cursor()
    sql = 'SELECT username FROM user WHERE username=(?)'
    cur.execute(sql, (username,))
    fetched = cur.fetchone()
    if fetched is not None:
        dictionary['result'] = 'Failure'
        dictionary['cause'] = 'Your specified user is already exists.'
        return jsonify(ResultSet=json.dumps(dictionary))

    sql = 'INSERT INTO user(username, password) VALUES (?, ?)'
    cur.execute(sql, (username, generate(password),))
    con.commit()
    cur.close()
    con.close()

    dictionary['result'] = 'Success'
    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/configureLdap', methods=['POST'])
def configure_ldap():
    dictionary = {}

    config = configparser.ConfigParser()
    config.read(conf)
    config['ldap']['server'] = request.json['ldap_address']
    config['ldap']['port'] = request.json['ldap_port']
    config['ldap']['base_dn'] = request.json['ldap_basedn']
    f = open(conf, 'w')
    config.write(f)
    f.close()

    dictionary['result'] = 'Success'
    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/changePath', methods=['POST'])
def change_path():
    dictionary = {}

    config = configparser.ConfigParser()
    config.read(conf)
    config['redpen']['java_home'] = request.json['java_home']
    config['redpen']['conf'] = request.json['redpen_path']
    f = open(conf, 'w')
    config.write(f)
    f.close()

    dictionary['result'] = 'Success'
    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and is_account_valid():
        session['username'] = request.form['username']
        config = configparser.ConfigParser()
        config.read(conf)
        initial_setup = config['setup']['initial_setup']
        if initial_setup == 'true':
            return redirect('/initialize')
        return redirect('/')
    return render_template('login.html')


def is_account_valid():
    username = request.form['username']
    config = configparser.ConfigParser()
    config.read(conf)

    if config['auth']['method'] == 'ldap':
        server = config['ldap']['server']
        port = int(config['ldap']['port'])
        base_dn = config['ldap']['base_dn']
        user_dn = 'uid=' + username + ',' + base_dn

        s = Server(server, port=port, get_info=GET_ALL_INFO)
        try:
            Connection(s, auto_bind=True, client_strategy=STRATEGY_SYNC,
                       user=user_dn, password=request.form['password'],
                       authentication=AUTH_SIMPLE, check_names=True)
            return True
        except LDAPBindError:
            return False
    if config['auth']['method'] == 'local':
        con = sqlite3.connect(db)
        cur = con.cursor()
        sql = 'SELECT password FROM user WHERE username=(?)'
        cur.execute(sql, (username,))
        fetched = cur.fetchone()
        if fetched is not None and check(fetched[0], request.form['password']):
            return True

    return False


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('cwd', None)
    return redirect('/login')


@app.route('/readDirectory', methods=['POST'])
def read_directory():
    dictionary = {}
    if not os.path.exists(storage) or not os.path.isdir(storage):
        os.mkdir(storage)

    user_storage = storage + session['username']
    if os.path.exists(user_storage) and os.path.isdir(user_storage):
        dictionary['name'] = os.listdir(user_storage)
    else:
        os.mkdir(user_storage)
        dictionary['name'] = ''

    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/createDirectory', methods=['POST'])
def create_directory():
    os.mkdir(storage + session['username'] + '/' + request.json['name'])
    return jsonify()


@app.route('/setDirectory', methods=['POST'])
def set_directory():
    dictionary = {}
    session['cwd'] = storage + session['username'] + '/' + request.json['name']
    os.chdir(session.get('cwd'))
    if os.path.exists(session['cwd']) and os.path.isdir(session['cwd']):
        dictionary['result'] = 'Success'
        # if document.tex exist, read it.
        if os.path.exists(session['cwd'] + '/document.tex'):
            text = open(session['cwd'] + '/document.tex').read()
            dictionary['exist'] = 'True'
            dictionary['text'] = text
        else:
            dictionary['exist'] = 'False'
    else:
        session['cwd'] = ''
        dictionary = {'result': 'Failure'}

    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/readFilelist', methods=['POST'])
def read_filelist():
    dictionary = {}
    if session.get('cwd') == '' or session.get('cwd') is None:
        dictionary['result'] = 'Failure'
    else:
        dictionary['result'] = 'Success'
        dictionary['list'] = os.listdir(session['cwd'])
        dictionary['username'] = session['username']
        if os.path.exists(os.path.join(session['cwd'], 'document.tex')):
            dictionary['tex'] = 'True'
            if os.path.exists(os.path.join(session['cwd'], 'document.pdf')):
                dictionary['pdf'] = 'True'
            else:
                dictionary['pdf'] = 'False'
        else:
            dictionary['tex'] = 'False'

    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/upload', methods=['POST'])
def upload_file():
    dictionary = {}
    if session.get('cwd') == '' or session.get('cwd') is None:
        dictionary['result'] = 'Failure'
    else:
        file = request.files['file']
        if file:
            filename = utils.secure_filename(file.filename)
            file.save(os.path.join(session.get('cwd'), filename))
            dictionary['result'] = 'Success'
        else:
            dictionary['result'] = 'Failure'

    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/compile', methods=['POST'])
def compile_tex():
    dictionary = {}
    if session.get('cwd') == '' or session.get('cwd') is None:
        dictionary['result'] = 'Failure'
    else:
        dictionary['result'] = 'Success'
        text = request.json['text']
        os.chdir(session['cwd'])
        f = open('document.tex', 'w')
        f.write(text)
        f.close()

        dictionary['texlog'] = subprocess.check_output(
            ['platex', '-halt-on-error', '-interaction=nonstopmode',
             '-file-line-error', '-no-shell-escape', 'document.tex'
             ]).decode('utf-8').splitlines()
        subprocess.check_output(
            ['dvipdfmx', 'document.dvi']).decode('utf-8').splitlines()
        if os.path.exists('document.pdf'):
            dictionary['existpdf'] = 'True'
            dictionary['user'] = session['username']
            config = configparser.ConfigParser()
            config.read(conf)
            os.environ['JAVA_HOME'] = config['redpen']['java_home']
            subprocess.call(['pdftotext', 'document.pdf', 'document.txt'])
            redpen = subprocess.Popen(
                ['redpen', '-c', config['redpen']['conf'], 'document.txt'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).communicate()
            dictionary['redpenout'] = redpen[0].decode('utf-8').splitlines()
            dictionary['redpenerr'] = redpen[1].decode('utf-8').splitlines()
        else:
            dictionary['existpdf'] = 'False'

    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/correct', methods=['POST'])
def correct_doc():
    dictionary = {}
    text = request.json['text']
    config = configparser.ConfigParser()
    config.read(conf)
    os.environ['JAVA_HOME'] = config['redpen']['java_home']
    redpen_config_detail = subprocess.check_output(
        ['cat', config['redpen']['conf']]
    ).decode('utf-8')
    redpen_document = "document='"+text+"'"
    redpen_config = "config='"+redpen_config_detail+"'"
    redpen = subprocess.Popen(
        ['curl', '--data', redpen_document, '--data', 'lang=ja', '--data',
         'format=PLAIN2', '--data', redpen_config,
         '127.0.0.1:8080/rest/document/validate/'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ).communicate()
    dictionary['redpenout'] = redpen[0].decode('utf-8').splitlines()
    dictionary['redpenerr'] = redpen[1].decode('utf-8').splitlines()

    return jsonify(ResultSet=json.dumps(dictionary))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
