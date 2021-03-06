"""Routes for the user"""

from app import app
from user.models import User


@app.route("/user/signup/", methods=["POST"])
def signup():
    """signup"""
    return User().signup()


@app.route("/user/signout/")
def signout():
    """signout"""
    return User().signout()


@app.route("/user/login/", methods=["POST"])
def login():
    """login"""
    return User().login()
