PROJECT TITLE: Django Billing System

DESCRIPTION:
A backend application developed for Mallow Technologies to manage product billing and automated invoicing.

CORE FEATURES:
1. Asynchronous Emailing: Uses Celery and Redis to send HTML invoices in the background.
2. Currency Denomination Logic: Calculates change breakdown (500, 200, 100, etc.) using math.floor logic.
3. Dynamic Tax Calculation: Handles CGST and SGST (9% each) automatically.

TECH STACK:
- Language: Python 3.x
- Framework: Django
- Task Queue: Celery
- Broker: Redis
- Database: PostgreSQL / SQLite

INSTALLATION & SETUP:
1. Clone the repository: git clone https://github.com/sandhiyaarjunan/sandhiya-git.git
2. Create Virtual Environment: python -m venv env
3. Activate Environment: ./env/Scripts/activate
4. Install Requirements: pip install -r requirements.txt
5. Run Migrations: python manage.py migrate

RUNNING THE PROJECT:
- Start Celery: celery -A billing_project worker -l info
- Start Server: python manage.py runserver
