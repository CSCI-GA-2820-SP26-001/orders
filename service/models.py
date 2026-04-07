"""
Models for Order
All of the models are stored in this module
"""

import logging
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Order(db.Model):
    """
    Class that represents a Order"""

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(63))
    address = db.Column(db.String(256))
    email = db.Column(db.String(256))
    status = db.Column(db.String(64), nullable=False, default="Unprocessed")
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    items = db.relationship("Item", backref="order", cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<Order {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Order to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Order to the database
        """
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Order from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Order into a dictionary"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "name": self.name,
            "address": self.address,
            "email": self.email,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "items": [item.serialize() for item in self.items],
        }

    def deserialize(self, data):
        """
        Deserializes a Order from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id = data["customer_id"]
            self.name = data["name"]
            self.address = data["address"]
            self.email = data["email"]
            self.status = data.get("status", "Unprocessed")
            if "items" in data:
                self.items = []
                for item_data in data["items"]:
                    item = Item()
                    item.deserialize(item_data)
                    self.items.append(item)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Order: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order: body of request contained bad or no data " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Orders in the database"""
        logger.info("Processing all Orders")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Order by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Orders with the given name

        Args:
            name (string): the name of the Orders you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_status(cls, order_status):
        logger.info("Processing status query for %s ...", order_status)
        return cls.query.filter(cls.status == order_status)

    @classmethod
    def find_by_customer_id(cls, customer_id):
        logger.info("Processing customer_id query for %s ...", customer_id)
        return cls.query.filter(cls.customer_id == customer_id)


class Item(db.Model):
    """Class that represents an Item within an Order"""

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("order.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(63), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Item {self.name} id=[{self.id}] order_id=[{self.order_id}]>"

    def create(self):
        """Creates an Item to the database"""
        logger.info("Creating Item %s", self.name)
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating Item: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """Updates an Item in the database"""
        logger.info("Saving Item %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating Item: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes an Item from the data store"""
        logger.info("Deleting Item %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting Item: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes an Item into a dictionary"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price,
        }

    def deserialize(self, data):
        """Deserializes an Item from a dictionary"""
        try:
            self.name = data["name"]
            self.quantity = data["quantity"]
            self.price = data["price"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid Item: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained bad or no data " + str(error)
            ) from error

        if not isinstance(self.quantity, int) or self.quantity <= 0:
            raise DataValidationError("Invalid Item: quantity must be a positive integer")
        if not isinstance(self.price, (int, float)) or self.price <= 0:
            raise DataValidationError("Invalid Item: price must be a positive number")

        return self

    @classmethod
    def find(cls, by_id):
        """Finds an Item by its ID"""
        logger.info("Processing lookup for item id %s ...", by_id)
        return cls.query.session.get(cls, by_id)
