""" Routes for the book """

from app import app
from book.models import Book
from user.models import User


@app.route("/dashboard/")
@User.login_required
def dashboard():
    """Dashboard page"""
    return Book().dashboard()


@app.route("/books/")
@User.login_required
def list_books():
    """books page"""
    return Book().list_books()


@app.route("/book/<book_id>/")
@User.login_required
def book_details(book_id):
    """book details"""
    return Book().book_details(book_id)


@app.route("/book/add/", methods=["GET", "POST"])
@User.login_required
@User.admin_required
def add_book():
    """Add new book"""
    return Book().add_book()


@app.route("/book/update/<book_id>/", methods=["GET", "POST"])
@User.login_required
@User.admin_required
def update_book(book_id):
    """book update"""
    return Book().update_book(book_id)


@app.route("/book/delete/<book_id>/")
@User.login_required
@User.admin_required
def delete_book(book_id):
    """book delete"""
    return Book().delete_book(book_id)


@app.route("/search/", methods=["GET"])
@User.login_required
def search_books():
    """search book"""
    return Book().search_books()


@app.route("/book/borrow/<book_id>/")
@User.login_required
def borrow_book(book_id):
    """borrow book"""
    return Book().borrow_book(book_id)


@app.route("/book/return/<record_id>/")
@User.login_required
def return_book(record_id):
    """return book"""
    return Book().return_book(record_id)
