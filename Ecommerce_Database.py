import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Tipaktop11!",
  database="mydatabase"
)

mycursor = mydb.cursor()

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE IF NOT EXISTS mydatabase")

mycursor.execute("CREATE TABLE IF NOT EXISTS user (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), email VARCHAR(255), password VARCHAR(8), is_admin BOOLEAN)")

mycursor.execute("CREATE TABLE IF NOT EXISTS product (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), description VARCHAR(255), price FLOAT, img BLOB)")

