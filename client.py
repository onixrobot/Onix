#!/usr/bin/env python3
"""
Command-line client for the Enterprise CRM API.
"""
import sys
import json
import requests
from datetime import datetime
import argparse
import textwrap

BASE_URL = "http://localhost:5000/api"


def format_customer(customer):
    """Format a customer record for display"""
    created_at = datetime.fromisoformat(customer['created_at'].replace('Z', '+00:00'))
    updated_at = datetime.fromisoformat(customer['updated_at'].replace('Z', '+00:00'))

    return f"""ID: {customer['id']}
Name: {customer['first_name']} {customer['last_name']}
Email: {customer['email']}
Company: {customer['company']}
Status: {customer['status']}
Created: {created_at.strftime('%Y-%m-%d %H:%M:%S')}
Updated: {updated_at.strftime('%Y-%m-%d %H:%M:%S')}
"""

def format_interaction(interaction):
    """Format an interaction record for display"""
    created_at = datetime.fromisoformat(interaction['created_at'].replace('Z', '+00:00'))

    return f"""ID: {interaction['id']}
Type: {interaction['type']}
Notes: {textwrap.fill(interaction['notes'], width=60)}
Created: {created_at.strftime('%Y-%m-%d %H:%M:%S')}
"""

def fetch_data(endpoint):
    """Helper function to fetch data from a given API endpoint"""
    try:
        with requests.Session() as session:
            session.headers.update({'Content-Type': 'application/json'})
            response = session.get(f"{BASE_URL}{endpoint}")
            response.raise_for_status()
            return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Request timeout: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    return None

def list_customers():
    """List all customers"""
    customers = fetch_data("/customers")

    if not customers:
        print("No customers found.")
        return

    print(f"Found {len(customers)} customers:\n")
    for i, customer in enumerate(customers, 1):
        print(f"Customer {i}:")
        print(format_customer(customer))

def get_customer(customer_id):
    """Get details for a specific customer"""
    customer = fetch_data(f"/customers/{customer_id}")

    if customer:
        print("Customer details:")
        print(format_customer(customer))

        # Also get interactions
        interactions = fetch_data(f"/customers/{customer_id}/interactions")

        if interactions:
            print(f"Customer has {len(interactions)} interactions:")
            for i, interaction in enumerate(interactions, 1):
                print(f"\nInteraction {i}:")
                print(format_interaction(interaction))
        else:
            print("No interactions found for this customer.")

def create_customer(first_name, last_name, email, company, status):
    """Create a new customer"""
    customer_data = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'company': company,
        'status': status
    }

    try:
        response = requests.post(
            f"{BASE_URL}/customers",
            json=customer_data
        )

        if response.status_code == 201:
            customer = response.json()
            print("Customer created successfully:")
            print(format_customer(customer))
        else:
            error_data = response.json()
            print(f"Error: {error_data.get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def add_interaction(customer_id, interaction_type, notes):
    """Add a new interaction for a customer"""
    interaction_data = {
        'customer_id': customer_id,
        'type': interaction_type,
        'notes': notes
    }

    try:
        response = requests.post(
            f"{BASE_URL}/interactions",
            json=interaction_data
        )

        if response.status_code == 201:
            interaction = response.json()
            print("Interaction added successfully:")
            print(format_interaction(interaction))
        else:
            error_data = response.json()
            print(f"Error: {error_data.get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def delete_customer(customer_id):
    """Delete a customer"""
    try:
        response = requests.delete(f"{BASE_URL}/customers/{customer_id}")

        if response.status_code == 200:
            print(f"Customer {customer_id} deleted successfully.")
        else:
            error_data = response.json()
            print(f"Error: {error_data.get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Enterprise CRM Command Line Client')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # List customers command
    subparsers.add_parser('list-customers', help='List all customers')

    # Get customer command
    get_customer_parser = subparsers.add_parser('get-customer', help='Get customer details')
    get_customer_parser.add_argument('customer_id', help='Customer ID')

    # Create customer command
    create_customer_parser = subparsers.add_parser('create-customer', help='Create a new customer')
    create_customer_parser.add_argument('first_name', help='First name')
    create_customer_parser.add_argument('last_name', help='Last name')
    create_customer_parser.add_argument('email', help='Email address')
    create_customer_parser.add_argument('--company', help='Company name')
    create_customer_parser.add_argument('--status', choices=['lead', 'prospect', 'customer'], default='lead', help='Customer status')

    # Add interaction command
    add_interaction_parser = subparsers.add_parser('add-interaction', help='Add a new interaction')
    add_interaction_parser.add_argument('customer_id', help='Customer ID')
    add_interaction_parser.add_argument('type', choices=['call', 'email', 'meeting'], help='Interaction type')
    add_interaction_parser.add_argument('notes', help='Interaction notes')

    # Delete customer command
    delete_customer_parser = subparsers.add_parser('delete-customer', help='Delete a customer')
    delete_customer_parser.add_argument('customer_id', help='Customer ID')

    args = parser.parse_args()

    if args.command == 'list-customers':
        list_customers()
    elif args.command == 'get-customer':
        get_customer(args.customer_id)
    elif args.command == 'create-customer':
        create_customer(
            args.first_name,
            args.last_name,
            args.email,
            args.company or '',
            args.status
        )
    elif args.command == 'add-interaction':
        add_interaction(
            args.customer_id,
            args.type,
            args.notes
        )
    elif args.command == 'delete-customer':
        delete_customer(args.customer_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
