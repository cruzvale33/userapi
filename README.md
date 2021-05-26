# userapi
API authorization and tasks for users

## Installation

Install the virtual enviroment

```bash
python -m venv venv
```

Let's activate the venv 

```bash
venv\Scripts\activate
```

Now you can install the framework and dependencies

```bash
pip install flask

pip install -r requirements.txt

Pip install Flask-SQLAlchemy

pip install passlib

pip install Flask-HTTPAuth

pip install mysqlclient

pip install responses

pip install markdown

pip install flask_swagger_ui
```

Set the default config to development mode 

DATABASE NAME: apiuser (MySql)

```bash
export FLASK_APP=main.py
```
```bash
export FLASK_ENV=development
```

To run the app
```bash
flask run
```

To test the methods
```bash
python -m unittest tests.py
```

The API documentation you can find this in:
http://127.0.0.1:5000/api/docs/