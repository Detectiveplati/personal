# 🍴 Restaurant Restocking App

A mobile-first checklist app to simplify **restaurant restocking**.  
Staff can tick items to order, and with one click the app generates a pre-filled WhatsApp message to send directly to suppliers.  

---

## 🚀 Motivation

I started as a restaurant chef-owner, so ordering of stocks have always been a big pain point.
It means managing **hundreds of stock items** — from dry goods to fresh vegetables to frozen meats. Staff often forget certain items when placing orders, causing delays, missing ingredients, and operational stress and diner rush hour delays due to stocks not properly ordered.

This app reduces restocking into a **guided checklist flow**:
- Staff select a supplier
- Tick items and quantities they need
- One-tap generate a WhatsApp message to the specific supplier
- Send directly to supplier  

Result: **fast, consistent, mistake-free ordering**.

---

## 🛠️ Features (Planned)

- [x] **Supplier Management**  
  Record supplier details (name, contact, category).

- [x] **Customisable Stock Items**  
  Add/edit items linked to each supplier with units (kg, carton, packet, etc.).

- [x] **Order Checklist Flow**  
  - Choose supplier  
  - Adjust item quantities via `+ / -` buttons  
  - Preview order  
  - Auto-generate WhatsApp message with one click  

- [x] **Notes & Defaults**  
  Configure outlet name, default delivery notes, and par levels.

- [ ] **Order History** *(MVP+)*  
  Save past orders for reference and auditing.

- [ ] **Multiple Outlets**   
Include functionality for multiple outlets.

- [ ] **Camera scan invoice details capture**  
  Scan invoices via phone and auto capture quantity of items, and update stocks prices on the fly.

- [ ] **Integration/Rebuilding of web app as a mobile app**  
  Either rebuilding the app as an iOS & android app or integration.

---

## 📦 Setup Flow

**Supplier acquired → Supplier details keyed in → Supplier stock keyed in**

### 1. Supplier Details
- Supplier name  
- Contact number (WhatsApp)  
- Category (Dry, Frozen, Vegetables, Packaging, etc.)  

### 2. Stock Item Details
- Item type (e.g., Dry goods, Frozen, Vegetables)  
- Item name (e.g., Salt, Frozen Chicken Thigh, Cabbage)  
- Item unit (e.g., kg, packet, carton, tin)  

### 3. Ordering Flow (Alpha)
- Go to supplier page  
- Choose stock items  
- Forward to WhatsApp  
- WhatsApp message auto-configured → tap send  

---

## 🖥️ Technical Plan

### Tech Stack
- **Backend:** Flask (Python) — handles routes, form submissions, WhatsApp link generation  
- **Database:** SQLAlchemy ORM + SQLite (dev) / Postgres (production-ready)  
- **Frontend:** Server-rendered HTML templates (Jinja2) with CSS + vanilla JS for interactivity (`+ / -` qty buttons, dynamic updates)  
- **Cross-Platform:** Mobile-friendly responsive design, accessible via browser (installable as a web app via “Add to Home Screen”)  
- **Integrations:** WhatsApp deep link (`https://wa.me/`) for one-click sending of orders

---

### Data Model
- **Suppliers**  
  - `id`, `name`, `phone`, `category`, `notes`  
- **Items**  
  - `id`, `supplier_id` (FK), `name`, `unit`, `default_qty`, `type`, `active`  
- **Orders** *(MVP+)*  
  - `id`, `supplier_id` (FK), `outlet_name`, `notes`, `timestamp`  
- **Order Lines** *(MVP+)*  
  - `id`, `order_id` (FK), `item_name_snapshot`, `qty`, `unit`  

---

## 📲 User Flow (Screens)

1. **Suppliers Page**
   - List of suppliers with category filter  
   - "Add Supplier" button  

2. **Items Page (per Supplier)**
   - List of items (name, unit, default qty)  
   - Add/Edit item  
   - Start order  

3. **Order Checklist**
   - Increment/decrement quantities  
   - Preview selected items  
   - Notes field  

4. **Order Preview**
   - Render WhatsApp message  
   - Tap "Send via WhatsApp" → opens app with message pre-filled  

5. **Order History** *(optional MVP+)*  
   - View past orders with timestamp  

---

## 📄 WhatsApp Message Format

```text
*Order from: Your Outlet*
Date: 2025-08-24

Items:
- Frozen Chicken Thigh: 3 carton
- Cabbage: 10 kg
- Salt: 2 pkt

Notes: Please deliver before 10am tomorrow.
PO Ref: SR-2025-08-24-001
