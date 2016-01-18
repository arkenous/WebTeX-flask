#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import json
import sqlite3
import subprocess

import os
from flask import Flask, render_template, session, request, redirect, jsonify
from ldap3 import Server, Connection, AUTH_SIMPLE, STRATEGY_SYNC, GET_ALL_INFO, LDAPBindError
from werkzeug import utils
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = os.urandom(24)

base = os.path.dirname(os.path.abspath(__file__))


@app.before_request
def before_request():
    if session.get('username') is not None:
        return
    if request.path == '/login':
        return
    return redirect('/login')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and is_account_valid():
        session['username'] = request.form['username']
        return redirect('/')
    return render_template('login.html')


def is_account_valid():
    username = request.form['username']
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.abspath(__file__)) + '/auth.ini')

    if config['auth']['method'] == 'ldap':
        server = config['ldap']['server']
        port = int(config['ldap']['port'])
        base_dn = config['ldap']['base_dn']
        user_dn = 'uid=' + username + ',' + base_dn

        s = Server(server, port=port, get_info=GET_ALL_INFO)
        try:
            Connection(s, auto_bind=True, client_strategy=STRATEGY_SYNC, user=user_dn,
                       password=request.form['password'], authentication=AUTH_SIMPLE, check_names=True)
            return True
        except LDAPBindError:
            return False
    elif config['auth']['method'] == 'normal':
        con = sqlite3.connect(os.path.dirname(os.path.abspath(__file__)) + '/WebTeX.db')
        cur = con.cursor()
        cur.execute('SELECT password FROM user WHERE username=(?)', (username,))
        fetched = cur.fetchone()
        if fetched is None:
            return False
        hashedpass = fetched[0]
        if check_password_hash(hashedpass, request.form['password']):
            return True
        else:
            return False


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


@app.route('/readDirectory', methods=['POST'])
def read_directory():
    storage_path = base+'/static/storage'
    if not os.path.exists(storage_path) or not os.path.isdir(storage_path):
        os.mkdir(storage_path)

    user_dirpath = storage_path+'/'+session.get('username')
    if os.path.exists(user_dirpath) and os.path.isdir(user_dirpath):
        directory_list = os.listdir(user_dirpath)
        dictionary = {'name': directory_list}
        return jsonify(ResultSet=json.dumps(dictionary))
    else:
        os.mkdir(user_dirpath)
        dictionary = {'name': ''}
        return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/createDirectory', methods=['POST'])
def create_directory():
    dir_path = base + '/static/storage/' + session.get('username') + '/' + request.json['name']
    os.mkdir(dir_path)
    return jsonify()


@app.route('/setDirectory', methods=['POST'])
def set_directory():
    session['cwd'] = base + '/static/storage/' + session.get('username') + '/' + request.json['name']
    os.chdir(session.get('cwd'))
    if os.path.exists(session.get('cwd')) and os.path.isdir(session.get('cwd')):
        # if document.tex exist, read it.
        if os.path.exists(session.get('cwd') + '/document.tex'):
            text = open(session.get('cwd') + '/document.tex').read()
            dictionary = {'result': 'Success', 'exist': 'True', 'text': text}
            return jsonify(ResultSet=json.dumps(dictionary))
        else:
            dictionary = {'result': 'Success', 'exist': 'False'}
            return jsonify(ResultSet=json.dumps(dictionary))
    else:
        session['cwd'] = ''
        dictionary = {'result': 'Failure'}
        return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/readFilelist', methods=['POST'])
def read_filelist():
    if session.get('cwd') == '':
        dictionary = {'result': 'Failure'}
        return jsonify(ResultSet=json.dumps(dictionary))
    filelist = os.listdir(session.get('cwd'))
    username = session.get('username')
    if os.path.exists(os.path.join(session.get('cwd'), 'document.tex')):
        if os.path.exists(os.path.join(session.get('cwd'), 'document.pdf')):
            dictionary = {'result': 'Success', 'list': filelist, 'username': username, 'tex': 'True', 'pdf': 'True'}
        else:
            dictionary = {'result': 'Success', 'list': filelist, 'username': username, 'tex': 'True', 'pdf': 'False'}
    else:
        dictionary = {'result': 'Success', 'list': filelist, 'username': username, 'tex': 'False', 'pdf': 'False'}

    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/upload', methods=['POST'])
def upload_file():
    if session.get('cwd') != '':
        file = request.files['file']
        if file:
            filename = utils.secure_filename(file.filename)
            file.save(os.path.join(session.get('cwd'), filename))
            dictionary = {'result': 'Success'}
        else:
            dictionary = {'result': 'Failure'}
    else:
        dictionary = {'result': 'Failure'}

    return jsonify(ResultSet=json.dumps(dictionary))


@app.route('/compile', methods=['POST'])
def compile_tex():
    if session.get('cwd') == '':
        dictionary = {'result': 'Failure'}
        return jsonify(ResultSet=json.dumps(dictionary))
    text = request.json['text']
    os.chdir(session.get('cwd'))
    f = open('document.tex', 'w')
    f.write(text)
    f.close()

    texlog = subprocess.check_output(['platex', '-halt-on-error', '-interaction=nonstopmode', '-file-line-error',
                                      '-no-shell-escape', 'document.tex', '&&', 'dvipdfmx',
                                      'document.dvi']).splitlines()
    if os.path.exists('document.pdf'):
        config = configparser.ConfigParser()
        config.read('redpen.ini')
        os.environ['JAVA_HOME'] = config['redpen']['JAVA_HOME']
        subprocess.call(['pdftotext', 'document.pdf', 'document.txt'])
        redpen = subprocess.Popen(['redpen', '-c', config['redpen']['conf'], 'document.txt'], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE).communicate()
        redpenout = redpen[0].splitlines()
        redpenerr = redpen[1].splitlines()

        dictionary = {'result': 'Success', 'redpenout': redpenout, 'redpenerr': redpenerr, 'texlog': texlog,
                      'existpdf': 'True', 'user': session.get('username')}
    else:
        dictionary = {'result': 'Success', 'texlog': texlog, 'existpdf': 'False'}

    return jsonify(ResultSet=json.dumps(dictionary))


if __name__ == '__main__':
    app.run(host='localhost', port=8080, threaded=True)
