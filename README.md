# MyClassmates

deployment steps

 #1. install needed dependencies:
```
 - caddy
 - python3
```
the steps needed will vary per platform, as such please find the relevant steps for your environment.

 #2. start backend server

navigate to `/server`

create a python virtual environment `python3 -m venv venv`

activate the environment `source venv/bin/activate`

install libraries `pip3 install -r requirements.txt`

start the server `python3 src/main.py`

 #3. start the frontend server

in a seperate terminal instance navigate to `/client`

run the server with `python3 -m http.server`

 #4. run caddy

in one last terminal instance, start caddy `caddy start`

from here open your browser to `https://localhost:5000/`
