"""Flask - Library Management System"""

import sys
import logging
import pymongo
from bson import ObjectId
from flask import Flask, render_template, Response, request


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s:%(levelname)s:%(name)s:%(message)s", datefmt="%d-%m-%Y %H:%M:%S"
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

client: pymongo.MongoClient = pymongo.MongoClient(host="localhost", port=27017)
db = client["lms"]  # database name


@app.route("/")
def home_page():
    """home page"""
    return render_template("index.html")


@app.route("/books")
def list_books():
    """books page"""
    books = list(db.books.find())
    logger.debug("%s books found", len(books))
    return render_template("books.html", books=books)


@app.route("/book/<book_id>", methods=["GET", "POST", "DELETE"])
def book_actions(book_id):
    """update book"""

    # Check if book_id is valid ObjectId
    if not ObjectId.is_valid(book_id):
        return Response("Invalid book id", status=400)

    # Check if book exists
    book = list(db.books.find({"_id": ObjectId(book_id)}))
    if len(book) == 0:
        logger.error("Invalid book id")
        return Response("Book not found", status=404)
    logger.info("%s book found with id='%s'", len(book), book_id)

    # Get book informations from db
    if request.method == "GET":
        return render_template("update_book.html", book=book[0])

    # Update book with new values
    elif request.method == "POST":
        # TODO: update book

        logger.info("Updating book with id='%s'", book_id)
        return Response("Book updated", status=200)

    # Delete book
    elif request.method == "DELETE":
        # TODO: delete book

        logger.info("Deleting book with id='%s'", book_id)
        return Response("Book deleted", status=200)

    else:
        return Response("Method not allowed", status=405)


# TODO: Search book by any field


if __name__ == "__main__":
    app.run(debug=True)
