#!/usr/bin/env python
# coding=utf8

################################################################################
import os
from flask import Flask, request, jsonify
from flask_login import LoginManager
from flask_login import login_user, logout_user, current_user, login_required
# from OpenSSL import SSL

################################################################################
app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)


################################################################################
class User:
    # ==========================================================================
    def __init__(self, user_id, email=None, passwd_hash=None,
                 authenticated=False):
        self.user_id = user_id
        self.email = email
        self.passwd_hash = passwd_hash
        self.authenticated = authenticated

    # ==========================================================================
    def __repr__(self):
        r = {
            'user_id': self.user_id,
            'email': self.email,
            'passwd_hash': self.passwd_hash,
            'authenticated': self.authenticated,
        }
        return str(r)

    # ==========================================================================
    def can_login(self, passwd_hash):
        return self.passwd_hash == passwd_hash

    # ==========================================================================
    def is_active(self):
        return True

    # ==========================================================================
    def get_id(self):
        return self.user_id

    # ==========================================================================
    def is_authenticated(self):
        return self.authenticated

    # ==========================================================================
    def is_anonymous(self):
        return False

################################################################################
USERS = {
    "user01": User("user01", passwd_hash='user_01'),
    "user02": User("user02", passwd_hash='user_02'),
    "user03": User("user03", passwd_hash='user_03'),
}


################################################################################
@login_manager.user_loader
def user_loader(user_id):
    return USERS[user_id]


################################################################################
@app.route("/api/auth_func", methods=['POST'])
@login_required
def auth_func():
    user = current_user
    json_res = {'ok': True, 'msg': 'auth_func(%s),user_id=%s'
                                   % (request.json, user.user_id)}
    return jsonify(json_res)


################################################################################
@app.route("/api/notauth_func", methods=['POST'])
def notauth_func():
    json_res = {'ok': True, 'msg': 'notauth_func(%s)'
                                   % request.json}
    return jsonify(json_res)


################################################################################
@app.route("/api/add_user", methods=['POST'])
def addUser():
    user_id = request.json['user_id']
    passwd_hash = request.json['passwd_hash']
    if user_id in USERS:
        json_res = {'ok': False, 'error': 'user <%s> already exists' % user_id}
    else:
        user = User(user_id, passwd_hash)
        USERS[user_id] = user
        json_res = {'ok': True, 'msg': 'user <%s> added' % user_id}
    return jsonify(json_res)


################################################################################
@app.route('/api/login', methods=['POST'])
def login():
    user_id = request.json['user_id']
    passwd_hash = request.json['passwd_hash']
    if user_id not in USERS:
        json_res={'ok': False, 'error': 'Invalid user_id or password'}
    elif not USERS[user_id].can_login(passwd_hash):
        json_res = {'ok': False, 'error': 'Invalid user_id or password'}
    else:
        json_res={'ok': True, 'msg': 'user <%s> logined' % user_id}
        USERS[user_id].authenticated = True
        login_user(USERS[user_id], remember=True)
    return jsonify(json_res)


################################################################################
@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    json_res = {'ok': True, 'msg': 'user <%s> logout' % user.user_id}
    logout_user()
    return jsonify(json_res)


################################################################################
if __name__ == "__main__":
    # context = SSL.Context(SSL.SSLv3_METHOD)
    # context.use_privatekey_file('appauth.key')
    # context.use_certificate_file('appauth.crt')
    # if AttributeError: 'Context' object has no attribute 'wrap_socket'
    context = ('appauth.crt', 'appauth.key')
    app.run(host='0.0.0.0',port=5000,
            ssl_context=context,
            debug=True)
