"""Flask - Library Management System"""

import sys
import logging
import pymongo
from bson import ObjectId
from flask import Flask, render_template, request, flash, url_for, redirect


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
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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


@app.route("/book/<book_id>")
def book_details(book_id):
    """book details"""

    # Check if book_id is valid ObjectId
    if not ObjectId.is_valid(book_id):
        flash("Invalid book id", "danger")
        return redirect(url_for("list_books"))

    book = list(db.books.find({"_id": ObjectId(book_id)}))
    if len(book) == 0:
        logger.error("Book not found")
        flash("Book not found", "danger")
        return redirect(url_for("list_books"))

    logger.info("%s book found with id='%s'", len(book), book_id)
    return render_template("books.html", book=book)


@app.route("/book/update/<book_id>", methods=["GET", "POST"])
def update_book(book_id):
    """book update"""

    # Check if book_id is valid ObjectId
    if not ObjectId.is_valid(book_id):
        flash("Invalid book id", "danger")
        return redirect(url_for("list_books"))

    # Check if book exists
    book = list(db.books.find({"_id": ObjectId(book_id)}))
    if len(book) == 0:
        logger.error("Invalid book id")
        flash("Book not found", "danger")
        return redirect(url_for("list_books"))
    logger.info("%s book found with id='%s'", len(book), book_id)

    # Get book informations from db
    if request.method == "GET":
        return render_template("update_book.html", book=book[0])

    # Update book with new values
    elif request.method == "POST":
        title = request.form.get("title")
        authors = request.form.get("authors")
        editors = request.form.get("editors")
        isbn = request.form.get("isbn")
        year = request.form.get("year")
        edition = request.form.get("edition")
        publisher = request.form.get("publisher")
        page = request.form.get("page")
        language = request.form.get("language")
        image = request.form.get("image")
        quantity = request.form.get("quantity")
        price = request.form.get("price")

        # TODO: Validate book informations

        authors = str(authors).split(",")
        authors = [author.strip() for author in authors]
        editors = str(editors).split(",")
        editors = [editor.strip() for editor in editors]

        db.books.update_one(
            {"_id": ObjectId(book_id)},
            {
                "$set": {
                    "title": title,
                    "authors": authors,
                    "editors": editors,
                    "isbn": isbn,
                    "year": year,
                    "edition": edition,
                    "publisher": publisher,
                    "page": page,
                    "language": language,
                    "image": image,
                    "quantity": quantity,
                    "price": price,
                }
            },
        )

        logger.info("Updating book with id='%s'", book_id)
        flash("Book updated successfully", "success")
        return redirect(url_for("list_books"))

    else:
        logger.error("Invalid request method")
        flash("Invalid request method", "danger")
        return redirect(url_for("list_books"))


@app.route("/book/delete/<book_id>")
def delete_book(book_id):
    """book delete"""

    # Check if book_id is valid ObjectId
    if not ObjectId.is_valid(book_id):
        flash("Invalid book id", "danger")
        return redirect(url_for("list_books"))

    # Check if book exists
    book = list(db.books.find({"_id": ObjectId(book_id)}))
    if len(book) == 0:
        logger.error("Invalid book id")
        flash("Book not found", "danger")
        return redirect(url_for("list_books"))
    logger.info("%s book found with id='%s'", len(book), book_id)

    db.books.delete_one({"_id": ObjectId(book_id)})

    logger.info("Deleting book with id='%s'", book_id)
    flash("Book deleted successfully", "success")
    return redirect(url_for("list_books"))


# TODO: Search book by any field


if __name__ == "__main__":
    app.run(debug=True)
