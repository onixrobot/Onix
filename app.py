from flask import Flask, request, jsonify, render_template, make_response, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from datetime import datetime
import os
import uuid
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'enterprise-demo-secret-key'
app.config['ITEMS_PER_PAGE'] = 10  # New configuration for pagination

# Ensure indexes are created for efficient querying
with app.app_context():
    db.session.execute('CREATE INDEX IF NOT EXISTS ix_customer_email ON Customer (email)')
    db.session.execute('CREATE INDEX IF NOT EXISTS ix_interaction_customer_id ON Interaction (customer_id)')
    db.session.commit()

db = SQLAlchemy(app)
api = Api(app)

# Database Models
class Customer(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    company = db.Column(db.String(100))
    status = db.Column(db.String(20), default='prospect')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'company': self.company,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Interaction(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('customer.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'type': self.type,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

# Create database tables
with app.app_context():
    db.create_all()

# Sample data initialization
# Prevent initializing sample data in production
def initialize_sample_data():
    if current_app.config['ENV'] != 'production':
        # Check if we already have data
        if Customer.query.count() == 0:
            
            # Add sample customers
            customers = [
                Customer(
                    id=str(uuid.uuid4()),
                    first_name='John',
                    last_name='Smith',
                    email='john.smith@acme.com',
                    company='ACME Inc.',
                    status='customer'
                ),
                Customer(
                    id=str(uuid.uuid4()),
                    first_name='Sarah',
                    last_name='Johnson',
                    email='sarah.j@techinnovate.com',
                    company='Tech Innovate',
                    status='prospect'
                ),
                Customer(
                    id=str(uuid.uuid4()),
                    first_name='Michael',
                    last_name='Brown',
                    email='mbrown@globalcorp.com',
                    company='Global Corp',
                    status='lead'
                )
            ]
            
            for customer in customers:
                db.session.add(customer)
            db.session.commit()
            
            # Add sample interactions for the first customer
            if customers:
                interaction = Interaction(
                    id=str(uuid.uuid4()),
                    customer_id=customers[0].id,
                    type='meeting',
                    notes='Discussed new product features'
                )
                db.session.add(interaction)
                db.session.commit()

# Initialize sample data
with app.app_context():
    initialize_sample_data()

@app.route('/')
def home():
    return render_template('index.html')

# API Endpoints

# Customer endpoints
@app.route('/api/customers', methods=['GET'])
def get_customers():
    try:
        page = request.args.get('page', 1, type=int)
        query = Customer.query.paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
        customers = query.items
        return jsonify([customer.to_dict() for customer in customers])
    except Exception as e:
        current_app.logger.error(f"Error fetching customers: {e}")
        return jsonify({"error": "An error occurred while fetching customers."}), 500

@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify(customer.to_dict())
    except Exception as e:
        current_app.logger.error(f"Error fetching customer {customer_id}: {e}")
        return jsonify({"error": "An error occurred while fetching the customer."}), 500

@app.route('/api/customers', methods=['POST'])
def create_customer():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"{field} is required"}), 400
        
        # Check if email already exists
        existing_customer = Customer.query.filter_by(email=data['email']).first()
        if existing_customer:
            return jsonify({"error": "A customer with this email already exists"}), 400
        
        # Create new customer
        new_customer = Customer(
            id=str(uuid.uuid4()),
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            company=data.get('company', ''),
            status=data.get('status', 'lead')
        )
        
        db.session.add(new_customer)
        db.session.commit()
        
        return jsonify(new_customer.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating customer: {e}")
        return jsonify({"error": "An error occurred while creating a new customer."}), 500

@app.route('/api/customers/<customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'first_name' in data:
            customer.first_name = data['first_name']
        if 'last_name' in data:
            customer.last_name = data['last_name']
        if 'email' in data:
            # Check if email already exists for another customer
            existing_customer = Customer.query.filter_by(email=data['email']).first()
            if existing_customer and existing_customer.id != customer_id:
                return jsonify({"error": "A customer with this email already exists"}), 400
            customer.email = data['email']
        if 'company' in data:
            customer.company = data['company']
        if 'status' in data:
            customer.status = data['status']
        
        customer.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(customer.to_dict())
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating customer {customer_id}: {e}")
        return jsonify({"error": "An error occurred while updating the customer."}), 500

@app.route('/api/customers/<customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        # Delete associated interactions first
        Interaction.query.filter_by(customer_id=customer_id).delete()
        
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({"message": "Customer deleted successfully"})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting customer {customer_id}: {e}")
        return jsonify({"error": "An error occurred while deleting the customer."}), 500

# Interaction endpoints
@app.route('/api/customers/<customer_id>/interactions', methods=['GET'])
def get_customer_interactions(customer_id):
    try:
        # Check if customer exists
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        interactions = Interaction.query.filter_by(customer_id=customer_id).order_by(Interaction.created_at.desc()).all()
        return jsonify([interaction.to_dict() for interaction in interactions])
    except Exception as e:
        current_app.logger.error(f"Error fetching interactions for customer {customer_id}: {e}")
        return jsonify({"error": "An error occurred while fetching interactions."}), 500

@app.route('/api/interactions', methods=['POST'])
def create_interaction():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['customer_id', 'type', 'notes']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"{field} is required"}), 400
        
        # Check if customer exists
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        # Create new interaction
        new_interaction = Interaction(
            id=str(uuid.uuid4()),
            customer_id=data['customer_id'],
            type=data['type'],
            notes=data['notes']
        )
        
        db.session.add(new_interaction)
        db.session.commit()
        
        return jsonify(new_interaction.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating interaction: {e}")
        return jsonify({"error": "An error occurred while creating a new interaction."}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
