# 🍴 Restaurant Restocking App

A **mobile-first checklist app** that simplifies restaurant restocking.  
Staff can tick items to order, and with one click, the app generates a pre-filled WhatsApp message to send directly to suppliers.

---

## 🚀 Motivation

As a chef-owner, I’ve always found stock ordering to be a major pain point.  
Restaurants deal with **hundreds of items** — from dry goods to fresh vegetables and frozen meats. Staff often forget items when placing orders, leading to **delays, missing ingredients, and stressful rush hours**.

This app turns restocking into a **guided checklist flow**:
- Staff select a supplier  
- Tick required items and quantities  
- One-tap generates a WhatsApp order message  
- Send directly to the supplier  

Result: **fast, consistent, and error-free ordering**.

---

## 🛠️ Features (Planned)

- [x] **Supplier Management**  
  Store supplier details (name, contact, category).  

- [x] **Customizable Stock Items**  
  Add/edit supplier-linked items with units (kg, carton, packet, etc.).  

- [x] **Order Checklist Flow**  
  - Choose supplier  
  - Adjust quantities via `+ / -` buttons  
  - Preview order  
  - Auto-generate WhatsApp message  

- [x] **Notes & Defaults**  
  Set outlet name, delivery notes, and par levels.  

- [x] **Live Deployment**  
  Configure PostgreSQL (NeonDB) & host on Render.  

- [ ] **User Authentication**  
  Add login/registration for secure access.  

- [ ] **CSV Import/Export**  
  - Add CSV Import for easy supplier and items database update.
  - Add CSV Export for future Order History export for audit. 

- [ ] **Order History** *(MVP+)*  
  Store and view past orders for auditing.  

- [ ] **Multi-Outlet Support**  
  Manage multiple outlets within one system.  

- [ ] **Invoice Scanning**  
  Capture invoice data via camera and auto-update stock and prices.  

- [ ] **Mobile App Integration/Rebuild**  
  Convert to native iOS/Android app or integrate as a PWA.  

---

## 📦 Setup Flow

**Supplier added → Stock items keyed in → Order placed**

### 1. Supplier Details
- Supplier name  
- Contact number (WhatsApp)  
- Category (Dry, Frozen, Vegetables, Packaging, etc.)  

### 2. Stock Item Details
- Item type (e.g., Dry goods, Frozen, Vegetables)  
- Item name (e.g., Salt, Frozen Chicken Thigh, Cabbage)  
- Item unit (e.g., kg, packet, carton, tin)  

### 3. Ordering Flow (Alpha)
- Open supplier page  
- Select stock items  
- Generate WhatsApp message  
- Tap send  

---

## 🖥️ Technical Plan

### Tech Stack
- **Backend:** Flask (Python) — routes, forms, WhatsApp link generation  
- **Database:** SQLAlchemy ORM + SQLite (dev) / PostgreSQL (production)  
- **Frontend:** Jinja2 templates + CSS + vanilla JS (interactive qty buttons, dynamic updates)  
- **Cross-Platform:** Mobile-first responsive design, installable as a PWA  
- **Integrations:** WhatsApp deep link (`https://wa.me/`) for one-tap ordering  

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
   - List suppliers with category filter  
   - "Add Supplier" button  

2. **Items Page (per Supplier)**  
   - List items (name, unit, default qty)  
   - Add/Edit item  
   - Start order  

3. **Order Checklist**  
   - Adjust quantities  
   - Preview selected items  
   - Add notes  

4. **Order Preview**  
   - WhatsApp message preview  
   - Tap “Send via WhatsApp”  

5. **Order History** *(optional MVP+)*  
   - View past orders with timestamps  

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
PO Ref: PO-2025-08-24-001
