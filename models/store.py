from db import db


class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    # SQLAlchemy is smart enough to be able to construct a many-to-one relationship from this
    items = db.relationship("ItemModel", lazy="dynamic")

    def __init__(self, name):
        self.name = name

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            # .all() needed when lazy="dynamic"
            # .all() makes it go into the database and retrieve all the items
            # "lazy" property because the items are not loaded until we do .all()
            "items": [item.json() for item in self.items.all()],
        }

    @classmethod
    def find_by_name(cls, name)-> "StoreModel":
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
