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
                    margin-bottom: 10px; 
                    background-color: #f9f9f9; 
                }
                .interaction-type { 
                    font-weight: 600; 
                    color: var(--servicenow-dark-blue);
                }
                .interaction-date { 
                    color: var(--servicenow-dark-gray); 
                    font-size: 12px; 
                }
                .api-section { 
                    margin-top: 30px; 
                }
                .endpoint { 
                    background-color: #f6f7f9; 
                    padding: 10px; 
                    border-radius: 4px; 
                    font-family: monospace; 
                    margin-bottom: 10px; 
                    border: 1px solid var(--servicenow-border);
                }
                pre { 
                    background-color: #f5f5f5; 
                    padding: 10px; 
                    border-radius: 4px; 
                    overflow-x: auto; 
                    border: 1px solid var(--servicenow-border);
                    font-size: 13px;
                }
                .tabs { 
                    display: flex; 
                    margin-bottom: 20px; 
                    border-bottom: 1px solid var(--servicenow-border);
                }
                .tab { 
                    padding: 10px 20px; 
                    cursor: pointer; 
                    border-bottom: 2px solid transparent; 
                    color: var(--servicenow-dark-gray);
                }
                .tab.active { 
                    border-bottom: 2px solid var(--servicenow-blue); 
                    font-weight: 600; 
                    color: var(--servicenow-blue);
                }
                .tab-content { 
                    display: none; 
                }
                .tab-content.active { 
                    display: block; 
                }
                
                /* Main view styles */
                .main-view {
                    display: none;
                }
                
                .main-view.active {
                    display: block;
                }
            </style>
        </head>
        <body>
            <div class="global-header">
                <div style="display: flex; align-items: center;">
                    <span style="font-size: 18px; font-weight: 600; margin-right: 30px;">Onix CRM</span>
                    <nav style="display: flex;">
                        <a href="#" id="nav-dashboard" onclick="switchMainView('dashboard')" style="color: white; text-decoration: none; padding: 0 15px; height: 50px; display: flex; align-items: center; border-bottom: 3px solid white;">Dashboard</a>
                        <a href="#" id="nav-customers" onclick="switchMainView('customers')" style="color: white; text-decoration: none; padding: 0 15px; height: 50px; display: flex; align-items: center;">Customers</a>
                        <a href="#" id="nav-reports" onclick="switchMainView('reports')" style="color: white; text-decoration: none; padding: 0 15px; height: 50px; display: flex; align-items: center;">Reports</a>
                    </nav>
                </div>
                <div>
                    <span style="font-size: 14px;">Admin</span>
                </div>
            </div>
            
            <div class="main-container" id="main-view-container">
                <!-- DASHBOARD VIEW -->
                <div id="main-dashboard" class="main-view active">
                    <div class="header">
                        <h1>Dashboard</h1>
                        <button onclick="openNewCustomerModal()">Add New Customer</button>
                    </div>
                    
                    <div class="tabs">
                        <div class="tab active" onclick="switchTab('dashboard')">Dashboard</div>
                        <div class="tab" onclick="switchTab('api')">API Documentation</div>
                    </div>
                
                    <div id="dashboard" class="tab-content active">
                        <div class="card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <h2 style="margin: 0; font-weight: 400; color: var(--servicenow-dark-blue);">Recent Customers</h2>
                                <div style="display: flex; gap: 10px; align-items: center;">
                                    <input type="text" placeholder="Search customers..." style="width: 250px; padding: 6px 10px; margin-right: 10px;">
                                    <select style="width: auto; padding: 6px 10px;">
                                        <option>All Statuses</option>
                                        <option>Customer</option>
                                        <option>Prospect</option>
                                        <option>Lead</option>
                                    </select>
                                </div>
                            </div>
                            <div class="customer-list" id="customerList">
                                <!-- Customer cards will be populated here -->
                                <div class="card customer-card">
                                    <p class="customer-name">Loading customers...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- CUSTOMERS VIEW -->
                <div id="main-customers" class="main-view">
                    <div class="header">
                        <h1>Customer Management</h1>
                        <button onclick="openNewCustomerModal()">Add New Customer</button>
                    </div>
                    
                    <div class="card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <h2 style="margin: 0; font-weight: 400; color: var(--servicenow-dark-blue);">All Customers</h2>
                            <div style="display: flex; gap: 10px; align-items: center;">
                                <input type="text" id="customer-search" placeholder="Search customers..." style="width: 250px; padding: 6px 10px; margin-right: 10px;">
                                <select id="status-filter" style="width: auto; padding: 6px 10px;">
                                    <option value="all">All Statuses</option>
                                    <option value="customer">Customer</option>
                                    <option value="prospect">Prospect</option>
                                    <option value="lead">Lead</option>
                                </select>
                            </div>
                        </div>
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="background-color: #f6f7f9; border-bottom: 1px solid var(--servicenow-border);">
                                    <th style="text-align: left; padding: 10px; font-weight: 500;">Name</th>
                                    <th style="text-align: left; padding: 10px; font-weight: 500;">Email</th>
                                    <th style="text-align: left; padding: 10px; font-weight: 500;">Company</th>
                                    <th style="text-align: left; padding: 10px; font-weight: 500;">Status</th>
                                    <th style="text-align: left; padding: 10px; font-weight: 500;">Created</th>
                                    <th style="text-align: center; padding: 10px; font-weight: 500;">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="customers-table-body">
                                <tr>
                                    <td colspan="6" style="text-align: center; padding: 20px;">Loading customers...</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- REPORTS VIEW -->
                <div id="main-reports" class="main-view">
                    <div class="header">
                        <h1>Reports & Analytics</h1>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                        <div class="card">
                            <h2 style="margin-top: 0; font-weight: 400; color: var(--servicenow-dark-blue);">Customer Status Distribution</h2>
                            <div style="height: 200px; display: flex; align-items: flex-end; gap: 20px; padding: 20px 0;">
                                <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
                                    <div style="background-color: var(--servicenow-yellow); width: 100%; height: 120px;"></div>
                                    <p style="margin-top: 10px; font-weight: 500;">Prospects</p>
                                    <p id="prospect-count" style="margin: 0;">0</p>
                                </div>
                                <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
                                    <div style="background-color: var(--servicenow-light-blue); width: 100%; height: 80px;"></div>
                                    <p style="margin-top: 10px; font-weight: 500;">Leads</p>
                                    <p id="lead-count" style="margin: 0;">0</p>
                                </div>
                                <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
                                    <div style="background-color: var(--servicenow-green); width: 100%; height: 150px;"></div>
                                    <p style="margin-top: 10px; font-weight: 500;">Customers</p>
                                    <p id="customer-count" style="margin: 0;">0</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h2 style="margin-top: 0; font-weight: 400; color: var(--servicenow-dark-blue);">Interaction Types</h2>
                            <div style="height: 200px; display: flex; align-items: flex-end; gap: 20px; padding: 20px 0;">
                                <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
                                    <div style="background-color: #6eb0d4; width: 100%; height: 100px;"></div>
                                    <p style="margin-top: 10px; font-weight: 500;">Calls</p>
                                    <p id="call-count" style="margin: 0;">0</p>
                                </div>
                                <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
                                    <div style="background-color: #d49a6e; width: 100%; height: 130px;"></div>
                                    <p style="margin-top: 10px; font-weight: 500;">Emails</p>
                                    <p id="email-count" style="margin: 0;">0</p>
                                </div>
                                <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
                                    <div style="background-color: #a16ed4; width: 100%; height: 70px;"></div>
                                    <p style="margin-top: 10px; font-weight: 500;">Meetings</p>
                                    <p id="meeting-count" style="margin: 0;">0</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h2 style="margin-top: 0; font-weight: 400; color: var(--servicenow-dark-blue);">Recent Activity</h2>
                            <div id="recent-activity" style="max-height: 250px; overflow-y: auto;">
                                <p style="text-align: center; color: var(--servicenow-dark-gray);">Loading recent activity...</p>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h2 style="margin-top: 0; font-weight: 400; color: var(--servicenow-dark-blue);">Top Companies</h2>
                            <div id="top-companies" style="max-height: 250px; overflow-y: auto;">
                                <p style="text-align: center; color: var(--servicenow-dark-gray);">Loading company data...</p>
                            </div>
                        </div>
                    </div>
                </div>
            
            <div id="api" class="tab-content">
                <div class="card api-section">
                    <h2>API Documentation</h2>
                    <p>This CRM system provides a RESTful API for managing customers and interactions.</p>
                    
                    <h3>Customer Endpoints</h3>
                    <div class="endpoint">
                        <strong>GET /api/customers</strong> - List all customers
                    </div>
                    <div class="endpoint">
                        <strong>GET /api/customers/:id</strong> - Get customer details
                    </div>
                    <div class="endpoint">
                        <strong>POST /api/customers</strong> - Create a new customer
                    </div>
                    <div class="endpoint">
                        <strong>PUT /api/customers/:id</strong> - Update a customer
                    </div>
                    <div class="endpoint">
                        <strong>DELETE /api/customers/:id</strong> - Delete a customer
                    </div>
                    
                    <h3>Interaction Endpoints</h3>
                    <div class="endpoint">
                        <strong>GET /api/customers/:id/interactions</strong> - List customer interactions
                    </div>
                    <div class="endpoint">
                        <strong>POST /api/interactions</strong> - Create a new interaction
                    </div>
                </div>
            </div>
            
            <!-- Customer Modal -->
            <div id="customerModal" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2 style="margin: 0; font-weight: 400; color: var(--servicenow-dark-blue);">Customer Details</h2>
                        <span class="close" onclick="closeCustomerModal()">&times;</span>
                    </div>
                    <div id="customerDetails" style="margin-bottom: 20px;">
                        <!-- Customer details will be populated here -->
                    </div>
                    <div class="action-buttons">
                        <button onclick="editCustomer()">Edit</button>
                        <button class="delete-btn" onclick="deleteCustomer()">Delete Customer</button>
                    </div>
                    
                    <div style="margin-top: 30px; border-top: 1px solid var(--servicenow-border); padding-top: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <h3 style="margin: 0; font-weight: 400; color: var(--servicenow-dark-blue);">Interactions</h3>
                            <button onclick="toggleAddInteraction()" style="background-color: transparent; color: var(--servicenow-blue); border: 1px solid var(--servicenow-blue); padding: 6px 12px;">New Interaction</button>
                        </div>
                        <div id="customerInteractions"></div>
                        
                        <div class="add-interaction" id="addInteractionForm" style="display: none; background-color: #f9f9f9; padding: 15px; border-radius: 4px; margin-top: 15px; border: 1px solid var(--servicenow-border);">
                            <h3 style="margin-top: 0; font-weight: 400; color: var(--servicenow-dark-blue);">Add Interaction</h3>
                            <div class="form-group">
                                <label for="interactionType">Type</label>
                                <select id="interactionType">
                                    <option value="call">Call</option>
                                    <option value="email">Email</option>
                                    <option value="meeting">Meeting</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="interactionNotes">Notes</label>
                                <textarea id="interactionNotes" placeholder="Notes" rows="3"></textarea>
                            </div>
                            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                                <button onclick="cancelAddInteraction()" style="background-color: transparent; color: var(--servicenow-dark-gray); border: 1px solid var(--servicenow-border);">Cancel</button>
                                <button onclick="addInteraction()">Add Interaction</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- New Customer Modal -->
            <div id="newCustomerModal" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2 style="margin: 0; font-weight: 400; color: var(--servicenow-dark-blue);">Add New Customer</h2>
                        <span class="close" onclick="closeNewCustomerModal()">&times;</span>
                    </div>
                    
                    <div style="padding: 10px 0;">
                        <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                            <div class="form-group" style="flex: 1;">
                                <label for="firstName">First Name</label>
                                <input type="text" id="firstName" required>
                            </div>
                            <div class="form-group" style="flex: 1;">
                                <label for="lastName">Last Name</label>
                                <input type="text" id="lastName" required>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" id="email" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="company">Company</label>
                            <input type="text" id="company">
                        </div>
                        
                        <div class="form-group">
                            <label for="status">Status</label>
                            <select id="status">
                                <option value="prospect">Prospect</option>
                                <option value="lead">Lead</option>
                                <option value="customer">Customer</option>
                            </select>
                        </div>
                    </div>
                    
                    <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; padding-top: 15px; border-top: 1px solid var(--servicenow-border);">
                        <button onclick="closeNewCustomerModal()" style="background-color: transparent; color: var(--servicenow-dark-gray); border: 1px solid var(--servicenow-border);">Cancel</button>
                        <button onclick="createCustomer()">Create Customer</button>
                    </div>
                </div>
            </div>
            
            <script>
                let currentCustomerId = null;
                
                // Load all data when the page loads
                window.onload = function() {
                    loadCustomers();
                    loadCustomersTable();
                    loadReportsData();
                };
                
                function switchMainView(viewId) {
                    // Hide all main views
                    document.querySelectorAll('.main-view').forEach(view => {
                        view.classList.remove('active');
                    });
                    
                    // Deactivate all navigation links
                    document.querySelectorAll('#nav-dashboard, #nav-customers, #nav-reports').forEach(nav => {
                        nav.style.borderBottom = 'none';
                    });
                    
                    // Activate the selected view and navigation link
                    document.getElementById(`main-${viewId}`).classList.add('active');
                    document.getElementById(`nav-${viewId}`).style.borderBottom = '3px solid white';
                    
                    // Refresh data for the selected view
                    if (viewId === 'customers') {
                        loadCustomersTable();
                    } else if (viewId === 'reports') {
                        loadReportsData();
                    } else if (viewId === 'dashboard') {
                        loadCustomers();
                    }
                }
                
                function switchTab(tabId) {
                    // Hide all tab contents
                    document.querySelectorAll('.tab-content').forEach(content => {
                        content.classList.remove('active');
                    });
                    
                    // Deactivate all tabs
                    document.querySelectorAll('.tab').forEach(tab => {
                        tab.classList.remove('active');
                    });
                    
                    // Activate the selected tab and content
                    document.getElementById(tabId).classList.add('active');
                    document.querySelector(`.tab[onclick="switchTab('${tabId}')"]`).classList.add('active');
                }
                
                function loadCustomers() {
                    fetch('/api/customers')
                        .then(response => response.json())
                        .then(data => {
                            const customerList = document.getElementById('customerList');
                            customerList.innerHTML = '';
                            
                            if (data.error) {
                                customerList.innerHTML = `<p class="error">${data.error}</p>`;
                                return;
                            }
                            
                            data.forEach(customer => {
                                const card = document.createElement('div');
                                card.className = 'card customer-card';
                                card.onclick = () => openCustomerModal(customer.id);
                                
                                const statusClass = `status-${customer.status}`;
                                
                                card.innerHTML = `
                                    <p class="customer-name">${customer.first_name} ${customer.last_name}</p>
                                    <p class="customer-email">${customer.email}</p>
                                    <p class="customer-company">${customer.company}</p>
                                    <span class="status ${statusClass}">${customer.status}</span>
                                `;
                                
                                customerList.appendChild(card);
                            });
                        })
                        .catch(error => {
                            document.getElementById('customerList').innerHTML = 
                                `<p class="error">Error loading customers: ${error.message}</p>`;
                        });
                }
                
                function openCustomerModal(customerId) {
                    currentCustomerId = customerId;
                    document.getElementById('customerModal').style.display = 'block';
                    
                    // Fetch customer details
                    fetch(`/api/customers/${customerId}`)
                        .then(response => response.json())
                        .then(customer => {
                            document.getElementById('customerDetails').innerHTML = `
                                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                                    <div style="width: 40px; height: 40px; border-radius: 50%; background-color: var(--servicenow-light-blue); color: white; display: flex; align-items: center; justify-content: center; margin-right: 15px; font-size: 18px;">
                                        ${customer.first_name.charAt(0)}${customer.last_name.charAt(0)}
                                    </div>
                                    <div>
                                        <h3 style="margin: 0; font-weight: 500; color: var(--servicenow-dark-blue);">${customer.first_name} ${customer.last_name}</h3>
                                        <p style="margin: 3px 0 0 0; color: var(--servicenow-dark-gray);">${customer.company}</p>
                                    </div>
                                </div>
                                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 20px;">
                                    <div class="card" style="margin-bottom: 0;">
                                        <p style="margin: 0 0 5px 0; color: var(--servicenow-dark-gray); font-size: 12px;">Email</p>
                                        <p style="margin: 0; font-weight: 500;">${customer.email}</p>
                                    </div>
                                    <div class="card" style="margin-bottom: 0;">
                                        <p style="margin: 0 0 5px 0; color: var(--servicenow-dark-gray); font-size: 12px;">Status</p>
                                        <p style="margin: 0;"><span class="status status-${customer.status}">${customer.status}</span></p>
                                    </div>
                                    <div class="card" style="margin-bottom: 0;">
                                        <p style="margin: 0 0 5px 0; color: var(--servicenow-dark-gray); font-size: 12px;">Created</p>
                                        <p style="margin: 0; font-weight: 500;">${new Date(customer.created_at).toLocaleDateString()}</p>
                                    </div>
                                    <div class="card" style="margin-bottom: 0;">
                                        <p style="margin: 0 0 5px 0; color: var(--servicenow-dark-gray); font-size: 12px;">Last Updated</p>
                                        <p style="margin: 0; font-weight: 500;">${new Date(customer.updated_at).toLocaleDateString()}</p>
                                    </div>
                                </div>
                            `;
                            
                            loadInteractions(customerId);
                        });
                    
                    // Hide the interaction form by default
                    document.getElementById('addInteractionForm').style.display = 'none';
                    document.getElementById('customerModal').style.display = 'block';
                }
                
                function loadInteractions(customerId) {
                    fetch(`/api/customers/${customerId}/interactions`)
                        .then(response => response.json())
                        .then(interactions => {
                            const interactionsList = document.getElementById('customerInteractions');
                            
                            if (interactions.error) {
                                interactionsList.innerHTML = `<p class="error">${interactions.error}</p>`;
                                return;
                            }
                            
                            if (interactions.length === 0) {
                                interactionsList.innerHTML = '<div style="padding: 15px; text-align: center; color: var(--servicenow-dark-gray);">No interactions recorded yet.</div>';
                                return;
                            }
                            
                            interactionsList.innerHTML = '';
                            
                            interactions.forEach(interaction => {
                                const item = document.createElement('div');
                                item.className = 'interaction-item';
                                
                                // Get icon based on interaction type
                                let icon = '📞'; // default phone icon
                                if (interaction.type === 'email') icon = '✉️';
                                if (interaction.type === 'meeting') icon = '👥';
                                
                                item.innerHTML = `
                                    <div style="display: flex; align-items: flex-start;">
                                        <div style="font-size: 18px; margin-right: 10px;">${icon}</div>
                                        <div style="flex: 1;">
                                            <p class="interaction-type">${interaction.type}</p>
                                            <p style="margin: 5px 0;">${interaction.notes}</p>
                                            <p class="interaction-date">${new Date(interaction.created_at).toLocaleString()}</p>
                                        </div>
                                    </div>
                                `;
                                interactionsList.appendChild(item);
                            });
                        })
                        .catch(error => {
                            document.getElementById('customerInteractions').innerHTML = 
                                `<p class="error">Error loading interactions: ${error.message}</p>`;
                        });
                }
                
                function toggleAddInteraction() {
                    const form = document.getElementById('addInteractionForm');
                    form.style.display = form.style.display === 'none' ? 'block' : 'none';
                }
                
                function cancelAddInteraction() {
                    document.getElementById('addInteractionForm').style.display = 'none';
                    document.getElementById('interactionNotes').value = '';
                    document.getElementById('interactionType').selectedIndex = 0;
                }
                
                function editCustomer() {
                    // This would be implemented in a real application
                    alert('Edit customer functionality would be implemented here');
                }
                
                function closeCustomerModal() {
                    document.getElementById('customerModal').style.display = 'none';
                    currentCustomerId = null;
                }
                
                function deleteCustomer() {
                    if (!currentCustomerId) return;
                    
                    if (confirm('Are you sure you want to delete this customer? This action cannot be undone.')) {
                        fetch(`/api/customers/${currentCustomerId}`, {
                            method: 'DELETE'
                        })
                        .then(response => {
                            if (response.ok) {
                                alert('Customer deleted successfully');
                                closeCustomerModal();
                                loadCustomers(); // Refresh the customer list
                            } else {
                                return response.json().then(data => {
                                    throw new Error(data.error || 'Failed to delete customer');
                                });
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('Error: ' + error.message);
                        });
                    }
                }
                
                function addInteraction() {
                    const type = document.getElementById('interactionType').value;
                    const notes = document.getElementById('interactionNotes').value;
                    
                    if (!notes.trim()) {
                        alert('Please enter interaction notes');
                        return;
                    }
                    
                    fetch('/api/interactions', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            customer_id: currentCustomerId,
                            type: type,
                            notes: notes
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            alert(`Error: ${data.error}`);
                            return;
                        }
                        
                        // Clear the form
                        document.getElementById('interactionNotes').value = '';
                        
                        // Reload interactions
                        loadInteractions(currentCustomerId);
                    })
                    .catch(error => {
                        alert(`Error adding interaction: ${error.message}`);
                    });
                }
                
                function openNewCustomerModal() {
                    document.getElementById('newCustomerModal').style.display = 'block';
                    document.getElementById('newCustomerError').textContent = '';
                    
                    // Clear the form
                    document.getElementById('firstName').value = '';
                    document.getElementById('lastName').value = '';
                    document.getElementById('email').value = '';
                    document.getElementById('company').value = '';
                    document.getElementById('status').value = 'lead';
                }
                
                function closeNewCustomerModal() {
                    document.getElementById('newCustomerModal').style.display = 'none';
                }
                
                function createCustomer() {
                    const firstName = document.getElementById('firstName').value;
                    const lastName = document.getElementById('lastName').value;
                    const email = document.getElementById('email').value;
                    const company = document.getElementById('company').value;
                    const status = document.getElementById('status').value;
                    
                    // Simple validation
                    if (!firstName || !lastName || !email) {
                        document.getElementById('newCustomerError').textContent = 'Please fill in all required fields';
                        return;
                    }
                    
                    fetch('/api/customers', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            first_name: firstName,
                            last_name: lastName,
                            email: email,
                            company: company,
                            status: status
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            document.getElementById('newCustomerError').textContent = data.error;
                            return;
                        }
                        
                        // Close the modal and reload customers
                        closeNewCustomerModal();
                        loadCustomers();
                    })
                    .catch(error => {
                        document.getElementById('newCustomerError').textContent = `Error: ${error.message}`;
                    });
                }
                // Function to load customers table for the Customers view
                function loadCustomersTable() {
                    fetch('/api/customers')
                        .then(response => response.json())
                        .then(data => {
                            const tableBody = document.getElementById('customers-table-body');
                            tableBody.innerHTML = '';
                            
                            if (data.error) {
                                tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 20px;">${data.error}</td></tr>`;
                                return;
                            }
                            
                            if (data.length === 0) {
                                tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 20px;">No customers found</td></tr>`;
                                return;
                            }
                            
                            data.forEach(customer => {
                                const row = document.createElement('tr');
                                row.style.borderBottom = '1px solid var(--servicenow-border)';
                                
                                row.innerHTML = `
                                    <td style="padding: 10px;">${customer.first_name} ${customer.last_name}</td>
                                    <td style="padding: 10px;">${customer.email}</td>
                                    <td style="padding: 10px;">${customer.company || '-'}</td>
                                    <td style="padding: 10px;"><span class="status status-${customer.status}">${customer.status}</span></td>
                                    <td style="padding: 10px;">${new Date(customer.created_at).toLocaleDateString()}</td>
                                    <td style="padding: 10px; text-align: center;">
                                        <button onclick="openCustomerModal('${customer.id}')" style="background-color: transparent; color: var(--servicenow-blue); border: none; cursor: pointer;">View</button>
                                    </td>
                                `;
                                
                                tableBody.appendChild(row);
                            });
                        })
                        .catch(error => {
                            document.getElementById('customers-table-body').innerHTML = 
                                `<tr><td colspan="6" style="text-align: center; padding: 20px;">Error loading customers: ${error.message}</td></tr>`;
                        });
                }
                
                // Function to load reports data
                function loadReportsData() {
                    // Load customer status counts
                    fetch('/api/customers')
                        .then(response => response.json())
                        .then(data => {
                            if (data.error) return;
                            
                            let prospectCount = 0;
                            let leadCount = 0;
                            let customerCount = 0;
                            
                            data.forEach(customer => {
                                if (customer.status === 'prospect') prospectCount++;
                                if (customer.status === 'lead') leadCount++;
                                if (customer.status === 'customer') customerCount++;
                            });
                            
                            document.getElementById('prospect-count').textContent = prospectCount;
                            document.getElementById('lead-count').textContent = leadCount;
                            document.getElementById('customer-count').textContent = customerCount;
                            
                            // Update chart heights based on counts
                            const maxHeight = 180;
                            const maxCount = Math.max(prospectCount, leadCount, customerCount) || 1;
                            
                            const prospectHeight = (prospectCount / maxCount) * maxHeight;
                            const leadHeight = (leadCount / maxCount) * maxHeight;
                            const customerHeight = (customerCount / maxCount) * maxHeight;
                            
                            document.querySelector('#main-reports .card:first-child div div:nth-child(1) div').style.height = `${prospectHeight}px`;
                            document.querySelector('#main-reports .card:first-child div div:nth-child(2) div').style.height = `${leadHeight}px`;
                            document.querySelector('#main-reports .card:first-child div div:nth-child(3) div').style.height = `${customerHeight}px`;
                            
                            // Generate top companies list
                            const companies = {};
                            data.forEach(customer => {
                                if (customer.company) {
                                    companies[customer.company] = (companies[customer.company] || 0) + 1;
                                }
                            });
                            
                            const topCompanies = Object.entries(companies)
                                .sort((a, b) => b[1] - a[1])
                                .slice(0, 5);
                            
                            const topCompaniesEl = document.getElementById('top-companies');
                            topCompaniesEl.innerHTML = '';
                            
                            if (topCompanies.length === 0) {
                                topCompaniesEl.innerHTML = '<p style="text-align: center; color: var(--servicenow-dark-gray);">No company data available</p>';
                                return;
                            }
                            
                            topCompanies.forEach(([company, count]) => {
                                const item = document.createElement('div');
                                item.style.padding = '10px';
                                item.style.borderBottom = '1px solid var(--servicenow-border)';
                                item.style.display = 'flex';
                                item.style.justifyContent = 'space-between';
                                
                                item.innerHTML = `
                                    <span>${company}</span>
                                    <span style="font-weight: 500;">${count} customer${count > 1 ? 's' : ''}</span>
                                `;
                                
                                topCompaniesEl.appendChild(item);
                            });
                        });
                    
                    // Load interaction counts
                    let callCount = 0;
                    let emailCount = 0;
                    let meetingCount = 0;
                    let recentActivity = [];
                    
                    // This is a simplified approach since we don't have an API endpoint for all interactions
                    // In a real app, we would have a dedicated endpoint for this data
                    fetch('/api/customers')
                        .then(response => response.json())
                        .then(customers => {
                            if (customers.error) return;
                            
                            // Process each customer's interactions
                            const promises = customers.map(customer => {
                                return fetch(`/api/customers/${customer.id}/interactions`)
                                    .then(response => response.json())
                                    .then(interactions => {
                                        if (interactions.error) return;
                                        
                                        interactions.forEach(interaction => {
                                            if (interaction.type === 'call') callCount++;
                                            if (interaction.type === 'email') emailCount++;
                                            if (interaction.type === 'meeting') meetingCount++;
                                            
                                            recentActivity.push({
                                                ...interaction,
                                                customer: `${customer.first_name} ${customer.last_name}`
                                            });
                                        });
                                    });
                            });
                            
                            // When all interaction data is loaded
                            Promise.all(promises).then(() => {
                                document.getElementById('call-count').textContent = callCount;
                                document.getElementById('email-count').textContent = emailCount;
                                document.getElementById('meeting-count').textContent = meetingCount;
                                
                                // Update chart heights based on counts
                                const maxHeight = 180;
                                const maxCount = Math.max(callCount, emailCount, meetingCount) || 1;
                                
                                const callHeight = (callCount / maxCount) * maxHeight;
                                const emailHeight = (emailCount / maxCount) * maxHeight;
                                const meetingHeight = (meetingCount / maxCount) * maxHeight;
                                
                                document.querySelector('#main-reports .card:nth-child(2) div div:nth-child(1) div').style.height = `${callHeight}px`;
                                document.querySelector('#main-reports .card:nth-child(2) div div:nth-child(2) div').style.height = `${emailHeight}px`;
                                document.querySelector('#main-reports .card:nth-child(2) div div:nth-child(3) div').style.height = `${meetingHeight}px`;
                                
                                // Sort recent activity by date
                                recentActivity.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
                                
                                // Display recent activity
                                const recentActivityEl = document.getElementById('recent-activity');
                                recentActivityEl.innerHTML = '';
                                
                                if (recentActivity.length === 0) {
                                    recentActivityEl.innerHTML = '<p style="text-align: center; color: var(--servicenow-dark-gray);">No recent activity</p>';
                                    return;
                                }
                                
                                recentActivity.slice(0, 10).forEach(activity => {
                                    const item = document.createElement('div');
                                    item.style.padding = '10px';
                                    item.style.borderBottom = '1px solid var(--servicenow-border)';
                                    
                                    // Get icon based on interaction type
                                    let icon = '📞'; // default phone icon
                                    if (activity.type === 'email') icon = '✉️';
                                    if (activity.type === 'meeting') icon = '👥';
                                    
                                    item.innerHTML = `
                                        <div style="display: flex; align-items: flex-start;">
                                            <div style="font-size: 18px; margin-right: 10px;">${icon}</div>
                                            <div>
                                                <p style="margin: 0; font-weight: 500;">${activity.customer}</p>
                                                <p style="margin: 5px 0 0 0;">${activity.notes}</p>
                                                <p style="margin: 5px 0 0 0; font-size: 12px; color: var(--servicenow-dark-gray);">${new Date(activity.created_at).toLocaleString()}</p>
                                            </div>
                                        </div>
                                    `;
                                    
                                    recentActivityEl.appendChild(item);
                                });
                            });
                        });
                }
            </script>
        </body>
    </html>
    """

# API Endpoints

# Customer endpoints
@app.route('/api/customers', methods=['GET'])
def get_customers():
    try:
        customers = Customer.query.all()
        return jsonify([customer.to_dict() for customer in customers])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify(customer.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        return jsonify({"error": str(e)}), 500

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
        return jsonify({"error": str(e)}), 500

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
        return jsonify({"error": str(e)}), 500

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
        return jsonify({"error": str(e)}), 500

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
        return jsonify({"error": str(e)}), 500


