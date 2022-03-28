# Photoshare

## MySQL + Flask image sharing website

### **DISCLAIMER**: The raw SQL queries that include user input are strictly for demonstration and are entirely vulnerable to SQL Injection attacks. Do not reuse this code in anything important!
---
## Setup

### 1.
`pip install -r requirements.txt`

### 2. Mac, Linux
`export FLASK_APP=app.py`

### 2. Windows
`set FLASK_APP=app.py`

### 3.
Execute `schema.sql` with MySQL Workbench

### 4. app.py
Change `app.config['MYSQL_DATABASE_PASSWORD']` to your MySQL root password

### 5.
`python -m flask run`

### Development server
http://localhost:5000
