import requests

from collections import defaultdict
from datetime import datetime
from psycopg2 import pool
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from logic import BOUGHT, SOLD
from logic import format_db_row_to_transaction

postgreSQL_pool = pool.SimpleConnectionPool(
    1,
    20,
    database="exampledb",
    user="docker",
    password="docker",
    host="127.0.0.1"
)

app = Flask(__name__)
cors = CORS(app)

app.config['postgreSQL_pool'] = postgreSQL_pool


@app.route("/")
def health_check():
    return "I am healthy!!!"

@app.route("/transactions", methods=["POST"])
def new_transaction():
    name = request.json["name"]
    symbol = request.json["symbol"]
    type = request.json["type"]
    amount = request.json["amount"]
    time_transacted = datetime.fromtimestamp(request.json["time_transacted"])
    time_created = datetime.fromtimestamp(request.json["time_created"])
    price_purchased_at = float(request.json["price_purchased_at"])
    no_of_coins = float(request.json["no_of_coins"])
    
    conn = postgreSQL_pool.getconn()
    cur = conn.cursor()
    
    insert_statement = f"insert into transaction (name, symbol, type, amount, time_transacted, time_created, price_purchased_at, no_of_coins) VALUES ('{name}', '{symbol}', '{type}', '{amount}', '{time_transacted}', '{time_created}', '{price_purchased_at}', '{no_of_coins}')"
    cur.execute(insert_statement)
    conn.commit()
    
    return jsonify(request.json)

@app.route("/transactions")
@cross_origin()
def get_transaction():
    cur = postgreSQL_pool.getconn().cursor()
    cur.execute("select * from transaction")
    rows = cur.fetchall()
    
    
    return jsonify(
        (
            format_db_row_to_transaction(row)
            for row in rows
        )
    )
app.run(debug=True, port=5000)