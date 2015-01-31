import web
import time
import json
import hashlib
import random as rand

urls = [
    '/si', 'SignIn',
    '/su', 'SignUp',
    '/so', 'SignOut'
]

app = web.application(urls, globals())
web.config.debug = False
db = web.database(dbn='sqlite', db='database.db')
db.query('''
    CREATE TABLE IF NOT EXISTS users(
        uid INTEGER PRIMARY KEY,
        uusr TEXT NOT NULL,
        upwd TEXT NOT NULL,
        utme INTEGER,
        utkn TEXT
    );
''')

store = web.session.DiskStore('sessions')
session = web.session.Session(app, store, initializer={'acc_token':''})
web.config._session = session

def genToken():
    r = int(rand.random()*10**7)
    return str(hashlib.sha1('%d%s'%(r, time.ctime())).hexdigest())

def getUser(usr, tkn=None):
    if tkn:
        d = dict(tkn = tkn); q = 'utkn = $tkn'
    else:
        d = dict(usr = usr); q = 'uusr = $usr'

    res = list(db.select('users', d, where=q))
    return res[0] if len(res) else None

def getPwd(usr, pwd):
    return hashlib.sha1('%s:%s'%(usr, pwd)).hexdigest()

def json_response(f):
    def wrapper(*args, **kwargs):
        res = f(*args, **kwargs)

        if type(res) is dict:
            return json.dumps(res)
        else:
            return res
    return wrapper

class Index:
    def GET(self):
        return

class SignUp:
    @json_response
    def GET(self):
        i = web.input()
        if not i.get('usr') or not i.get('pwd'):
            return web.badrequest()
        usr = i.get('usr');
        pwd = getPwd(usr, i.get('pwd'))

        if getUser(usr):
            return {'error': 'userExist - user already exist'}

        db.insert('users', uusr=usr, upwd=pwd, utkn=genToken(), utme=int(time.time()))

        return {'sucess': True}

class SignIn:
    @json_response
    def GET(self):
        i = web.input()
        if not i.get('usr') or not i.get('pwd'):
            return web.badrequest()
        usr = i.get('usr')
        pwd = getPwd(usr, i.get('pwd'))

        user = getUser(usr)
        if not user:
            return {'error': 'userNotExist - user does not exist'}

        if not user['upwd']==pwd:
            return {'error': 'invalidPass - invalid password, try again'}
        else:
            t = int(time.time())
            if t-user['utme'] > 1200:
                token = genToken()
            else:
                token = user['utkn']

            res = db.update('users', where='uid=$id', utkn=token, utme=int(time.time()), vars={'id':user['uid']})

            '''
            s = web.config._session
            s.acc_token = token
            web.config._session = s
            '''

            return {'success':True, 'token':token}

        return {'error':'loginError - cannot login'}

class SignOut:
    @json_response
    def GET(self):
        '''
        s = web.config._session
        s.kill()
        return dir(s)
        '''

        i = web.input()
        if not i.get('tkn'):
            return web.badrequest()
        tkn = i.get('tkn')

        user = getUser(None, tkn)
        if not user:
            return {'error':'Not logged in'}

        res = db.update('users', where='uid=$id', utkn=None, utme=0, vars={'id':user['uid']})

        return web.seeother('/')

if __name__=='__main__':
    app.run()
