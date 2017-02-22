# WebTeX
[![Build Status](https://travis-ci.org/trileg/WebTeX.svg?branch=master)](https://travis-ci.org/trileg/WebTeX)
[![Code Climate](https://codeclimate.com/github/trileg/WebTeX/badges/gpa.svg)](https://codeclimate.com/github/trileg/WebTeX)
[![Issue Count](https://codeclimate.com/github/trileg/WebTeX/badges/issue_count.svg)](https://codeclimate.com/github/trileg/WebTeX)
[![Test Coverage](https://codeclimate.com/github/trileg/WebTeX/badges/coverage.svg)](https://codeclimate.com/github/trileg/WebTeX/coverage)
[![Dependency Status](https://www.versioneye.com/user/projects/575bb1f57757a00041b3b74b/badge.svg?style=flat)](https://www.versioneye.com/user/projects/575bb1f57757a00041b3b74b)
[![Join the chat at https://gitter.im/trileg/WebTeX](https://badges.gitter.im/trileg/WebTeX.svg)](https://gitter.im/trileg/WebTeX?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![AMA](https://img.shields.io/badge/ask%20me-anything-0e7fc0.svg)](https://github.com/trileg/ama)
[![license](https://img.shields.io/github/license/trileg/WebTeX.svg?maxAge=2592000)](LICENSE)

Web-based LaTeX editor and compiler.
This application use [Flask](https://github.com/mitsuhiko/flask "https://github.com/mitsuhiko/flask").

Docker image of this application is [here](https://github.com/trileg/docker-webtex "https://github.com/trileg/docker-webtex")

## Features
- Edit, compile and preview LaTeX document on the web.
- LDAP authentication support (using [LDAP3](https://github.com/cannatag/ldap3 "https://github.com/cannatag/ldap3")).
- Automatic correction (using [RedPen](https://github.com/redpen-cc/redpen/ "https://github.com/redpen-cc/redpen/")).

Default account is **Admin** and password is **webtex**

## Requirements
- Python 3.x
  - [Flask](https://github.com/mitsuhiko/flask "https://github.com/mitsuhiko/flask")
  - [LDAP3](https://github.com/cannatag/ldap3 "https://github.com/cannatag/ldap3")
- Java
- TeX Live (texlive-lang-cjk)
  - This application use `platex` to compile LaTeX document.
- [RedPen](https://github.com/redpen-cc/redpen/ "https://github.com/redpen-cc/redpen/")
- [Ace](https://github.com/ajaxorg/ace-builds "https://github.com/ajaxorg/ace-builds")
  - Placement path: `static/ace-builds/src-noconflict/`
- pdftotext (poppler-utils)

## Setup

1. Download and extract this project

2. Install `texlive-lang-cjk (or texlive-langcjk)`, `openjdk-7-jre (or jre7-openjdk)`, `poppler`

3. Install Python3 modules using pip: `pip install -r pip-requirements.txt`

4. Install Ace.js

   ```
   $ wget https://github.com/ajaxorg/ace-builds/archive/v1.2.5.tar.gz -O /tmp/ace.tar.gz
   $ mkdir /tmp/ace-builds
   $ tar -xvf /tmp/ace.tar.gz -C /tmp/ace-builds --strip-components 1
   $ mkdir WebTeX/static/ace-builds
   $ mv /tmp/ace-builds/src-noconflict WebTeX/static/ace-builds/
   $ rm -f /tmp/ace.tar.gz && rm -rf /tmp/ace-builds
   ```

5. Install RedPen

   ```
   $ wget https://github.com/redpen-cc/redpen/releases/download/redpen-1.7.4/redpen-1.7.4.tar.gz -O /tmp/redpen.tar.gz
   $ mkdir redpen
   $ tar -xvf /tmp/redpen.tar.gz -C redpen --strip-components 1
   $ export PATH=$PATH:$PWD/redpen/bin
   $ rm -f /tmp/redpen.tar.gz
   ```

6. Run this application

   ```
   $ python WebTeX/app.py
   ```


## Author

[Kensuke Kosaka](https://github.com/trileg "https://github.com/trileg")
