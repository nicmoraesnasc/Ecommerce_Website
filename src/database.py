import mysql.connector
import logging
import os
import sqlite3

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
        CREATE TABLE IF NOT EXISTS user (
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
        CREATE TABLE IF NOT EXISTS product (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            product_name VARCHAR(255), 
            product_desc VARCHAR(255), 
            product_price FLOAT, 
            img BLOB
        );
        """)

    self.mycursor.execute("""
        INSERT IGNORE INTO user 
            (id, name, last_name,phone, state, city, email, password, is_admin) 
        VALUES 
            (1, 'root', 'root', '99999999999', 'root', 'root', 'root@root.com', 'root', 1);
        """)

    self.mydb.commit()

  def insert_user(self, name, last_name, phone, state, city, email, password, is_admin):
     self.mycursor.execute(f"INSERT INTO user (name, last_name, phone, state, city, email, password, is_admin) VALUES ('{str(name)}', '{str(last_name)}', '{str(phone)}', '{str(state)}', '{str(city)}', '{str(email)}', '{str(password)}', {str(is_admin)});")
     self.mydb.commit()

  def select_user(self, email, password):
    self.mycursor.execute(f" SELECT * FROM user WHERE email = '{email}' AND password = '{password}';")
    user = []
    result = self.mycursor.fetchall()
    for row in result:
      user.append(row)
    return user
  
  def select_user_by_id(self, user_id):
    self.mycursor.execute(f"SELECT * FROM user WHERE id = '{user_id}';")
    user = []
    result = self.mycursor.fetchall()
    for row in result:
      user.append(row)
    return user
  
  def update_user(self, id, name, last_name, phone, state, city, email, password):
    if name == '':
      self.mycursor.execute(f"UPDATE user SET last_name = '{last_name}', phone = {phone}, state = '{state}', city = '{city}', email = '{email}', password = '{password}' WHERE id = {id};")
    if last_name == '':
      self.mycursor.execute(f"UPDATE user SET name = '{name}', phone = {phone}, state = '{state}', city = '{city}', email = '{email}', password = '{password}' WHERE id = {id};")
    if phone == '':
      self.mycursor.execute(f"UPDATE user SET name = '{name}', last_name = '{last_name}', state = '{state}', city = '{city}', email = '{email}', password = '{password}' WHERE id = {id};")
    if state == '':
      self.mycursor.execute(f"UPDATE user SET name = '{name}', last_name = '{last_name}', phone = {phone}, city = '{city}', email = '{email}', password = '{password}' WHERE id = {id};")
    if city == '':
      self.mycursor.execute(f"UPDATE user SET name = '{name}', last_name = '{last_name}', phone = {phone}, state = '{state}', email = '{email}', password = '{password}' WHERE id = {id};")
    if email == '':
      self.mycursor.execute(f"UPDATE user SET name = '{name}', last_name = '{last_name}', phone = {phone}, state = '{state}', city = '{city}', password = '{password}' WHERE id = {id};")
    if password == '':
      self.mycursor.execute(f"UPDATE user SET name = '{name}', last_name = '{last_name}', phone = {phone}, state = '{state}', city = '{city}', email = '{email}' WHERE id = {id};")
    else:
      self.mycursor.execute(f"UPDATE user SET name = '{name}', last_name = '{last_name}', phone = {phone}, state = '{state}', city = '{city}', email = '{email}', password = '{password}' WHERE id = {id};")
    self.mydb.commit()

  def get_users(self):
    self.mycursor.execute("SELECT * FROM user;")
    users = []
    results = self.mycursor.fetchall()
    for row in results:
      users.append(row)
    return users
  
  def is_admin(self, user_id):
    return bool(self.select_user_by_id(user_id)[0][8])
  
  def delete_user(self, user_id):
    self.mycursor.execute(f"DELETE FROM user WHERE id = {user_id};")
    self.mydb.commit()
    
  def get_products(self):
    self.mycursor.execute("SELECT * FROM product;")
    products = []
    results = self.mycursor.fetchall()
    for row in results:
      products.append(row)
    return products
  
  def get_product_by_id(self, product_id):
    self.mycursor.execute(f"SELECT * FROM product WHERE id = '{product_id}';")
    product = []
    result = self.mycursor.fetchall()
    for row in result:
      product.append(row)
    return product[0]
  

  def update_product(self, product_id, product_name, product_desc, product_price):
    self.mycursor.execute(f"UPDATE product SET product_name = '{product_name}', product_desc = '{product_desc}', product_price = {product_price} WHERE id = {product_id};")
    self.mydb.commit()
  
  
  def insert_product(self, product_name, product_desc, product_price):
    self.mycursor.execute(f"INSERT INTO product (product_name, product_desc, product_price) VALUES ('{str(product_name)}', '{str(product_desc)}', '{str(product_price)}');")
    self.mydb.commit()

  def delete_product(self, product_id):
    self.mycursor.execute(f"DELETE FROM product WHERE id = {product_id};")
    self.mydb.commit()

    
  def select_product(self, product_id):
    self.mycursor.execute(f"SELECT * FROM product WHERE id = {product_id};")
    product = []
    result = self.mycursor.fetchall()
    for row in result:
      product.append(row)
    return product
