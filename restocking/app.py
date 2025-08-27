import re
import os
from datetime import datetime, timedelta
from urllib.parse import quote_plus

from flask import Flask, render_template, request, redirect, url_for, flash
from flask.cli import with_appcontext
from flask_migrate import Migrate

from config import Config, ProdConfig
from models import db, Supplier, Item, Outlet


def _digits_only(phone: str) -> str:
    # keep only digits for https://wa.me/
    return re.sub(r"\D", "", phone or "")

# This creates a reference number starting with prefix PO
def _po_ref(prefix="PO"):
    return f"{prefix}-{datetime.now().strftime('%Y-%m-%d-' '%H%M')}"

# This function builds the whatsapp message
def _build_whatsapp_text(outlet_name, items, notes, address="", delivery_date=""):
    lines = []
    lines.append(f"*Order from: {outlet_name}*")
    if address:
        lines.append(f"Address: {address}")
    if delivery_date:
        lines.append(f"Date of Delivery: {delivery_date}")
        # Emphasize if not next day
        try:
            delivery_dt = datetime.strptime(delivery_date, "%Y-%m-%d").date()
            if delivery_dt != (datetime.utcnow().date() + timedelta(days=1)):
                lines.append("❗️Order is NOT for next day!")
        except Exception:
            pass
    lines.append("")
    lines.append("Items:")
    for it in items:
        lines.append(f"- {it['name']}: {it['qty']} {it['unit']}")
    if notes:
        lines.append("")
        lines.append(f"Notes: {notes}")
    lines.append(f"PO Ref: {_po_ref('SR')}")
    return "\n".join(lines)

# This creates the app using the config
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate = Migrate(app, db) 

    # Allows initiating the db via $flask init-db
    @app.cli.command("init-db")
    @with_appcontext
    def init_db():
        db.create_all()
        print("DB initialized")

    # ---- Suppliers (list + quick create) ----
    @app.get("/")
    def suppliers_list():
        # Have a search bar(query) so if there are many more suppliers, we can filter them
        q = (request.args.get("q") or "").strip()
        qry = Supplier.query
        if q:
            qry = qry.filter(Supplier.name.ilike(f"%{q}%"))
        suppliers = qry.order_by(Supplier.name.asc()).all()
        return render_template("suppliers_list.html", suppliers=suppliers, q=q)
    # To create new suppliers
    @app.post("/suppliers/new")
    def suppliers_create():
        name = (request.form.get("name") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        category = (request.form.get("category") or "").strip()
        if not name:
            flash("Supplier name is required", "error")
            return redirect(url_for("suppliers_list"))
        # Write into db the Supplier table with their corresponding columns
        s = Supplier(name=name, phone=phone, category=category)
        db.session.add(s)
        db.session.commit()
        flash("Supplier created", "ok")
        return redirect(url_for("supplier_items", supplier_id=s.id))

    @app.get("/suppliers/new")
    def supplier_new_form():
        return render_template("add_supplier.html")
    # This function is for editing suppliers by getting current info and posting new updates 
    @app.route("/suppliers/<int:supplier_id>/edit", methods=["GET", "POST"])
    def edit_supplier(supplier_id):
        supplier = Supplier.query.get_or_404(supplier_id)
        if request.method == "POST":
            supplier.name = request.form.get("name", supplier.name)
            supplier.phone = request.form.get("phone", supplier.phone)
            supplier.category = request.form.get("category", supplier.category)
            db.session.commit()
            flash("Supplier updated!", "ok")
            return redirect(url_for("suppliers_list"))
        return render_template("edit_supplier.html", supplier=supplier)
    # This is for deleting a supplier
    @app.post("/suppliers/<int:supplier_id>/delete")
    def supplier_delete(supplier_id):
        supplier = Supplier.query.get_or_404(supplier_id)
        db.session.delete(supplier)
        db.session.commit()
        flash("Supplier deleted", "ok")
        return redirect(url_for("suppliers_list"))

    # Items for current supplier
    @app.get("/suppliers/<int:supplier_id>/items")
    def supplier_items(supplier_id):
        supplier = Supplier.query.get_or_404(supplier_id)
        items = (
            Item.query.filter_by(supplier_id=supplier.id, active=True)
            .order_by(Item.name.asc())
            .all()
        )
        return render_template("items_list.html", supplier=supplier, items=items)

    # This is to generate a new item for a supplier, if get, give the form, if post, write into db
    @app.get("/suppliers/<int:supplier_id>/items/new")
    def item_new(supplier_id):
        supplier = Supplier.query.get_or_404(supplier_id)
        return render_template("item_form.html", supplier=supplier, item=None)

    @app.post("/suppliers/<int:supplier_id>/items/new")
    def item_create(supplier_id):
        supplier = Supplier.query.get_or_404(supplier_id)
        name = (request.form.get("name") or "").strip()
        unit = (request.form.get("unit") or "").strip()
        default_qty_raw = (request.form.get("default_qty") or "1").strip()
        item_type = (request.form.get("item_type") or "").strip()

        if not name or not unit:
            flash("Name and unit are required", "error")
            return redirect(url_for("item_new", supplier_id=supplier.id))

        try:
            dq = float(default_qty_raw)
            if dq <= 0:
                raise ValueError
        except ValueError:
            flash("Default qty must be a positive number", "error")
            return redirect(url_for("item_new", supplier_id=supplier.id))

        new_item = Item(
            supplier_id=supplier.id,
            name=name,
            unit=unit,
            default_qty=dq,
            item_type=item_type,
        )
        db.session.add(new_item)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("There is already an item with this name for the supplier", "error")
            return redirect(url_for("item_new", supplier_id=supplier.id))

        flash("Item added", "ok")
        return redirect(url_for("supplier_items", supplier_id=supplier.id))
    # This is for editing an item, get the form filled in, then post for edits
    @app.get("/items/<int:item_id>/edit")
    def item_edit(item_id):
        item_obj = Item.query.get_or_404(item_id)
        return render_template(
            "item_form.html", supplier=item_obj.supplier, item=item_obj
        )

    @app.post("/items/<int:item_id>/edit")
    def item_update(item_id):
        item_obj = Item.query.get_or_404(item_id)
        name = (request.form.get("name") or "").strip()
        unit = (request.form.get("unit") or "").strip()
        default_qty_raw = (request.form.get("default_qty") or "1").strip()
        item_type = (request.form.get("item_type") or "").strip()
        active = request.form.get("active") == "on"

        if not name or not unit:
            flash("Name and unit are required", "error")
            return redirect(url_for("item_edit", item_id=item_obj.id))

        try:
            dq = float(default_qty_raw)
            if dq <= 0:
                raise ValueError
        except ValueError:
            flash("Default qty must be a positive number", "error")
            return redirect(url_for("item_edit", item_id=item_obj.id))

        item_obj.name = name
        item_obj.unit = unit
        item_obj.default_qty = dq
        item_obj.item_type = item_type
        item_obj.active = active

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Item name must be unique per supplier", "error")
            return redirect(url_for("item_edit", item_id=item_obj.id))

        flash("Item updated", "ok")
        return redirect(url_for("supplier_items", supplier_id=item_obj.supplier_id))
    # Deleting an item
    @app.post("/items/<int:item_id>/delete")
    def item_delete(item_id):
        item = Item.query.get_or_404(item_id)
        supplier_id = item.supplier_id
        db.session.delete(item)
        db.session.commit()
        flash("Item deleted!", "ok")
        return redirect(url_for("supplier_items", supplier_id=supplier_id))

    # This is for creating a new order
    @app.get("/suppliers/<int:supplier_id>/order")
    def order_form(supplier_id):
        supplier = Supplier.query.get_or_404(supplier_id)
        items = Item.query.filter_by(supplier_id=supplier.id, active=True).order_by(Item.name.asc()).all()
        outlets = Outlet.query.order_by(Outlet.name.asc()).all()
        return render_template(
            "order_form.html",
            supplier=supplier,
            items=items,
            outlets=outlets,
            datetime=datetime,
            timedelta=timedelta
        )
    # Posting in suppliers will give preview of order
    @app.post("/suppliers/<int:supplier_id>/order/preview")
    def order_preview(supplier_id):
        supplier = Supplier.query.get_or_404(supplier_id)
        outlet_name = request.form.get("outlet_name", "").strip()
        address = request.form.get("address", "").strip()
        notes = request.form.get("notes", "").strip()
        delivery_date = request.form.get("delivery_date", "")  # <-- get date from form

        # Fetch the outlet from the database
        outlet = Outlet.query.filter_by(name=outlet_name).first()
        address = outlet.address if outlet else ""

        selected = []
        for key, val in request.form.items():
            # inputs are named qty_<item_id>
            m = re.match(r"qty_(\d+)$", key)
            if not m:
                continue
            try:
                qty = float(val)  # <-- use float, not int
            except (TypeError, ValueError):
                qty = 0
            if qty <= 0:
                continue
            item_id = int(m.group(1))
            it = Item.query.get(item_id)
            if it and it.supplier_id == supplier.id and it.active:
                selected.append({"id": it.id, "name": it.name, "unit": it.unit, "qty": qty})

        if not selected:
            flash("Pick at least one item (qty > 0).", "error")
            return redirect(url_for("order_form", supplier_id=supplier.id))

        text = _build_whatsapp_text(outlet_name, selected, notes, address, delivery_date)
        encoded = quote_plus(text)
        phone = _digits_only(supplier.phone)
        wa_url = (
            f"https://wa.me/{phone}?text={encoded}"
            if phone
            else f"https://wa.me/?text={encoded}"
        )

        return render_template(
            "order_preview.html",
            supplier=supplier,
            outlet_name=outlet_name,
            address=address,
            notes=notes,
            delivery_date=delivery_date,  # <-- pass to template
            items=selected,
            wa_url=wa_url,
            text=text,
        )

    # This is to setup the outlet
    @app.route("/outlet/setup", methods=["GET", "POST"])
    def outlet_setup():
        outlet = Outlet.query.first()
        if request.method == "POST":
            if not outlet:
                outlet = Outlet()
                db.session.add(outlet)
            outlet.name = request.form.get("name", "")
            outlet.address = request.form.get("address", "")
            outlet.notes = request.form.get("notes", "")
            db.session.commit()
            flash("Outlet details updated!", "ok")
            return redirect(url_for("outlet_setup"))
        return render_template("outlet_form.html", outlet=outlet)

    @app.route("/suppliers/<int:supplier_id>/items/add", methods=["GET", "POST"])
    def add_item(supplier_id):
        supplier = Supplier.query.get_or_404(supplier_id)
        if request.method == "POST":
            name = request.form.get("name")
            unit = request.form.get("unit")
            default_qty = request.form.get("default_qty", type=float)
            item_type = request.form.get("item_type")
            item = Item(
                name=name,
                unit=unit,
                default_qty=default_qty,
                item_type=item_type,
                supplier_id=supplier.id,
                active=True
            )
            db.session.add(item)
            db.session.commit()
            flash("Item added!", "ok")
            return redirect(url_for("supplier_items", supplier_id=supplier.id))
        return render_template("add_item.html", supplier=supplier)

    return app


# Choose config based on environment variable
if os.getenv("FLASK_ENV") == "production":
    app = create_app(ProdConfig)
else:
    app = create_app(Config)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)