from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models.item import ItemModel

BLANK_ERROR = " '{}' This field cannot be left blank!"
NAME_ALREADY_EXISTS = "An item with name '{}' already exists."
ERROR_INSERTING = "An error occurred while inserting the item."
ITEM_NOT_FOUND = "Item not found."
ITEM_DELETED = "Item deleted."

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price", type=float, required=True, help=BLANK_ERROR.format("price")
    )
    parser.add_argument(
        "store_id", type=int, required=True, help=BLANK_ERROR.format("store_id")
    )

    def get(self, name:str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        return {"message": ITEM_NOT_FOUND}, 404

    # highly sensitive endpoint as it require a fresh JWT
    # cannot be a JWT generated via the Token Refresh functionality.
    # A fresh token is the most secure token since it means the user just authenticated
    @jwt_required(fresh=True)
    def post(self, name:str):
        if ItemModel.find_by_name(name):
            return {"message": NAME_ALREADY_EXISTS.format(name)}, 400
        # Retrieves method payload
        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except Exception as ex:
            print(ex.args)
            return {"message": ERROR_INSERTING}, 500

        return item.json(), 201

    #  JWT must have a claim stating that is_admin is True
    #  Claims are arbitrary pieces of data that can be included 
    #  in the JWT when it is created
    @jwt_required
    def delete(self, name:str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": ITEM_DELETED}, 200
        return {"message": ITEM_NOT_FOUND}, 404

    def put(self, name:str):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data["price"]
        else:
            item = ItemModel(name, **data)

        item.save_to_db()

        return item.json(), 200


class ItemList(Resource):
    # optional can be very handy if you want loggedd-out users 
    # to be able to see some data, but allow logged-in users see more data
    def get(self):
        items = [item.json() for item in ItemModel.find_all()]
        return {"items": items}, 200
    
