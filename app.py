from flask import Flask, request, jsonify, render_template, make_response
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
def initialize_sample_data():
    # Check if we already have data
    if Customer.query.count() > 0:
        return
        
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
    return """
    <html>
        <head>
            <title>Onix CRM</title>
            <style>
                /* ServiceNow-inspired styles */
                :root {
                    --servicenow-blue: #2e51bb;
                    --servicenow-light-blue: #3a7cda;
                    --servicenow-dark-blue: #1e3c8c;
                    --servicenow-green: #6eb056;
                    --servicenow-yellow: #f2af43;
                    --servicenow-red: #e74c3c;
                    --servicenow-gray: #e8e8e8;
                    --servicenow-dark-gray: #4a4a4a;
                    --servicenow-border: #d9d9d9;
                }
                body { 
                    font-family: 'Source Sans Pro', 'Helvetica Neue', Arial, sans-serif; 
                    margin: 0; 
                    padding: 0; 
                    background-color: #f6f7f9; 
                    color: #2e2e2e;
                }
                .main-container {
                    max-width: 1400px;
                    margin: 0 auto;
                    padding: 0 20px;
                }
                .global-header {
                    background-color: var(--servicenow-blue);
                    color: white;
                    padding: 0 20px;
                    height: 50px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    position: sticky;
                    top: 0;
                    z-index: 1000;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                h1 { 
                    color: var(--servicenow-dark-blue); 
                    margin: 20px 0; 
                    font-weight: 400;
                    font-size: 24px;
                }
                .header { 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center; 
                    margin-bottom: 20px; 
                    padding: 15px 0;
                    border-bottom: 1px solid var(--servicenow-border);
                }
                .card { 
                    background-color: white; 
                    border-radius: 4px; 
                    box-shadow: 0 1px 3px rgba(0,0,0,0.08); 
                    padding: 16px; 
                    margin-bottom: 16px; 
                    border: 1px solid var(--servicenow-border);
                }
                .customer-list { 
                    display: grid; 
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
                    gap: 16px;
                }
                .customer-card { 
                    cursor: pointer; 
                    transition: all 0.2s; 
                    border-left: 4px solid transparent;
                }
                .customer-card:hover { 
                    border-left: 4px solid var(--servicenow-light-blue); 
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1); 
                }
                .customer-name { 
                    font-size: 16px; 
                    font-weight: 600; 
                    color: var(--servicenow-blue); 
                }
                .customer-email { 
                    color: var(--servicenow-dark-gray); 
                    margin-bottom: 8px; 
                    font-size: 14px;
                }
                .customer-company { 
                    font-weight: 500; 
                    font-size: 14px;
                }
                .status { 
                    display: inline-block; 
                    padding: 3px 8px; 
                    border-radius: 12px; 
                    font-size: 12px; 
                    font-weight: 600; 
                    text-transform: uppercase; 
                }
                .status-customer { 
                    background-color: var(--servicenow-green); 
                    color: white; 
                }
                .status-prospect { 
                    background-color: var(--servicenow-yellow); 
                    color: white; 
                }
                .status-lead { 
                    background-color: var(--servicenow-light-blue); 
                    color: white; 
                }
                .modal { 
                    display: none; 
                    position: fixed; 
                    top: 0; 
                    left: 0; 
                    width: 100%; 
                    height: 100%; 
                    background-color: rgba(0,0,0,0.4); 
                    z-index: 1001; 
                }
                .modal-content { 
                    background-color: #fff; 
                    margin: 10% auto; 
                    padding: 20px; 
                    border-radius: 4px; 
                    width: 70%; 
                    max-width: 700px; 
                    position: relative; 
                    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                }
                .modal-header {
                    border-bottom: 1px solid var(--servicenow-border);
                    padding-bottom: 10px;
                    margin-bottom: 15px;
                }
                .close { 
                    position: absolute; 
                    right: 15px; 
                    top: 10px; 
                    font-size: 24px; 
                    font-weight: normal; 
                    cursor: pointer; 
                    color: #888;
                }
                .action-buttons { 
                    margin: 15px 0; 
                    display: flex;
                    gap: 10px;
                }
                .delete-btn { 
                    background-color: var(--servicenow-red); 
                    color: white; 
                    border: none; 
                    padding: 8px 12px; 
                    border-radius: 4px; 
                    cursor: pointer; 
                }
                .delete-btn:hover { 
                    background-color: #c82333; 
                }
                .close:hover { 
                    color: #444; 
                }
                .form-group { 
                    margin-bottom: 15px; 
                }
                label { 
                    display: block; 
                    margin-bottom: 5px; 
                    font-weight: 500; 
                    font-size: 14px;
                    color: var(--servicenow-dark-gray);
                }
                input, select, textarea { 
                    width: 100%; 
                    padding: 8px 10px; 
                    border: 1px solid var(--servicenow-border); 
                    border-radius: 4px; 
                    font-family: inherit; 
                    font-size: 14px;
                }
                input:focus, select:focus, textarea:focus {
                    outline: none;
                    border-color: var(--servicenow-light-blue);
                    box-shadow: 0 0 0 2px rgba(58, 124, 218, 0.2);
                }
                button { 
                    background-color: var(--servicenow-blue); 
                    color: white; 
                    border: none; 
                    padding: 8px 16px; 
                    border-radius: 4px; 
                    cursor: pointer; 
                    font-weight: 600; 
                    font-size: 14px;
                }
                button:hover { 
                    background-color: var(--servicenow-dark-blue); 
                }
                .error { 
                    color: var(--servicenow-red); 
                    margin-top: 5px; 
                    font-size: 13px;
                }
                .interactions { 
                    margin-top: 20px; 
                }
                .interaction-item { 
                    padding: 10px; 
                    border-left: 3px solid var(--servicenow-light-blue); 
document.getElementById('newCustomerModal').style.display = 'block';
                   ...