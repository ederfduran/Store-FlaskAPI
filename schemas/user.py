from marshmallow import Schema, fields
from sqlalchemy.orm import load_only

class UserSchema(Schema):
    class Meta:
        load_only = ("password",)
        dump_only = ("id",)
    id = fields.Int()
    username = fields.Str()
    password = fields.Str()