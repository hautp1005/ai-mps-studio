"""
where we'll define environment-specific configuration variables
Here, the database is configured based on the DATABASE_URL environment variable that we just defined.
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/project/static"
    MEDIA_FOLDER = f"{os.getenv('APP_FOLDER')}/project/media"
    PROJECTS_TESTING_FOLDER = f"{os.getenv('APP_FOLDER')}/project/autotest"
