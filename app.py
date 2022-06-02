"""Flask - Library Management System"""

import sys
import logging
from functools import wraps
from bson import ObjectId
from flask import Flask, render_template, request, flash, url_for, redirect, session
import pymongo
from datetime import datetime

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
app.secret_key = b"#\x89q\xe8\xa4;u\xc1[\xab\xe2SE\xe9\xb5*"


client: pymongo.MongoClient = pymongo.MongoClient(host="localhost", port=27017)
db = client["lms"]  # database name

# Routes
from user import routes


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            return redirect("/")

    return wrap


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session["user"] == "admin":
            return f(*args, **kwargs)
        else:
            return redirect("/")

    return wrap


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/dashboard/")
@login_required
def dashboard():

    borrow_history = list(db.borrow_history.find({"user_id": session["user"]["_id"]}))

    for index, record in enumerate(borrow_history):
        borrow_history[index]["book"] = db.books.find_one(
            {"_id": ObjectId(record["book_id"])}
        )

    logger.debug(borrow_history)

    return render_template("dashboard.html", borrow_history=borrow_history)


@login_required
def check_book(book_id: str) -> bool:
    """Check if book exists in database"""

    # Check if book_id is valid ObjectId
    if not ObjectId.is_valid(book_id):
        logger.warning("Invalid book_id: %s", book_id)
        return False

    # Check if book exists
    book = list(db.books.find({"_id": ObjectId(book_id)}))
    if len(book) == 0:
        logger.warning("Book not found: %s", book_id)
        return False

    logger.info("%s book found with id='%s'", len(book), book_id)
    logger.debug("Book: %s", book)
    return True


@app.route("/books")
@login_required
def list_books():
    """books page"""
    books = list(db.books.find())
    logger.debug("%s books found", len(books))
    return render_template("books.html", books=books)


@app.route("/book/<book_id>")
@login_required
def book_details(book_id):
    """book details"""

    book = check_book(book_id)
    if not book:
        flash("Book not found", "danger")
        return redirect(url_for("list_books"))

    logger.info("Book found with id='%s'", book_id)
    return render_template("books.html", book=book)


@app.route("/book/update/<book_id>", methods=["GET", "POST"])
@login_required
def update_book(book_id):
    """book update"""

    # Get book informations from db
    if request.method == "GET":
        book = check_book(book_id)
        if not book:
            flash("Book not found", "danger")
            return redirect(url_for("list_books"))

        book = list(db.books.find({"_id": ObjectId(book_id)}))[0]
        logger.debug("Book: %s", book)
        return render_template("update_book.html", book=book)

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

        logger.debug("Book: %s", request.form)

        # TODO: Validate book informations
        # TODO: image upload

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
                    # "image": image,
                    "quantity": quantity,
                    "price": price,
                }
            },
        )

        logger.info("Updating book with id='%s'", book_id)
        flash("Book updated successfully", "success")
        return redirect(url_for("list_books"))

    else:
        logger.warning("Invalid request method %s", request.method)
        flash("Invalid request method", "danger")
        return redirect(url_for("list_books"))


@app.route("/book/delete/<book_id>")
@login_required
def delete_book(book_id):
    """book delete"""

    book = check_book(book_id)

    if not book:
        flash("Book not found", "danger")
        return redirect(url_for("list_books"))

    db.books.delete_one({"_id": ObjectId(book_id)})

    logger.info("Deleting book with id='%s'", book_id)
    flash("Book deleted successfully", "success")
    return redirect(url_for("list_books"))


@app.route("/book", methods=["GET"])
@login_required
def search_books():
    """Search book"""
    search = request.args.get("search")

    if not search or len(search) < 1:
        return redirect(url_for("list_books"))

    books = list(db.books.find({"title": {"$regex": search, "$options": "i"}}))

    logger.debug("%s books found", len(books))
    if not books:
        flash("Book not found", "danger")
        return redirect(url_for("list_books"))

    flash(f"{len(books)} books found", "success")
    return render_template("books.html", books=books)


@app.route("/book/borrow/<book_id>")
@login_required
def borrow_book(book_id):
    """borrow book"""

    book = check_book(book_id)

    if not book:
        flash("Book not found", "danger")
        return redirect(url_for("list_books"))

    db.borrow_history.insert_one(
        {
            "user_id": session["user"]["_id"],
            "book_id": book_id,
            "borrow_date": datetime.now(),
        }
    )

    logger.info("Borrowing book with id='%s'", book_id)
    flash("Book borrowed successfully", "success")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
