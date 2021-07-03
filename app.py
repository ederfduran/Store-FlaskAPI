from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from db import db
from blacklist import BLACKLIST
from resources.user import UserRegister, UserLogin, User, TokenRefresh, UserLogout
from resources.item import Item, ItemList
from resources.store import Store, StoreList

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

# what extra information to add to the JWT 
@jwt.additional_claims_loader
def add_claims_to_jwt(identity): # identity is what we define when creating the access token
    if ( identity == 1):  # instead of hard-coding, we should read from a file or database to get a list of admins instead
        return {"is_admin": True}
    return {"is_admin": False}


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    print(jwt_payload["type"])
    return (
        # BLACKLIST shall be replaced with some cache like Redis
        jwt_payload["jti"] in BLACKLIST
    )  # Here we blacklist particular JWTs that have been created in the past.


# The following callbacks are used for customizing jwt response/error messages.
# The original ones may not be in a very pretty format (opinionated)
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401


# we have to keep the argument here, since it's passed in by the caller internally
@jwt.invalid_token_loader
def invalid_token_callback(error):  
    return (
        jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        401,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return (
        jsonify(
            {"description": "The token is not fresh.", "error": "fresh_token_required"}
        ),
        401,
    )


@jwt.revoked_token_loader
def revoked_token_callback():
    return (
        jsonify(
            {"description": "The token has been revoked.", "error": "token_revoked"}
        ),
        401,
    )

# All methods implemented in Store resource under 
# this path must receive name as parameter ,
# same thing for other resources
api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
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
