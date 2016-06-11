# WebTeX
[![Build Status](https://travis-ci.org/trileg/WebTeX.svg?branch=master)](https://travis-ci.org/trileg/WebTeX)
[![Code Climate](https://codeclimate.com/github/trileg/WebTeX/badges/gpa.svg)](https://codeclimate.com/github/trileg/WebTeX)
[![Test Coverage](https://codeclimate.com/github/trileg/WebTeX/badges/coverage.svg)](https://codeclimate.com/github/trileg/WebTeX/coverage)
[![Dependency Status](https://www.versioneye.com/user/projects/575bb1f57757a00041b3b74b/badge.svg?style=flat)](https://www.versioneye.com/user/projects/575bb1f57757a00041b3b74b)
[![Join the chat at https://gitter.im/trileg/WebTeX](https://badges.gitter.im/trileg/WebTeX.svg)](https://gitter.im/trileg/WebTeX?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![AMA](https://img.shields.io/badge/ask%20me-anything-0e7fc0.svg)](https://github.com/trileg/ama)

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
- TeX Live (texlive-lang-cjk)
  - This application use `platex` to compile LaTeX document.
- [RedPen](https://github.com/redpen-cc/redpen/ "https://github.com/redpen-cc/redpen/")
- [Ace](https://github.com/ajaxorg/ace-builds "https://github.com/ajaxorg/ace-builds")
  - Placement path: `static/ace-builds/src-noconflict/`

## Author
[Kensuke Kosaka](https://github.com/trileg "https://github.com/trileg")
