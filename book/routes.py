""" Routes for the book """

from app import app
from book.models import Book


@app.route("/books")
def list_books():
    """books page"""
    return Book().list_books()


@app.route("/book/<book_id>")
# @login_required
def book_details(book_id):
    """book details"""
    return Book().book_details(book_id)


@app.route("/book/update/<book_id>", methods=["GET", "POST"])
# @login_required
def update_book(book_id):
    """book update"""
    return Book().update_book(book_id)


@app.route("/book/delete/<book_id>")
# @login_required
def delete_book(book_id):
    """book delete"""
    return Book().delete_book(book_id)


@app.route("/search", methods=["GET"])
# @login_required
def search_books():
    """search book"""
    return Book().search_books()


@app.route("/book/borrow/<book_id>")
# @login_required
def borrow_book(book_id):
    """borrow book"""
    return Book().borrow_book(book_id)


@app.route("/book/return/<record_id>")
# @login_required
def return_book(record_id):
    """return book"""
    return Book().return_book(record_id)
