"""Flask - Library Management System"""

import sys
import logging
import pymongo
from flask import Flask, render_template


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")

file_handler = logging.FileHandler("logs.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


app = Flask(__name__)

client: pymongo.MongoClient = pymongo.MongoClient(host="localhost", port=27017)
db = client.lms


@app.route("/")
def home_page():
    """home page"""
    return render_template("index.html")


@app.route("/books")
def book_list():
    """books page"""
    books = list(db.books.find())
    logger.debug("%s books found", len(books))
    return render_template("books.html", books=books)


if __name__ == "__main__":
    app.run()
