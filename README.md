# Inventory Management System

A Python REST API with Flask for managing an inventory of products. The project includes full CRUD functionality, OpenFoodFacts integration, a command-line interface (CLI), automated testing, and a Git-based feature development workflow.

## Features

- View all inventory items
- View a single inventory item
- Add a new inventory item
- Update inventory item price and stock
- Delete inventory items
- Search OpenFoodFacts by barcode
- Search OpenFoodFacts by product name
- Import OpenFoodFacts products into the inventory
- Command-line inventory management interface
- Automated tests using pytest
- Mocked external API and CLI tests using unittest.mock

## Technologies

- Python 3
- Flask
- Requests
- pytest
- unittest.mock
- OpenFoodFacts API
- Git and GitHub

## Project Structure

```text
inventory-management/
├── app.py
├── cli.py
├── external_api.py
├── README.md
├── requirements.txt
├── .gitignore
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_cli.py
    └── test_external_api.py