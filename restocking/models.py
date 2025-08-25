from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Supplier(db.Model):
    __tablename__ = "suppliers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(64))
    notes = db.Column(db.Text, nullable=True)
    items = db.relationship("Item", backref="supplier", cascade="all, delete-orphan")


class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False)
    name = db.Column(db.String(160), nullable=False)
    unit = db.Column(db.String(32), nullable=False)  # kg, pkt, carton, tin
    default_qty = db.Column(db.Float, nullable=False, default=1)
    item_type = db.Column(db.String(64), nullable=True)  # Dry, Frozen, Vegetables, etc.
    active = db.Column(db.Boolean, nullable=False, default=True)

    __table_args__ = (
        db.UniqueConstraint("supplier_id", "name", name="uq_item_per_supplier"),
    )


class Outlet(db.Model):
    __tablename__ = "outlets"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text, nullable=True)
