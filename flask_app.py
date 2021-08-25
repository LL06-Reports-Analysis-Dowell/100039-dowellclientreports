
# A very simple Flask Hello World app for you to get started with...

from typing import List, Tuple

import pymongo

from flask import Flask, render_template, request

app = Flask(__name__)

def db_connect(id: str) -> Tuple[List[str], List[int]]:
    # replace the connection string with yours
    client = pymongo.MongoClient("mongodb+srv://qruser:qr1234@cluster0.n2ih9.mongodb.net/BD_IMAGE?retryWrites=true&w=majority")
    # replace "GettingStarted" with the name of your db and "clients" with the name of the collection of clients
    db = client.client_data
    clients = db.client_login
    # "_id" is the default parameter of any document on MongoDB and in this case it should be filled with the client's email
    query = clients.find_one({ "_id": id })
    keys = [i for i in query.keys()]
    values = [i for i in query.values()]
    return keys, values


@app.route("/")
def load_html():
    return render_template("index.html", display = "hidden-container")

@app.route("/data", methods = ["GET", "POST"])
def display_charts():
    if request.method == "POST":
        id = request.form.get("email")
        keys, values = db_connect(id)
        return render_template(
            "index.html",
            display = "flex-container",
            key_1 = keys[1],
            key_2 = keys[2],
            key_3 = keys[3],
            key_4 = keys[4],
            key_5 = keys[5],
            key_6 = keys[6],
            key_7 = keys[7],
            val_1 = values[1],
            val_2 = values[2],
            val_3 = values[3],
            val_4 = values[4],
            val_5 = values[5],
            val_6 = values[6],
            val_7 = values[7]
        )

