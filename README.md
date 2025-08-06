# Insurance Tracker Portal

## Overview

Insurance Tracker Portal is a comprehensive web application built in Flask to help users manage and track insurance policies and claims. It supports multiple user roles (admin, agent, user) with role-based dashboards and permissions. The portal also features automated backups and notifications for policy and claim updates.

## System Architecture

- **Backend:** Flask web framework with SQLAlchemy ORM.
- **Database:** SQLite (development) and PostgreSQL (production).
- **Frontend:** Jinja2 server-side templates with Bootstrap 5.
- **Authentication:** Flask-Login for session management.
- **Forms:** WTForms for form handling and validation.
- **File Handling:** Secure document uploads.

## Key Components

- **Models (models.py):**
  - User: Account management, roles (admin/agent/user).
  - Policy: Insurance policy information linked to users.
  - Claim: Tracks submitted claims.
  - Notification: System notifications for users.

- **Forms (forms.py):**
  - LoginForm: User authentication.
  - RegistrationForm: New users and role selection.
  - PolicyForm: Create/edit insurance policies.
  - ClaimForm: Submit and manage claims.

- **Routes (routes.py):**
  - Authentication (login/register/logout).
  - Dashboards (role-specific).
  - Policy management (CRUD).
  - Claim management (submission/tracking).
  - Admin features (user management, backups).

- **Backup System (backup_manager.py):**
  - JSON-based automated backup and restore for data safety.

## Data Flow

1. **User Authentication:** Flask-Login session management.
2. **Role-Based Access:** Dashboards and permissions based on user roles.
3. **Policy Management:** Create, view, edit, and manage policies.
4. **Claim Processing:** Submit and track claims with status updates.
5. **File Management:** Secure document storage for uploads.
6. **Notifications:** Alerts for policy expiration/claim updates.

## External Dependencies

- Flask
- SQLAlchemy
- Flask-Login
- WTForms
- Bootstrap 5
- Font Awesome
- Gunicorn (production/server)

## Deployment

- **Development:** Flask dev server (debug mode).
- **Production:** Gunicorn WSGI server with autoscaling.
- **Database:** PostgreSQL recommended for production; SQLite fallback for development.
- **Environment Variables:** Session secrets and database URLs should be set via environment variables.

## Features

- Role-based dashboards and access control.
- Insurance policy and claim management.
- Automated JSON data backup and restore.
- Notification system for policy expiry and claim status.
- Responsive UI with Bootstrap 5.
- Secure file upload and management.


## Getting Started

1. Clone the repository.
2. Install Python dependencies:  
   `pip install -r requirements.txt`
3. Set up environment variables for secrets and database URLs.
4. Run the development server:  
   `flask run`
5. (Optional) Set up PostgreSQL for production.


