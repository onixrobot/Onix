# Onix CRM

A Flask-based Customer Relationship Management (CRM) application called Onix, designed for enterprise environments. This project showcases a simple but functional CRM system with both API and UI features.

```
  ____  _   ___   ____  __
 / __ \| \ | \ \ / /\ \/ /
| |  | |  \| |\ V /  \  / 
| |__| | |\  | | |   /  \ 
 \____/|_| \_| |_|  /_/\_\
                           
 Customer Relationship Management
```

## Project Overview

This project includes:

1. A web-based Onix CRM Dashboard for managing customers and their interactions
2. RESTful API endpoints for CRUD operations on customers and interactions
3. SQLite database with SQLAlchemy ORM for data persistence
4. Unit tests that verify API functionality
5. A command-line client for interacting with the API

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Onix CRM Architecture                 │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                           Flask App                         │
├──────────────────┬────────────────────────┬─────────────────┤
│   Web Dashboard  │    RESTful API         │  Command-line   │
│   (HTML/CSS/JS)  │    (Flask-RESTful)     │  Client         │
└──────────────────┴────────────────────────┴─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                      SQLAlchemy ORM                         │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       SQLite Database                           │
│                                                                 │
│  ┌─────────────────┐                  ┌─────────────────┐       │
│  │    Customers    │◄────────────────►│   Interactions  │       │
│  └─────────────────┘                  └─────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## Setup and Running Instructions

### Steps to Run Onix CRM Locally

1. **Clone the repository**:
   ```bash
   git clone ssh://gitlab.ifsdev.servicenow.net:29418/project-onix/onix.git
   cd onix
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Flask application**:
   ```bash
   flask run
   ```
   or
   ```bash
   python app.py
   ```

6. **Access the application**:
   Open a web browser and go to http://localhost:5000

### Important Notes

1. The application uses SQLite, so no additional database setup is required. The `crm.db` file is included in the repository.

2. The application will automatically initialize with sample data if the database is empty.

3. The application runs in debug mode by default, which is suitable for development but not for production.

4. All customer emails are set to use the @innovationweek.com domain.

## Features

### Web Dashboard

Access the Onix dashboard at http://localhost:5000 to:

- View a list of all customers
- View customer details and interactions
- Add new customers
- Add new interactions for customers
- View API documentation

### Data Model

```
┌──────────────────────────────────┐
│           Customer               │
├──────────────────────────────────┤
│ id: String(36) PK                │
│ first_name: String(50)           │
│ last_name: String(50)            │
│ email: String(100) UNIQUE        │
│ company: String(100)             │
│ status: String(20)               │
│ created_at: DateTime             │
│ updated_at: DateTime             │
└──────────────────────────────────┘
                │
                │ 1:N
                ▼
┌──────────────────────────────────┐
│          Interaction             │
├──────────────────────────────────┤
│ id: String(36) PK                │
│ customer_id: String(36) FK       │
│ type: String(20)                 │
│ notes: Text                      │
│ created_at: DateTime             │
└──────────────────────────────────┘
```

### API Endpoints

#### Customers

- `GET /api/customers` - Get all customers
- `GET /api/customers/<customer_id>` - Get a specific customer
- `POST /api/customers` - Create a new customer
- `PUT /api/customers/<customer_id>` - Update a customer
- `DELETE /api/customers/<customer_id>` - Delete a customer

#### Interactions

- `GET /api/customers/<customer_id>/interactions` - Get all interactions for a customer
- `POST /api/interactions` - Create a new interaction

## Testing

Run the tests with pytest:

```
pytest test_app.py
```

## Command-line Client

A command-line client is provided to interact with the API:

```
# List all customers
python client.py list-customers

# Get a specific customer
python client.py get-customer <customer_id>

# Create a new customer
python client.py create-customer <first_name> <last_name> <email> [--company <company>] [--status <status>]

# Add an interaction
python client.py add-interaction <customer_id> <type> <notes>

# Delete a customer
python client.py delete-customer <customer_id>
```

## Demo Scenario

1. Show the Onix dashboard and its features
2. Demonstrate API operations using the command-line client
3. Show how to create, view, and manage customers and interactions
4. Highlight the enterprise features like error handling, validation, and database persistence
5. Showcase the responsive UI design and user experience

### Customer Workflow

```
┌──────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│  Create Customer │────►│  Add Interaction │────►│ Update Customer   │
└──────────────────┘     └──────────────────┘     └───────────────────┘
        │                       │                      │
        │                       │                      │
        ▼                       ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Customer Lifecycle                          │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤
│  Prospect   │     Lead    │  Customer   │   Active    │ Former  │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────┘
```

## Potential Extensions

- Add authentication using Flask-JWT-Extended
- Implement role-based access control
- Add more advanced search and filtering capabilities
- Create reporting and analytics features
- Integrate with external services (email, calendar, etc.)

## Documentation

For comprehensive documentation about the Onix CRM system, please refer to the [Onix CRM Knowledge Base](../onix-docs/README.md) which includes:

- [Project Overview](../onix-docs/overview.md)
- [Architecture](../onix-docs/architecture.md)
- [API Documentation](../onix-docs/api.md)
- [Database Schema](../onix-docs/database.md)
- [User Interface](../onix-docs/ui.md)
- [Command-line Client](../onix-docs/client.md)
- [Testing](../onyx-docs/testing.md)
- [Setup and Deployment](../onyx-docs/setup.md)
- [Future Enhancements Roadmap](../onyx-docs/roadmap.md)

## License

MIT
