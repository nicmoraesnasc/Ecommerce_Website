import mysql.connector
import os
import logging

logger = logging.getLogger('werkzeug')

class Database:
  def __init__(self, host, db_name, db_user, db_password):

    self.mydb = mysql.connector.connect(
      host=host,
      user=db_user,
      password=db_password
    )

    self.mycursor = self.mydb.cursor()

    self.mycursor.execute("CREATE DATABASE IF NOT EXISTS mydatabase2")
    self.mycursor.execute("USE mydatabase2")

    self.mydb = mysql.connector.connect(
      host=host,
      user=db_user,
      password=db_password,
      database=db_name
    )

    self.mycursor = self.mydb.cursor()

    self.mycursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            name VARCHAR(255), 
            last_name VARCHAR(255), 
            phone VARCHAR(11), 
            state VARCHAR(255), 
            city VARCHAR(255), 
            email VARCHAR(255), 
            password VARCHAR(255), 
            is_admin TINYINT
        );
        """)

    self.mycursor.execute("""
        CREATE TABLE IF NOT EXISTS Product (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            product_name VARCHAR(255), 
            product_desc VARCHAR(255), 
            product_price FLOAT, 
            image_path VARCHAR(255)
        );
        """)

    self.mycursor.execute("""
        INSERT IGNORE INTO User 
            (id, name, last_name,phone, state, city, email, password, is_admin) 
        VALUES 
            (1, 'root', 'root', '99999999999', 'root', 'root', 'root@root.com', 'root', 1);
        """)
    
    self.mycursor.execute("""
        CREATE TABLE IF NOT EXISTS Cart (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            FOREIGN KEY (user_id) REFERENCES User(id)
        );
        """)
    
    self.mycursor.execute("""
        CREATE TABLE IF NOT EXISTS CartItem (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cart_id INT,
            product_id INT,
            quantity INT, 
            price FLOAT,
            FOREIGN KEY (cart_id) REFERENCES Cart(id),
            FOREIGN KEY (product_id) REFERENCES Product(id)
        );
        """)

    self.mycursor.execute("""
        CREATE TABLE IF NOT EXISTS `Order` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tracking_code VARCHAR(13) UNIQUE NOT NULL,
            user_id INT NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_price DECIMAL(10,2) NOT NULL,
            confirmed_payment TINYINT(1) DEFAULT 1,  # 1 = true (pago)
            shipped TINYINT(1) DEFAULT 0,
            completed TINYINT(1) DEFAULT 0,
            shipping_address VARCHAR(255),
            shipping_city VARCHAR(255),
            shipping_state VARCHAR(255),
            payment_status ENUM('pendente', 'pago', 'erro', 'estornado') DEFAULT 'pago',
            shipping_status ENUM('pendente', 'enviado') DEFAULT 'enviando',
            FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
        );
    """)
      
    self.mycursor.execute("""
        CREATE TABLE IF NOT EXISTS OrderItem (
            id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT,
            product_id INT,
            quantity INT, 
            price FLOAT,
            FOREIGN KEY (order_id) REFERENCES `Order`(id),
            FOREIGN KEY (product_id) REFERENCES Product(id)
        );
        """)

    self.mydb.commit()

  def insert_user(self, name, last_name, phone, state, city, email, password, is_admin):
     self.mycursor.execute(f"INSERT INTO User (name, last_name, phone, state, city, email, password, is_admin) VALUES ('{str(name)}', '{str(last_name)}', '{str(phone)}', '{str(state)}', '{str(city)}', '{str(email)}', '{str(password)}', {str(is_admin)});")
     self.mydb.commit()

  def select_user(self, email, password):
    self.mycursor.execute(f" SELECT * FROM User WHERE email = '{email}' AND password = '{password}';")
    user = []
    result = self.mycursor.fetchall()
    for row in result:
      user.append(row)
    return user
  
  def select_user_by_id(self, user_id):
    self.mycursor.execute(f"SELECT * FROM User WHERE id = '{user_id}';")
    user = []
    result = self.mycursor.fetchall()
    for row in result:
      user.append(row)
    return user
  
  def update_user(self, id, name=None, last_name=None, phone=None, state=None, city=None, email=None, password=None):
    updates = []
    values = []
    if name is not None and name != '':
        updates.append("name = %s")
        values.append(name)
    if last_name is not None and last_name != '':
        updates.append("last_name = %s")
        values.append(last_name)
    if phone is not None and phone != '':
        updates.append("phone = %s")
        values.append(phone)
    if state is not None and state != '':
        updates.append("state = %s")
        values.append(state)
    if city is not None and city != '':
        updates.append("city = %s")
        values.append(city)
    if email is not None and email != '':
        updates.append("email = %s")
        values.append(email)
    if password is not None and password != '':
        updates.append("password = %s")
        values.append(password)
    if updates:
        query = f"UPDATE User SET {', '.join(updates)} WHERE id = %s"
        values.append(id)
        self.mycursor.execute(query, tuple(values))
        self.mydb.commit()

  def get_users(self):
    self.mycursor.execute("SELECT * FROM User;")
    users = []
    results = self.mycursor.fetchall()
    for row in results:
      users.append(row)
    return users
  
  def is_admin(self, user_id):
    return bool(self.select_user_by_id(user_id)[0][8])
  
  def delete_user(self, user_id):
    self.mycursor.execute(f"DELETE FROM User WHERE id = {user_id};")
    self.mydb.commit()

  def insert_product(self, product_name, product_desc, product_price, image_path=None):
      if image_path:
          query = "INSERT INTO Product (product_name, product_desc, product_price, image_path) VALUES (%s, %s, %s, %s)"
          values = (product_name, product_desc, product_price, image_path)
      else:
          query = "INSERT INTO Product (product_name, product_desc, product_price) VALUES (%s, %s, %s)"
          values = (product_name, product_desc, product_price)
      
      self.mycursor.execute(query, values)
      self.mydb.commit()
    
  def get_products(self):
    self.mycursor.execute("SELECT * FROM Product;")
    products = []
    results = self.mycursor.fetchall()
    for row in results:
      products.append(row)
    return products
  
  def get_product_by_id(self, product_id):
    self.mycursor.execute(f"SELECT * FROM Product WHERE id = '{product_id}';")
    product = []
    result = self.mycursor.fetchall()

    if not result:
      return None
  
    for row in result:
      product.append(row)
    return product[0]

  def update_product(self, product_id, product_name, product_desc, product_price, image_path=None):
      if image_path:
          query = "UPDATE Product SET product_name = %s, product_desc = %s, product_price = %s, image_path = %s WHERE id = %s"
          values = (product_name, product_desc, product_price, image_path, product_id)
      else:
          query = "UPDATE Product SET product_name = %s, product_desc = %s, product_price = %s WHERE id = %s"
          values = (product_name, product_desc, product_price, product_id)
      
      self.mycursor.execute(query, values)
      self.mydb.commit()

  def delete_product(self, product_id):
    try:
        self.mycursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        self.mycursor.execute("DELETE FROM CartItem WHERE product_id = %s", (product_id,))
        self.mycursor.execute("DELETE FROM OrderItem WHERE product_id = %s", (product_id,))
        
        product = self.get_product_by_id(product_id)
        if product and product[4]:
            img_path = os.path.join('static', 'uploads', product[4])
            if os.path.exists(img_path):
                os.remove(img_path)
        
        self.mycursor.execute("DELETE FROM Product WHERE id = %s", (product_id,))
        self.mydb.commit()
        return True
    except Exception as e:
        self.mydb.rollback()
        logger.error(f"Error deleting product: {str(e)}")
        return False
    finally:
        self.mycursor.execute("SET FOREIGN_KEY_CHECKS = 1")

  def select_product(self, product_id):
    self.mycursor.execute(f"SELECT * FROM Product WHERE id = {product_id};")
    product = []
    result = self.mycursor.fetchall()
    for row in result:
      product.append(row)
    return product

  def insert_cart(self, user_id):
    self.mycursor.execute("SELECT * FROM Cart WHERE user_id = %s", (user_id,))
    cart = self.mycursor.fetchone()
    if not cart:
      self.mycursor.execute(f"INSERT INTO Cart (user_id) VALUES ('{str(user_id)}')")
      self.mydb.commit()

  def insert_cart_item(self, cart_id, product_id, quantity, price):
    self.mycursor.execute(f"INSERT INTO CartItem (cart_id, product_id, quantity, price) VALUES ('{str(cart_id)}', '{str(product_id)}', '{str(quantity)}', '{str(price)}')")
    self.mydb.commit()

  def get_cart_items(self, user_id):
    self.mycursor.execute("SELECT * FROM CartItem WHERE id = %s", (user_id,))
    cart_items = []
    results = self.mycursor.fetchall()
    for row in results:
      cart_items.append(row)
    return cart_items

  def insert_order(self, tracking_code, user_id, order_date, total_price, 
                confirmed_payment=1, shipped=0, completed=0, 
                shipping_address=None, shipping_city=None, shipping_state=None, 
                payment_status='pago', shipping_status='enviando'):
    try:
        valid_payment = ['pendente', 'pago', 'erro', 'estornado']
        valid_shipping = ['pendente', 'enviado']
        
        payment_status = payment_status if payment_status in valid_payment else 'pago'
        shipping_status = shipping_status if shipping_status in valid_shipping else 'pendente'
        
        query = """
            INSERT INTO `Order` 
            (tracking_code, user_id, order_date, total_price,
            confirmed_payment, shipped, completed,
            shipping_address, shipping_city, shipping_state,
            payment_status, shipping_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            tracking_code,
            user_id,
            order_date,
            total_price,
            confirmed_payment,
            shipped,
            completed,
            shipping_address,
            shipping_city,
            shipping_state,
            payment_status,
            shipping_status
        )
        self.mycursor.execute(query, values)
        self.mydb.commit()
        return True
    except mysql.connector.Error as err:
        logger.error(f"Erro ao inserir pedido: {err}")
        return False
    
  def insert_order_item(self, order_id, product_id, quantity, price):
    self.mycursor.execute("SELECT id FROM Product WHERE id = %s", (product_id,))
    product = self.mycursor.fetchone()
    if not product:
        raise ValueError(f"Produto com ID {product_id} não encontrado!")
    self.mycursor.execute("""
        INSERT INTO OrderItem (order_id, product_id, quantity, price)
        VALUES (%s, %s, %s, %s)
    """, (order_id, product_id, quantity, price))
    self.mydb.commit()

  def get_order_by_tracking(self, tracking_code):
      self.mycursor.execute("""
          SELECT tracking_code, order_date, total_price, 
                shipping_address, shipping_city, shipping_state
          FROM `Order`
          WHERE tracking_code = %s
      """, (tracking_code,))
      result = self.mycursor.fetchone()
      if result:
          columns = [col[0] for col in self.mycursor.description]
          return dict(zip(columns, result))
      return None

  def get_cart_id(self, user_id):
      self.mycursor.execute("SELECT id FROM Cart WHERE user_id = %s", (user_id,))
      cart = self.mycursor.fetchone()
      if cart:
          return cart[0]
      return None

  def get_full_cart_items(self, user_id):
      cart_id = self.get_cart_id(user_id)
      if not cart_id:
          return []
      
      self.mycursor.execute("""
          SELECT 
              CartItem.id, 
              Product.id as product_id,  # Certifique-se de incluir isso
              Product.product_name, 
              CartItem.quantity, 
              CartItem.price,
              (CartItem.quantity * CartItem.price) as total_price
          FROM CartItem
          JOIN Product ON CartItem.product_id = Product.id
          WHERE CartItem.cart_id = %s
      """, (cart_id,))
      
      columns = [col[0] for col in self.mycursor.description]
      return [dict(zip(columns, row)) for row in self.mycursor.fetchall()]

  def update_cart_item(self, item_id, quantity):
      self.mycursor.execute("""
          UPDATE CartItem 
          SET quantity = %s 
          WHERE id = %s
      """, (quantity, item_id))
      self.mydb.commit()

  def remove_cart_item(self, item_id):
      self.mycursor.execute("DELETE FROM CartItem WHERE id = %s", (item_id,))
      self.mydb.commit()

  def clear_cart(self, user_id):
      cart_id = self.get_cart_id(user_id)
      if cart_id:
          self.mycursor.execute("DELETE FROM CartItem WHERE cart_id = %s", (cart_id,))
          self.mydb.commit()

  def get_user_orders(self, user_id):
    self.mycursor.execute("""
        SELECT id, tracking_code, order_date, total_price, 
               payment_status, shipping_status
        FROM `Order`
        WHERE user_id = %s
        ORDER BY order_date DESC
    """, (user_id,))
    
    columns = [col[0] for col in self.mycursor.description]
    return [dict(zip(columns, row)) for row in self.mycursor.fetchall()]

  def get_order_items(self, order_id):
      self.mycursor.execute("""
          SELECT oi.quantity, oi.price, 
                p.product_name, p.product_desc
          FROM OrderItem oi
          JOIN Product p ON oi.product_id = p.id
          WHERE oi.order_id = %s
      """, (order_id,))
      
      columns = [col[0] for col in self.mycursor.description]
      return [dict(zip(columns, row)) for row in self.mycursor.fetchall()]
  
  def insert_order_and_get_id(self, tracking_code, user_id, total_price, **shipping_info):
    try:
        query = """
            INSERT INTO `Order` 
            (tracking_code, user_id, total_price,
             shipping_address, shipping_city, shipping_state)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            tracking_code,
            user_id,
            total_price,
            shipping_info.get('shipping_address'),
            shipping_info.get('shipping_city'),
            shipping_info.get('shipping_state')
        )
        
        self.mycursor.execute(query, values)
        self.mydb.commit()
        return self.mycursor.lastrowid  # Retorna o ID do pedido criado
        
    except mysql.connector.Error as err:
        logger.error(f"Erro ao criar pedido: {err}")
        return None

  # ===== MÉTODOS FALTANTES PARA O PAINEL ADMIN =====

  def get_all_orders(self, status_filter='all', search_query=''):
      """Retorna todos os pedidos com filtros opcionais"""
      query = """
          SELECT o.id, o.tracking_code, u.email as user_email, 
                o.order_date, o.total_price, o.shipping_status,
                o.payment_status, o.shipping_address, o.shipping_city, o.shipping_state
          FROM `Order` o
          JOIN User u ON o.user_id = u.id
      """
      
      conditions = []
      params = []
      
      if status_filter != 'all':
          conditions.append("o.shipping_status = %s")
          params.append(status_filter)
      
      if search_query:
          conditions.append("(o.tracking_code LIKE %s OR u.email LIKE %s)")
          params.extend([f"%{search_query}%", f"%{search_query}%"])
      
      if conditions:
          query += " WHERE " + " AND ".join(conditions)
      
      query += " ORDER BY o.order_date DESC"
      
      self.mycursor.execute(query, tuple(params))
      return self.mycursor.fetchall()

  def get_order_details(self, order_id):
      """Obtém detalhes completos de um pedido específico"""
      query = """
          SELECT o.*, u.email, u.name, u.phone
          FROM `Order` o
          JOIN User u ON o.user_id = u.id
          WHERE o.id = %s
      """
      self.mycursor.execute(query, (order_id,))
      return self.mycursor.fetchone()

  def update_order_status(self, order_id, shipping_status, payment_status):
      """Atualiza os status de envio e pagamento de um pedido"""
      query = """
          UPDATE `Order` 
          SET shipping_status = %s, payment_status = %s
          WHERE id = %s
      """
      self.mycursor.execute(query, (shipping_status, payment_status, order_id))
      self.mydb.commit()
      return self.mycursor.rowcount > 0