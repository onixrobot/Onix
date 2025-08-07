import pytest
import json
from app import app, db, Customer, Interaction

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        
        # Add test data
        test_customer = Customer(
            id='test-customer-id',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            company='Test Company',
            status='customer'
        )
        db.session.add(test_customer)
        db.session.commit()
    
    with app.test_client() as client:
        yield client
    
    with app.app_context():
        db.drop_all()

def test_home_page(client):
    """Test that the home page loads correctly"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Onyx CRM" in response.data

def test_get_customers(client):
    """Test getting all customers"""
    response = client.get('/api/customers')
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['email'] == 'test@example.com'

def test_get_customer(client):
    """Test getting a single customer"""
    response = client.get('/api/customers/test-customer-id')
    data = response.get_json()
    assert response.status_code == 200
    assert data['first_name'] == 'Test'
    assert data['last_name'] == 'User'

def test_get_nonexistent_customer(client):
    """Test getting a customer that doesn't exist"""
    response = client.get('/api/customers/nonexistent-id')
    data = response.get_json()
    assert response.status_code == 404
    assert 'error' in data

def test_create_customer(client):
    """Test creating a new customer"""
    new_customer = {
        'first_name': 'Jane',
        'last_name': 'Doe',
        'email': 'jane.doe@example.com',
        'company': 'Jane Corp',
        'status': 'lead'
    }
    
    response = client.post(
        '/api/customers',
        data=json.dumps(new_customer),
        content_type='application/json'
    )
    
    data = response.get_json()
    assert response.status_code == 201
    assert data['first_name'] == 'Jane'
    assert data['email'] == 'jane.doe@example.com'
    
    # Verify customer was added to database
    get_response = client.get('/api/customers')
    customers = get_response.get_json()
    assert len(customers) == 2

def test_create_customer_duplicate_email(client):
    """Test creating a customer with an email that already exists"""
    duplicate_customer = {
        'first_name': 'Another',
        'last_name': 'User',
        'email': 'test@example.com',  # This email already exists
        'company': 'Another Company'
    }
    
    response = client.post(
        '/api/customers',
        data=json.dumps(duplicate_customer),
        content_type='application/json'
    )
    
    data = response.get_json()
    assert response.status_code == 400
    assert 'error' in data
    assert 'already exists' in data['error']

def test_create_customer_missing_fields(client):
    """Test creating a customer with missing required fields"""
    incomplete_customer = {
        'first_name': 'Incomplete',
        # Missing last_name and email
        'company': 'Incomplete Corp'
    }
    
    response = client.post(
        '/api/customers',
        data=json.dumps(incomplete_customer),
        content_type='application/json'
    )
    
    data = response.get_json()
    assert response.status_code == 400
    assert 'error' in data

def test_update_customer(client):
    """Test updating a customer"""
    update_data = {
        'first_name': 'Updated',
        'company': 'Updated Company'
    }
    
    response = client.put(
        '/api/customers/test-customer-id',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    
    data = response.get_json()
    assert response.status_code == 200
    assert data['first_name'] == 'Updated'
    assert data['last_name'] == 'User'  # Unchanged
    assert data['company'] == 'Updated Company'

def test_delete_customer(client):
    """Test deleting a customer"""
    response = client.delete('/api/customers/test-customer-id')
    assert response.status_code == 200
    
    # Verify customer was deleted
    get_response = client.get('/api/customers/test-customer-id')
    assert get_response.status_code == 404

def test_create_interaction(client):
    """Test creating a new interaction"""
    new_interaction = {
        'customer_id': 'test-customer-id',
        'type': 'call',
        'notes': 'Test interaction notes'
    }
    
    response = client.post(
        '/api/interactions',
        data=json.dumps(new_interaction),
        content_type='application/json'
    )
    
    data = response.get_json()
    assert response.status_code == 201
    assert data['type'] == 'call'
    assert data['notes'] == 'Test interaction notes'
    
    # Verify interaction was added
    get_response = client.get('/api/customers/test-customer-id/interactions')
    interactions = get_response.get_json()
    assert len(interactions) == 1
    assert interactions[0]['notes'] == 'Test interaction notes'

def test_get_customer_interactions(client):
    """Test getting interactions for a customer"""
    # First add an interaction
    new_interaction = {
        'customer_id': 'test-customer-id',
        'type': 'email',
        'notes': 'Another test interaction'
    }
    
    client.post(
        '/api/interactions',
        data=json.dumps(new_interaction),
        content_type='application/json'
    )
    
    # Now get the interactions
    response = client.get('/api/customers/test-customer-id/interactions')
    interactions = response.get_json()
    
    assert response.status_code == 200
    assert len(interactions) >= 1  # There might be more from other tests
