from flask import Flask, json
from config import DevelopmentConfig
from flask_httpauth import HTTPBasicAuth
from flask import g, jsonify
from flask import request
from flask_login import login_required, current_user, login_user, logout_user, LoginManager

from models import Task, db
from models import User

import pathlib
import markdown

from flask_swagger_ui import get_swaggerui_blueprint

#auth = HTTPBasicAuth()

app = Flask(__name__)

#login_manager = LoginManager()
#login_manager.init_app(app)
#login_manager.login_message = "You must be logged in to access this page."
#login_manager.login_view = "auth.login"

app.config.from_object(DevelopmentConfig)

db.init_app(app)
with app.app_context():
    db.create_all()


app_path = pathlib.Path(__file__).parent.absolute()


### swagger specific ###
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "STING API User authentication and tasks managment"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


#Show the readme.md file content
@app.route("/")
def index():
    # You can then reference the file's path relative to the app's path. 
    readme_file = open(str(app_path)+'/README.md', 'r')
    md_template_string = markdown.markdown(readme_file.read(), extensions=["fenced_code"]                                         )
    return md_template_string

#Check if the user and password are valid or is a valid token
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(email = username_or_token).first()
        print(user)
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

#Get the authorization token for the user
def get_auth_token():
    token = g.user.generate_auth_token()
    return  token.decode('ascii')


#This route allows to an user get the auth token
@app.route('/api/login', methods=['POST'])
def login():
    user_request = json.loads(request.form.get('user'))
    user = User()
    user.email = user_request['email']
    user.password_hash = user_request['password']
    
    if verify_password(user.email, user.password_hash):
        token = get_auth_token()
        user = User.query.filter_by(email = user_request['email']).first()
        user.token = token
        db.session.commit()
        return jsonify({'user' : g.user.get_id(), 'token' : token})
    
    return jsonify({'message' : 'Invalid User'})

#Destroy the user auth token 
@app.route("/api/logout", methods= ['POST'])
def logout():
    id = request.form.get('id')
    user = User.query.filter_by(id = id).first()
    user.token = None
    db.session.commit()
    return 'Logout'

#This route allows to check if a token is valid
@app.route('/api/check-token', methods = ['POST'])
def check_token():
    token = request.form.get('token')
    if token:
        if verify_password(token, None):
            return True
    return False

#Function to remove an user by id
def delete_user(id):
    user = User.query.filter_by(id = id).first()
    db.session.delete(user)
    db.session.commit()
    return 'User Deleted'

#Function to update an user 
def update_user(user_request):
    user = User.query.filter_by(id = int(user_request['id'])).first()
    user.photo = user_request['photo'] if user_request['email'] else user.photo
    user.full_name = user_request['full_name'] if user_request['full_name'] else user.full_name
    user.email = user_request['email'] if user_request['email'] else user.email

    db.session.commit()

    return 'User Updated'

#This route allows multiple methods from request POST, PUT, DELETE
#It is used to create, update or delete an user
@app.route('/api/users', methods = ['POST', 'DELETE', 'PUT'])
def users():
    
    if request.method == 'POST':
      
        user_request = json.loads(request.form.get('user'))
        
        user = User(email = user_request['email'],password_hash = user_request['password'], full_name = user_request['full_name'], photo = user_request['photo'] if user_request['photo'] else None)
        user.hash_password(user.password_hash)
        db.session.add(user)
        db.session.commit()

        return jsonify({'id':user.get_id()})

    if request.method == 'DELETE':
        id = request.form.get('id')
        if check_token():
            return delete_user(id)
        return 'Invalid Token'

    if request.method == 'PUT':
        if check_token():
            user_request = json.loads(request.form.get('user'))
            return update_user(user_request)    
        return 'Invalid Token'

#This route use a GET method and return an user structure by id       
@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.filter_by(id = int(id)).first()
    if not user:
        return jsonify({'message' : 'User not found'})
    return jsonify({'id' : user.id,'email' : user.email, 'full_name' : user.full_name, 'photo' : user.photo })


#This route allows multiple methods from request POST, PUT, DELETE
#It is used to create, update or delete tasks for an user
@app.route('/api/tasks', methods = ['POST', 'DELETE', 'PUT'])
def tasks():
    if request.method == 'POST':
        if check_token():
            user_id = request.form.get('user_id')
            task_request = json.loads(request.form.get('task'))

            task = Task(title = task_request['title'], description = task_request['description'], start_date = task_request['start_date'], due_date = task_request['due_date'])
            
            user = User.query.filter_by(id = int(user_id)).first()
            user.tasks = [task]

            db.session.commit()

            return jsonify({'task_id' : task.get_id()})

        return 'Invalid Token'
    
    if request.method == 'DELETE':
        id = request.form.get('id')
        if check_token():
            task = Task.query.filter_by(id = id).first()
            db.session.delete(task)
            db.session.commit()
            return 'Task Deleted'
        return 'Invalid Token'
    
    if request.method == 'PUT':
        if check_token():
            task_request = json.loads(request.form.get('task'))
        
            task = Task.query.filter_by(id = int(task_request['id'])).first()
            task.title = task_request['title'] if task_request['title'] else task.title
            task.description = task_request['description'] if task_request['description'] else task.description
            task.start_date = task_request['start_date'] if task_request['start_date'] else task.start_date
            task.due_date = task_request['due_date'] if task_request['due_date'] else task.due_date

            db.session.commit()

            return 'Task Updated'
        return 'Invalid Token'

#This route use a GET method and return a task structure by id       
@app.route('/api/tasks/<int:id>')
def get_task(id):
    task = Task.query.filter_by(id = int(id)).first()
    if not task:
        return jsonify({'message' : 'Task not found'})
    return jsonify({'id' : task.id,'title' : task.title, 'description' : task.description, 'start_date' : task.formatted_start_date, 'due_date' : task.formatted_due_date, 'priority' : task.priority })
#if __name__ == '__main__':
