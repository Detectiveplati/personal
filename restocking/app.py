import re
from datetime import datetime
from urllib.parse import quote_plus

from flask import Flask, render_template, request, redirect, url_for, flash
from flask.cli import with_appcontext

from config import Config
from models import db, Supplier, Item


def _digits_only(phone: str) -> str:
    # keep only digits for https://wa.me/
    return re.sub(r"\D", "", phone or "")


def _po_ref(prefix="SR"):
    return f"{prefix}-{datetime.now().strftime('%Y-%m-%d-%H%M')}"


def _build_whatsapp_text(outlet_name: str, items, notes: str):
    # items = list[dict{name, qty, unit}]
    lines = []
    lines.append(f"*Order from: {outlet_name}*")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append("Items:")
    for it in items:
        lines.append(f"- {it['name']}: {it['qty']} {it['unit']}")
    if notes:
        lines.append("")
        lines.append(f"Notes: {notes}")
    lines.append(f"PO Ref: {_po_ref('SR')}")
    return "\n".join(lines)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # ---- CLI: flask init-db ----
    @app.cli.command("init-db")
    @with_appcontext
    def init_db():
        db.create_all()
        print("DB initialized")

    # ---- Suppliers (list + quick create) ----
    @app.get("/")
    def suppliers_list():
        q = (request.args.get("q") or "").strip()
        qry = Supplier.query
        if q:
            qry = qry.filter(Supplier.name.ilike(f"%{q}%"))
        suppliers = qry.order_by(Supplier.name.asc()).all()
        return render_template("suppliers_list.html", suppliers=suppliers, q=q)

    @app.post("/suppliers/new")
    def suppliers_create():
        name = (request.form.get("name") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        category = (request.form.get("category") or "").strip()
        if not name:
            flash("Supplier name is required", "error")
            return redirect(url_for("suppliers_list"))

        s = Supplier(name=name, phone=phone, category=category)
        db.session.add(s)
        db.session.commit()
        flash("Supplier created", "ok")
        return redirect(url_for("supplier_items", supplier_id=s.id))

    # ---- Items per supplier ----
    @app.get("/suppliers/<int:supplier_id>/items")
    def supplier_items(supplier_id):
        supplier = Supplier.query.get_or_404(supplier_id)
        items = (
            Item.query.filter_by(supplier_id=supplier.id, active=True)
            .order_by(Item.name.asc())
            .all()
        )
        return render_template("items_list.html", supplier=supplier, items=items)

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
            dq = int(default_qty_raw)
            if dq <= 0:
                raise ValueError
        except ValueError:
            flash("Default qty must be a positive integer", "error")
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
            flash("Item name must be unique per supplier", "error")
            return redirect(url_for("item_new", supplier_id=supplier.id))

        flash("Item added", "ok")
        return redirect(url_for("supplier_items", supplier_id=supplier.id))

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
            dq = int(default_qty_raw)
            if dq <= 0:
                raise ValueError
        except ValueError:
            flash("Default qty must be a positive integer", "error")
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

    # ---- Ordering (Step 3) ----
    @app.get("/suppliers/<int:supplier_id>/order")
    def order_form(supplier_id):
        supplier = Supplier.query.get_or_404(supplier_id)
        items = (
            Item.query.filter_by(supplier_id=supplier.id, active=True)
            .order_by(Item.name.asc())
            .all()
        )
        return render_template("order_form.html", supplier=supplier, items=items)

    @app.post("/suppliers/<int:supplier_id>/order/preview")
    def order_preview(supplier_id):
        supplier = Supplier.query.get_or_404(supplier_id)
        outlet_name = request.form.get("outlet_name", "Sari Rasa (East Village)").strip()
        notes = request.form.get("notes", "").strip()

        selected = []
        for key, val in request.form.items():
            # inputs are named qty_<item_id>
            m = re.match(r"qty_(\d+)$", key)
            if not m:
                continue
            try:
                qty = int(val)
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

        text = _build_whatsapp_text(outlet_name, selected, notes)
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
            notes=notes,
            items=selected,
            wa_url=wa_url,
            text=text,
        )

    return app


app = create_app()
