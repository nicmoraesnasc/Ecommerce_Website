from flask import Flask, redirect, url_for, request, render_template, Blueprint, flash, session, abort, jsonify
from database import Database
import logging
import sys
import json
from datetime import datetime
import random
import string
from flask import flash
import os
from werkzeug.utils import secure_filename

logger = logging.getLogger('werkzeug')

app = Flask(__name__)
app.secret_key = '1234'
site = Blueprint('site', __name__, template_folder='templates')

with open(str(sys.argv[1])) as config_file:
    config = json.load(config_file)

database = Database(config["host"], config["db_name"], config["db_user"], config["db_password"])

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET','POST'])
def index():
    user_id = 0
    if 'user_id' in session:
        
        if int(session['user_id']) == 0:
            
            return redirect(url_for('login'))

        user_id = session['user_id']
    else:
        return redirect(url_for('login'))
    
    return redirect(url_for('products'))


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
            session['user_id'] = int(user[0][0])

            # TODO: verificar se usuario possui carrinho
            #       se nao possuir carrinho, criar um.
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

            user = database.select_user(email, password)

            if user:
                database.insert_cart(user[0][0])

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
    if request.method == 'POST':
        try:
            # Verificação de campos obrigatórios
            required_fields = ['product_name', 'product_price', 'product_desc']
            if not all(field in request.form for field in required_fields):
                flash('Preencha todos os campos obrigatórios')
                return redirect(request.url)
            
            # Processamento da imagem
            file = request.files.get('product_img')
            filename = None
            
            if file and file.filename != '':  # Se a imagem foi fornecida
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)  # Usa o nome original da imagem
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                else:
                    flash('Tipo de arquivo não permitido')
                    return redirect(request.url)
            
            # Chamada corrigida para insert_product
            database.insert_product(
                request.form['product_name'],  # name
                request.form['product_desc'],  # description
                request.form['product_price'], # price
                filename                      # image_path (opcional)
            )
            
            flash('Produto criado com sucesso!')
            return redirect(url_for('products'))
            
        except Exception as e:
            flash(f'Erro ao criar produto: {str(e)}')
            return redirect(request.url)
    
    return redirect(url_for('products'))


@app.route('/product/update/<int:id>', methods=['GET', 'POST'])
def update_product(id):
    product = database.get_product_by_id(id)
    if not product:
        abort(404)

    if request.method == 'POST':
        try:
            product_name = request.form['product_name']
            product_desc = request.form['product_desc']
            product_price = float(request.form['product_price'])

            filename = product[4] if len(product) > 4 else None

            if 'product_img' in request.files:
                file = request.files['product_img']
                if file and file.filename != '':  # Se a imagem foi fornecida
                    if allowed_file(file.filename):
                        if filename and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                        filename = secure_filename(file.filename)  # Usando o nome original da imagem
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                    else:
                        flash('Tipo de arquivo não permitido', 'error')
                        return redirect(request.url)

            database.update_product(id, product_name, product_desc, product_price, filename)
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('products'))

        except ValueError:
            flash('Preço inválido', 'error')
        except Exception as e:
            flash(f'Erro ao atualizar produto: {str(e)}', 'error')

    return render_template('product/update.html',
                           product_id=id,
                           product_name=product[1],
                           product_desc=product[2],
                           product_price=product[3],
                           product_img=product[4] if len(product) > 4 else None,
                           is_admin=database.is_admin(session.get('user_id', 0)))


@app.route('/product/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not database.is_admin(session.get('user_id', 0)):
        abort(403)
    
    try:
        if database.delete_product(product_id):
            flash('Product deleted successfully!', 'success')
        else:
            flash('Failed to delete product', 'error')
    except Exception as e:
        flash(f'Error deleting product: {str(e)}', 'error')
    
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

@app.route('/cart', methods=['GET'])
def cart():
    if 'user_id' not in session or session['user_id'] == 0:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cart_items = database.get_full_cart_items(user_id)
    
    total_price = sum(item['total_price'] for item in cart_items)
    
    return render_template('cart/index.html', 
                         cart_items=cart_items,
                         total_price=total_price,
                         is_admin=database.is_admin(session['user_id']))


@app.route('/cart/add/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session or session['user_id'] == 0:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    quantity = int(request.form['quantity'])
    product = database.get_product_by_id(product_id)
    
    if not product:
        abort(404)
    
    unit_price = float(product[3])
    
    cart_id = database.get_cart_id(user_id)
    if not cart_id:
        database.insert_cart(user_id)
        cart_id = database.get_cart_id(user_id)
    
    database.mycursor.execute("""
        SELECT id, quantity FROM CartItem 
        WHERE cart_id = %s AND product_id = %s
    """, (cart_id, product_id))
    existing_item = database.mycursor.fetchone()
    
    if existing_item:
        new_quantity = existing_item[1] + quantity
        database.update_cart_item(existing_item[0], new_quantity)
    else:
        database.insert_cart_item(cart_id, product_id, quantity, unit_price)
    
    return redirect(url_for('cart'))


@app.route('/cart/update/<int:item_id>', methods=['POST'])
def update_cart_item(item_id):
    if 'user_id' not in session or session['user_id'] == 0:
        return redirect(url_for('login'))
    
    quantity = int(request.form['quantity'])
    
    database.update_cart_item(item_id, quantity)
    
    return redirect(url_for('cart'))


@app.route('/cart/remove/<int:item_id>', methods=['POST'])
def remove_cart_item(item_id):
    if 'user_id' not in session or session['user_id'] == 0:
        return redirect(url_for('login'))
    
    database.remove_cart_item(item_id)
    
    return redirect(url_for('cart'))


@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    if 'user_id' not in session or session['user_id'] == 0:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    database.clear_cart(user_id)
    
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session or session['user_id'] == 0:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    cart_items = database.get_full_cart_items(user_id)
    total_price = sum(item['total_price'] for item in cart_items) if cart_items else 0
    
    if not cart_items:
        flash('Seu carrinho está vazio', 'error')
        return redirect(url_for('cart'))

    if request.method == 'POST':
        use_registered = request.form.get('use_registered_address') == 'on'
        
        user_data = database.select_user_by_id(user_id)[0]
        if use_registered:
            shipping_data = {
                'address': user_data[7] if len(user_data) > 7 else 'Não cadastrado',
                'city': user_data[5],
                'state': user_data[4]
            }
        else:
            shipping_data = {
                'address': request.form.get('new_address', 'Não informado'),
                'city': request.form.get('new_city', 'Não informado'),
                'state': request.form.get('new_state', 'Não informado')
            }

        try:
            tracking_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            
            database.insert_order(
                tracking_code=tracking_code,
                user_id=user_id,
                order_date=datetime.now(),
                total_price=total_price,
                confirmed_payment=0,
                shipped=0,
                completed=0,
                shipping_address=shipping_data['address'],
                shipping_city=shipping_data['city'],
                shipping_state=shipping_data['state']
            )
            
            database.clear_cart(user_id)
            
            flash('Pedido finalizado com sucesso!', 'success')
            return redirect(url_for('checkout_success', tracking_code=tracking_code))
            
        except Exception as e:
            flash(f'Erro ao finalizar compra: {str(e)}', 'error')
            return redirect(url_for('cart'))

    user = database.select_user_by_id(user_id)[0]
    return render_template('cart/checkout.html',
                         user=user,
                         cart_items=cart_items, 
                         total_price=total_price,
                         is_admin=database.is_admin(session['user_id'])
                         )


@app.route('/process-payment', methods=['POST'])
def process_payment():
    try:
        user_id = session['user_id']
        cart_items = database.get_full_cart_items(user_id)
        
        if not cart_items:
            flash('Seu carrinho está vazio', 'error')
            return redirect(url_for('cart'))

        tracking_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=13))
        total_price = sum(item['price'] * item['quantity'] for item in cart_items)
        
        order_id = database.insert_order_and_get_id(
            tracking_code=tracking_code,
            user_id=user_id,
            total_price=total_price,
            shipping_address=request.form.get('shipping_address'),
            shipping_city=request.form.get('shipping_city'),
            shipping_state=request.form.get('shipping_state')
        )
        
        if not order_id:
            raise Exception("Falha ao criar pedido")

        for item in cart_items:
            database.insert_order_item(
                order_id=order_id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=item['price']
            )

        database.clear_cart(user_id)
        
        flash('Pagamento processado com sucesso!', 'success')
        return redirect(url_for('my_orders', tracking_code=tracking_code))
        
    except Exception as e:
        logger.error(f"Erro no pagamento: {str(e)}")
        flash(f'Erro ao processar pagamento: {str(e)}', 'error')
        return redirect(url_for('cart'))
    
    
@app.route('/checkout/success/<tracking_code>')
def checkout_success(tracking_code):
    if 'user_id' not in session or session['user_id'] == 0:
        return redirect(url_for('login'))
    
    order = database.get_order_by_tracking(tracking_code)
    return render_template('cart/checkout_success.html',
                         tracking_code=tracking_code,
                         order=order,
                         is_admin=database.is_admin(session['user_id']))

    
@app.route('/confirmation/<tracking_code>')
def order_confirmation(tracking_code):
    if 'user_id' not in session or session['user_id'] == 0:
        return redirect(url_for('login'))
    
    return render_template('order/confirmation.html', tracking_code=tracking_code, is_admin=database.is_admin(session['user_id']))

@app.route('/orders')
def my_orders():
    if 'user_id' not in session or session['user_id'] == 0:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    orders = database.get_user_orders(user_id)
    
    return render_template('order/my_orders.html', orders=orders, is_admin=database.is_admin(session['user_id']))

# ===== NOVAS ROTAS PARA O PAINEL ADMIN =====

@app.route('/admin/orders')
def admin_orders():
    """Lista todos os pedidos com opções de filtro"""
    if not database.is_admin(session.get('user_id', 0)):
        abort(403)  # Acesso negado se não for admin
    
    # Obter parâmetros de filtro da URL
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '')
    
    # Obter pedidos filtrados
    orders = database.get_all_orders(status_filter, search_query)
    
    return render_template('admin/orders.html',
                        orders=orders,
                        status_filter=status_filter,
                        search_query=search_query,
                        is_admin=True)

@app.route('/admin/order/<int:order_id>', methods=['GET', 'POST'])
def admin_order_detail(order_id):
    """Detalhes de um pedido específico e atualização de status"""
    if not database.is_admin(session.get('user_id', 0)):
        abort(403)
    
    if request.method == 'POST':
        # Processar atualização do pedido
        new_status = request.form.get('shipping_status')
        payment_status = request.form.get('payment_status')
        database.update_order_status(order_id, new_status, payment_status)
        flash('Status atualizado com sucesso!', 'success')
    
    # Obter dados do pedido
    order = database.get_order_details(order_id)
    if not order:
        abort(404)
    
    # Obter itens do pedido (usando seu método existente)
    order_items = database.get_order_items(order_id)
    
    return render_template('admin/order_detail.html',
                         order=order,
                         order_items=order_items,
                         is_admin=True)

@app.route('/admin/order/update_status', methods=['POST'])
def update_order_status():
    """Endpoint para atualização de status via AJAX (opcional)"""
    if not database.is_admin(session.get('user_id', 0)):
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    try:
        data = request.get_json()
        order_id = data['order_id']
        new_status = data['status']
        
        # Atualiza apenas o status de envio (adaptar conforme necessidade)
        database.mycursor.execute(
            "UPDATE `Order` SET shipping_status = %s WHERE id = %s",
            (new_status, order_id)
        )
        database.mydb.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
    app.run(host=config["host"], 
            port=config["port"], 
            debug=config["debug"])

    