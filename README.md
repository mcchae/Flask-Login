# Flask-Login 예제

## 동기

Flask에서 RESTful API 등을 간단하게 작성하고 나서, 해당 API 가 각 세션별로 login 및 logout 되기 전에 호출되는 각 함수들이 보호되어야할 필요가 있습니다. 이런 작업을 도와주는 역할로써 [Flask-Login](https://flask-login.readthedocs.io/en/latest/) 이라는 모듈이 존재합니다.

바로 사용해 볼 만한 샘플이 존재하지 않아 며칠 삽질을 했고 그 결과를 공유합니다.
또한 HTTPS 통신을 통해 채널 보안도 했습니다.
Users 관련 작업을 더 하거나 OAuth2 등과 연동을 하는 등의 약간만 더 손질을 보면 Production에도 충분히 사용할 만 할 것입니다.

## requirements.txt

``` text
Flask==0.11.1
Flask-RESTful==0.3.5
Flask-Login==0.4.0
Flask-API==0.6.9
pyOpenSSL==16.2.0
requests==2.11.1
```
위와 같은 모듈 의존성을 만족하면 됩니다.

시작할 때

```bash
pip install -r requirements.txt
```
라고 실행시키면 됩니다.
> 주의: VirtualEnv 가 아니면 앞에 sudo 를 붙입니다.


## appauth.py (서버쪽 Flask 실행 프로그램)


### 시작하며

우선 시작할 때,

```python
################################################################################
app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)
```
라고 선언해 줍니다.

```python
app.secret_key = os.urandom(24)
```
코드는 사용자 세션 관리를 할 때 필요한 정보입니다.

```python
login_manager = LoginManager()
login_manager.init_app(app)
```
`login_manager`는 Flask-Login 에서 가져온 것으로 필요한 코드입니다.

### 사용자 User 클래스 정의

```python
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
```

`User` 라는 사용자 정의 클래스를 만들어 사용합니다. User-Login에 user 에서 미리 정의된 스펙에 따라 위에 내용에서 더 추가할 수 있습니다.

### 글로벌 사용자 정보

```python
################################################################################
USERS = {
    "user01": User("user01", passwd_hash='user_01'),
    "user02": User("user02", passwd_hash='user_02'),
    "user03": User("user03", passwd_hash='user_03'),
}
```
글로벌로 위와 같이 해쉬로 가지고 있는데 간단하게 /etc/passwd 와 유사한 방법으로 관리할 수 있겠습니다.

### 로그인 객체 가져오기

```python
################################################################################
@login_manager.user_loader
def user_loader(user_id):
    return USERS[user_id]
```
이 정보는 해당 `user_id`로 해당 사용자 객체를 가져오는 코드로 login_manager에 의해 불려지는 코드를 정의합니다.

### 인증하기를 원하는 함수

```python
################################################################################
@app.route("/api/auth_func", methods=['POST'])
@login_required
def auth_func():
    user = current_user
    json_res = {'ok': True, 'msg': 'auth_func(%s),user_id=%s'
                                   % (request.json, user.user_id)}
    return jsonify(json_res)
```
위와 같이 인증을 원하는 함수 위에 `@login_required`라는 데코레이터만 줍니다.
또한 `current_user`라는 login_manager에서 가지고 있는 글로벌에 따라 현재 사용자(`User` 객체)를 구해와서 사용 가능합니다. 패러미터 중 `methods`는 `POST`만 가능하다고 지정합니다.

만약 로그인을 하지 않고 본 함수를 호출하면  HTTP 리턴 코드 `401` 인 `인증 오류`가 발생합니다.

### 인증을 요하지 않는 함수

```python
################################################################################
@app.route("/api/notauth_func", methods=['POST'])
def notauth_func():
    json_res = {'ok': True, 'msg': 'notauth_func(%s)'
                                   % request.json}
    return jsonify(json_res)
```

`@login_required`라는 데코레이터만 없으면 됩니다. 또한 current_user 라는 글로벌 접근을 할 수 없습니다. (접근을 할 수는 있지만 `User` 인스턴스가 아닌 디폴트 `MixedIn.AnonymousUser` 인스턴스 입니다.

### 로그인 함수

```python

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
```

주의할 것은 

```python
        login_user(USERS[user_id], remember=True)
```
라고 호출하여 User 인스턴스를 current_user에 등록한다는 것입니다.

### 로그아웃 함수

```python
################################################################################
@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    json_res = {'ok': True, 'msg': 'user <%s> logout' % user.user_id}
    logout_user()
    return jsonify(json_res)
```


```python
    logout_user()
```

위와 같이 logout_user() 라고 호출하여 login_manager에게 해당 세션의 사용자를 로그아웃하겠다고 알려줍니다.


위와 같이 간단한 Flask 이용 함수 인증을 하는 서버를 만들 수 있습니다.

## appauth_test.py (Requests를 이용한 클라이언트)

UnitTest로 로그인을 하지 않거나 또는 로그인 후 인증 / 비인증 함수 호출을 하고 그 결과가 맞는가를 확인하는 프로그램입니다.

클라이언트를 돌리면

```sh
test0000_init (__main__.TU) ... ok
test0080_notauth_api_call (__main__.TU) ... {'msg': "notauth_func({'param11': 'param-04', 'param10': 'param-03'})", 'ok': True}
ok
test0100_auth_api_call (__main__.TU) ... ok
test0200_login (__main__.TU) ... {'msg': 'user <user01> logined', 'ok': True}
ok
test0280_notauth_api_call (__main__.TU) ... {'msg': "notauth_func({'param12': 'param-03', 'param13': 'param-04'})", 'ok': True}
ok
test0300_auth_api_call (__main__.TU) ... {'msg': "auth_func({'param3': 'param-01', 'param4': 'param-02'}),user_id=user01", 'ok': True}
ok
test0400_logout (__main__.TU) ... {'msg': 'user <user01> logout', 'ok': True}
ok
test0480_notauth_api_call (__main__.TU) ... {'msg': "notauth_func({'param14': 'param-03', 'param15': 'param-04'})", 'ok': True}
ok
test0500_auth_api_call (__main__.TU) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.216s

OK
```
라는 결과가 나오고 모두 정상동작하는 것을 확인할 수 있습니다.

# TODO

* USERS 관리 부분
* OAuth2 연동 등의 확장


어느 분께는 도움이 되셨기를...