# Blog Website using Flask
 Blog Website using Flask as a framework

# Installation
Install neccessary library
```shell
pip install Flask
pip install Flask-SQLAlchemy
```

# Run the app

Create db
```shell
python models.py
```

Run app
```shell
python app.py
```

Note for database migration
1. Initialize database migration
```shell
flask db init
```
2. Create first migration
```shell
flask db migrate -m "Initial migration."
```
3. Upgrade db
```shell
flask db upgrade
```
Database migration is used when you need to change structure of database's tables without losing data already saved in that database, no need to recreate that database.
