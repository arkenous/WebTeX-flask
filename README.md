# WebTeX

[![Join the chat at https://gitter.im/trileg/WebTeX](https://badges.gitter.im/trileg/WebTeX.svg)](https://gitter.im/trileg/WebTeX?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/trileg/WebTeX.svg?branch=master)](https://travis-ci.org/trileg/WebTeX)
[![Coverage Status](https://coveralls.io/repos/github/trileg/WebTeX/badge.svg?branch=master)](https://coveralls.io/github/trileg/WebTeX?branch=master)

Web-based LaTeX editor and compiler.
This application using [Flask](https://github.com/mitsuhiko/flask "https://github.com/mitsuhiko/flask").

## Features
- Edit, compile and preview LaTeX document on the web
- LDAP authentication support (using [LDAP3](https://github.com/cannatag/ldap3 "https://github.com/cannatag/ldap3"))
- Automatic correction (using [RedPen](https://github.com/redpen-cc/redpen/ "https://github.com/redpen-cc/redpen/"))

Default account is **Admin** and password is **webtex**

## Requirements
- Python 3.x
  - [Flask](https://github.com/mitsuhiko/flask "https://github.com/mitsuhiko/flask")
  - [LDAP3](https://github.com/cannatag/ldap3 "https://github.com/cannatag/ldap3")
- TeX Live (texlive-lang-cjk)
- [RedPen](https://github.com/redpen-cc/redpen/ "https://github.com/redpen-cc/redpen/")
- [Ace](https://github.com/ajaxorg/ace "https://github.com/ajaxorg/ace")

## Author
[Kensuke Kosaka](https://github.com/trileg "https://github.com/trileg")