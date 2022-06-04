"""Book model"""

from datetime import datetime
import logging
import sys
from flask import request, session, redirect, url_for, flash, render_template
from bson import ObjectId

from app import db


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


class Book:
    """Book model"""

    def check_book(self, book_id: str) -> bool:
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

    def list_books(self):
        """List all books"""
        books = list(db.books.find())
        logger.debug("%s books found", len(books))
        return render_template("books.html", books=books)

    def book_details(self, book_id):
        """Show book details"""

        if not self.check_book(book_id):
            flash("Book not found", "danger")
            return redirect(url_for("list_books"))

        book = db.books.find_one({"_id": ObjectId(book_id)})

        logger.info("Book: %s", book)
        return render_template("book_details.html", book=book)

    def update_book(self, book_id):
        """Updates book by book_id"""

        # Get book informations from db
        if request.method == "GET":
            if not self.check_book(book_id):
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

            # TODO: validate data
            # TODO: image upload

            logger.debug("Book: %s", request.form)

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
                        "quantity": int(quantity),
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

    def delete_book(self, book_id):
        """Deletes book by book_id"""

        book = self.check_book(book_id)

        if not book:
            flash("Book not found", "danger")
            return redirect(url_for("list_books"))

        db.books.delete_one({"_id": ObjectId(book_id)})

        logger.info("Deleting book with id='%s'", book_id)
        flash("Book deleted successfully", "success")
        return redirect(url_for("list_books"))

    def search_books(self):
        """Search books by any field"""
        search = request.args.get("search")

        if not search or len(search) < 1:
            return redirect(url_for("list_books"))

        books = list(
            db.books.find(
                {
                    "$or": [
                        {"authors": {"$in": [search]}},
                        {"editors": {"$in": [search]}},
                        {"edition": {"$regex": search, "$options": "i"}},
                        {"title": {"$regex": search, "$options": "i"}},
                        {"language": {"$regex": search, "$options": "i"}},
                        {"isbn": {"$regex": search, "$options": "i"}},
                        {"publisher": {"$regex": search, "$options": "i"}},
                        {"page": search},
                        {"year": search},
                    ]
                }
            )
        )

        logger.debug("%s books found", len(books))
        if not books:
            flash("Book not found", "danger")
            return redirect(url_for("list_books"))

        flash(f"{len(books)} books found", "success")
        return render_template("books.html", books=books)

    def borrow_book(self, book_id):
        """Borrow book by book_id"""

        if not self.check_book(book_id):
            flash("Book not found", "danger")
            return redirect(url_for("list_books"))

        # Check if book is available
        book = list(db.books.find({"_id": ObjectId(book_id)}))[0]
        if book["quantity"] <= 0:
            flash("Book is not available", "danger")
            return redirect(url_for("list_books"))

        # Update book quantity
        db.books.update_one({"_id": ObjectId(book_id)}, {"$inc": {"quantity": -1}})

        # Add borrow history
        db.borrow_history.insert_one(
            {
                "user_id": session["user"]["_id"],
                "book_id": ObjectId(book_id),
                "borrow_date": datetime.now(),
            }
        )

        logger.info("Borrowing book with id='%s'", book_id)
        flash("Book borrowed successfully", "success")
        return redirect(url_for("dashboard"))

    def return_book(self, record_id):
        """Return book by borrow history record_id"""

        # Check if record_id is valid ObjectId
        if not ObjectId.is_valid(record_id):
            flash("Invalid record id", "danger")
            return redirect(url_for("dashboard"))

        record = db.borrow_history.find_one({"_id": ObjectId(record_id)})
        logger.debug(record)

        if not record:
            flash("Book not found", "danger")
            return redirect(url_for("list_books"))

        book_id = record["book_id"]

        # Check if book returned before
        if "return_date" in record.keys():
            flash("Book is already returned", "danger")
            return redirect(url_for("dashboard"))

        # Update book quantity
        db.books.update_one({"_id": ObjectId(book_id)}, {"$inc": {"quantity": 1}})

        db.borrow_history.update_one(
            {"_id": ObjectId(record_id)},
            {"$set": {"return_date": datetime.now()}},
        )
        logger.info("return_date updated from borrow history. Record ID: '%s'", book_id)

        flash("Book returned successfully", "success")
        return redirect(url_for("dashboard"))
