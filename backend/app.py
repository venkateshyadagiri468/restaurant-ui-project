import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure the SQLite database, relative to the app instance folder
basedir = os.path.abspath(os.path.dirname(__name__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'restaurant.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Models ---
class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250))
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(300))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(50), default="Pending") # Pending, Preparing, Ready, Served
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'table_number': self.table_number,
            'total_amount': self.total_amount,
            'status': self.status,
            'items': [item.to_dict() for item in self.items]
        }

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    menu_item = db.relationship('MenuItem')

    def to_dict(self):
        return {
            'id': self.id,
            'menu_item': self.menu_item.to_dict(),
            'quantity': self.quantity
        }

# --- Initialization & Seed ---
with app.app_context():
    db.create_all()
    # Seed data if empty
    if not MenuItem.query.first():
        sample_items = [
            MenuItem(name="Margherita Pizza", description="Classic cheese and tomato pizza.", price=12.99, category="Main", image_url="https://images.unsplash.com/photo-1574071318508-1cdbab80d002?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8N3x8bWFyZ2hlcml0YSUyMHBpenphfGVufDB8fDB8fHww"),
            MenuItem(name="Caesar Salad", description="Crisp romaine lettuce, croutons, and parmesan.", price=8.50, category="Starter", image_url="https://images.unsplash.com/photo-1550304943-4f24f54ddde9?fm=jpg&w=3000&auto=format&fit=crop&q=60"),
            MenuItem(name="Tiramisu", description="Coffee-flavored Italian dessert.", price=6.99, category="Dessert", image_url="https://images.unsplash.com/photo-1571115177098-24dec2fa231e?fm=jpg&w=3000&auto=format&fit=crop&q=60"),
            MenuItem(name="Spaghetti Carbonara", description="Pasta with creamy egg sauce and pancetta.", price=14.99, category="Main", image_url="https://images.unsplash.com/photo-1612874742237-65261d76326e?fm=jpg&w=3000&auto=format&fit=crop&q=60"),
            MenuItem(name="Garlic Bread", description="Toasted bread with garlic and herbs.", price=4.99, category="Starter", image_url="https://images.unsplash.com/photo-1573140247632-18daf1648bc8?fm=jpg&w=3000&auto=format&fit=crop&q=60")
        ]
        db.session.add_all(sample_items)
        db.session.commit()

# --- Routes ---

@app.route('/api/menu', methods=['GET'])
def get_menu():
    items = MenuItem.query.all()
    return jsonify([item.to_dict() for item in items])

@app.route('/api/menu', methods=['POST'])
def add_menu_item():
    data = request.json
    try:
        new_item = MenuItem(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            category=data.get('category', 'Uncategorized'),
            image_url=data.get('image_url', '')
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify(new_item.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders = Order.query.order_by(Order.id.desc()).all()
    return jsonify([order.to_dict() for order in orders])

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    try:
        table_number = int(data.get('table_number', 1))
        items_data = data.get('items', [])
        
        if not items_data:
            return jsonify({"error": "Order must contain items"}), 400

        new_order = Order(table_number=table_number, status="Pending")
        db.session.add(new_order)
        db.session.flush() # Get order ID before committing
        
        total_amount = 0
        for item in items_data:
            menu_item_id = item['menu_item_id']
            quantity = item.get('quantity', 1)
            
            menu_item = MenuItem.query.get(menu_item_id)
            if not menu_item:
                return jsonify({"error": f"Menu item {menu_item_id} not found"}), 400
                
            total_amount += menu_item.price * quantity
            order_item = OrderItem(order_id=new_order.id, menu_item_id=menu_item_id, quantity=quantity)
            db.session.add(order_item)
            
        new_order.total_amount = total_amount
        db.session.commit()
        return jsonify(new_order.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    data = request.json
    new_status = data.get('status')
    if not new_status:
         return jsonify({"error": "Status is required"}), 400
         
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
        
    order.status = new_status
    db.session.commit()
    return jsonify(order.to_dict())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
