from flask import Flask, redirect, url_for, request, render_template, Blueprint, flash, session, abort, jsonify
from flask import Flask
from database import Database
import logging
import sys
import json

logger = logging.getLogger('werkzeug')

app = Flask(__name__)
app.secret_key = '1234'
site = Blueprint('site', __name__, template_folder='templates')

with open(str(sys.argv[1])) as config_file:
    config = json.load(config_file)

database = Database(config["host"], config["db_name"], config["db_user"], config["db_password"])

@app.route('/', methods=['GET','POST'])
def index():
    user_id = 0
    if 'user_id' in session:
        
        if int(session['user_id']) == 0:
            
            return redirect(url_for('login'))

        user_id = session['user_id']
    else:
        return redirect(url_for('login'))

    return render_template('index.html', user_id = user_id, is_admin=database.is_admin(user_id))

@app.route('/login', methods=['GET','POST'])
def login():

    login_failed = False

    if (request.method == 'POST' and 'email' in request.form and 'password' in request.form):

        email = request.form['email']
        password = request.form['password']

        user = database.select_user(email, password)

        if not user:
            login_failed = True
            session['user_id'] = 0
        else:
            print(user[0])
            session['user_id'] = int(user[0][0])
            return redirect(url_for('index'))

    return render_template('auth/login.html', login_failed=login_failed)


@app.route('/logout', methods=['GET','POST'])
def logout():
    session['user_id'] = 0
    return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    return render_template('auth/register.html')

@app.route('/user/create', methods=['GET', 'POST'])
def create_user():
    
    if (request.method == 'POST' and 'name' in request.form and 'last_name' in request.form and 'phone' in request.form and 'state' in request.form and 'city' in request.form and 'email' in request.form and 'password' in request.form and 'password_c' in request.form):
        
        name = request.form['name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        state = request.form['state']
        city = request.form['city']
        email = request.form['email']
        password = request.form['password']
        password_c = request.form['password_c']

        password_incorrect = password_c != password

        if not password_incorrect:

            database.insert_user(name, last_name, phone, state, city, email, password, 0)

            return redirect(url_for('login'))
            
    return redirect('/register')

@app.route('/user', methods=['GET','POST'])
def user():
    user_id = session['user_id']
    user = database.select_user_by_id(user_id)[0]

    return render_template('user/index.html',
                           user=user,
                           is_admin=database.is_admin(user_id))

@app.route('/user/update/<id>', methods=['GET', 'POST'])
def update_user(id):

    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        state = request.form['state']
        city = request.form['city']
        email = request.form['email']
        password = request.form['password']
        password_c = request.form['password_c']

        password_incorrect = password_c != password

        if not password_incorrect:

            database.update_user(id, name, last_name, phone, state, city, email, password)
            return redirect(url_for('user'))

    user = database.select_user_by_id(id)[0]

    return render_template('user/update.html', 
                        id=user[0],
                        name=user[1],
                        last_name=user[2],
                        phone=user[3],
                        state=user[4],
                        city=user[5],
                        email=user[6],
                        password=user[7],
                        user_id=user[0],
                        is_admin=database.is_admin(session['user_id']))

@app.route('/admin/users', methods=['GET'])
def manage_users():
    users = database.get_users()
    return render_template('user/manage.html', users=users, is_admin=database.is_admin(session['user_id']))

@app.route('/user/delete/<id>', methods=['GET', 'POST'])
def delete_user(id):
    database.delete_user(id)
    return redirect(url_for('user'))

@app.route('/products', methods=['GET','POST'])
def products():
    print(session['user_id'])
    return render_template('product/index.html', 
                           products=database.get_products(),
                           is_admin=database.is_admin(session['user_id'])
                           )

@app.route('/product/create', methods=['GET', 'POST'])
def create_product():
    if (request.method == 'POST' and 'product_name' in request.form and 'product_price' in request.form and 'product_desc' in request.form):
        
        product_name = request.form['product_name']
        product_price = request.form['product_price']
        product_desc = request.form['product_desc']

        database.insert_product(product_name, product_desc, product_price)

    return redirect(url_for('products'))

@app.route('/product/update/<id>', methods=['GET', 'POST'])
def update_product(id):
    if (request.method == 'POST' and 'product_name' in request.form and 'product_desc' in request.form and 'product_price' in request.form):
        
        product_name = request.form['product_name']
        product_desc = request.form['product_desc']
        product_price = request.form['product_price']

        database.update_product(id, product_name, product_desc, product_price)

    product = database.get_product_by_id(id)

    return render_template('product/update.html', 
                           product_id=id,
                           product_name=product[1],
                           product_desc=product[2],
                           product_price=product[3],
                           is_admin=database.is_admin(session['user_id'])
                           )

@app.route('/product/delete/<id>', methods=['GET', 'POST'])
def delete_product(id):
    database.delete_product(id)
    return redirect(url_for('products'))


@app.route('/user/select/<id>', methods=['GET', 'POST'])
def select_product(id):
    database.select_product(id)
    product = database.get_product_by_id(id)
    return render_template('product/select.html', 
                           product_id=id,
                           product_name=product[1],
                           product_desc=product[2],
                           product_price=product[3],
                           is_admin=database.is_admin(session['user_id'])
                           )


if __name__ == '__main__':
    app.run(debug=True)
    app.run(host=config["host"], 
            port=config["port"], 
            debug=config["debug"])

    