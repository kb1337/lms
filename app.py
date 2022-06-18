"""Flask - Library Management System"""

import os
import sys
import logging
from bson import ObjectId
from flask import Flask, render_template, session
import pymongo


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(lineno)d:%(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)

file_handler = logging.FileHandler("logs.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


app = Flask(__name__)
app.secret_key = os.urandom(24)

client: pymongo.MongoClient = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client["lms"]  # database name

# Routes
from user import routes as user_routes
from book import routes as book_routes

from user.models import User


@app.route("/")
def home():
    """Home page"""
    return render_template("home.html")


@app.route("/dashboard/")
@User.login_required
def dashboard():
    """Dashboard page"""

    # FIXME Join books and borrow_history collections
    borrow_history = list(db.borrow_history.find({"user_id": session["user"]["_id"]}))

    for index, record in enumerate(borrow_history):
        borrow_history[index]["book"] = db.books.find_one(
            {"_id": ObjectId(record["book_id"])}
        )

    logger.debug(borrow_history[::-1])
    return render_template("dashboard.html", borrow_history=borrow_history[::-1])


if __name__ == "__main__":
    app.run(debug=True)
