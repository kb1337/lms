"""Flask - Library Management System"""

import sys
import logging
import pymongo
from flask import Flask

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")

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
    logger.debug(str(list(db.books.find())))
    return str(list(db.books.find()))


if __name__ == "__main__":
    app.run()
