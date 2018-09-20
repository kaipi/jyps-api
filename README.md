This is simple flask based api to serve jyps ry's event registeration system and bicyclist statistics.

##Things you need:

```
Python virtualenv installed
Python 3.5+
MariaDb 10+ (configure your db options in localconfig.py)
```

##Install + startup

```
enable virtualenv: source ./venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask db migrate
flask run --with-threads
python createuser.py to create first user
```
