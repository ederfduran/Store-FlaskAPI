from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from db import db
from blacklist import BLACKLIST
from resources.user import UserRegister, UserLogin, User, TokenRefresh, UserLogout


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(user='root', password='rootpassword', server='localhost', database='flask_examples')

# keeps track of changes to SQLAlchemy models.(for Flask-SQLAlchemy event system)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#  it is needed for Flask-RESTful exceptions to show up in our app as errors instead 
#  of crashing our server with a generic "Internal Server Error").
app.config["PROPAGATE_EXCEPTIONS"] = True

app.config["JWT_SECRET_KEY"] = "super-secret" #TODO Change this!

api = Api(app)


@app.before_first_request
def create_tables():
    # create all our tables in the database 
    # This only runs if there is no tables already created
    db.create_all()


jwt = JWTManager(app)


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    print(jwt_payload["type"])
    return (
        # BLACKLIST shall be replaced with some cache like Redis
        jwt_payload["jti"] in BLACKLIST
    )  # Here we blacklist particular JWTs that have been created in the past.



api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserLogout, "/logout")


#In Python, if __name__ == "__main__": 
# is a frequently used construct that means 
# the subsequent code block only runs if this 
# file was executed. It does not run if the file was imported.
if __name__ == "__main__":
    db.init_app(app)
    app.run(port=5000, debug=True)
