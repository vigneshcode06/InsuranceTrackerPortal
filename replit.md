# Insurance Tracker Portal

## Overview

The Insurance Tracker Portal is a comprehensive web application built with Flask that allows users to manage insurance policies, track claims, and maintain organized records. The system supports multiple user roles (admin, agent, user) with different access levels and capabilities.

## System Architecture

The application follows a traditional Flask web application architecture with the following structure:

- **Backend**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite (development) with PostgreSQL support configured
- **Frontend**: Server-side rendered templates using Jinja2 with Bootstrap 5
- **Authentication**: Flask-Login for session management
- **Forms**: WTForms for form handling and validation
- **File Handling**: Support for document uploads with secure file storage

## Key Components

### Models (models.py)
- **User**: Manages user accounts with roles (admin, agent, user)
- **Policy**: Stores insurance policy information with relationships to users
- **Claim**: Tracks insurance claims linked to policies
- **Notification**: Handles user notifications

### Forms (forms.py)
- **LoginForm**: User authentication
- **RegistrationForm**: New user registration with role selection
- **PolicyForm**: Insurance policy creation and editing
- **ClaimForm**: Claim submission and management

### Routes (routes.py)
- Authentication endpoints (login, register, logout)
- Dashboard views (role-specific dashboards)
- Policy management (CRUD operations)
- Claim management (submission and tracking)
- Admin functionality (user management, backups)

### Backup System (backup_manager.py)
- JSON-based data backup and restore functionality
- Automated backup creation for data protection

## Data Flow

1. **User Authentication**: Users log in through Flask-Login session management
2. **Role-Based Access**: Different dashboard views and permissions based on user roles
3. **Policy Management**: Users can create, view, edit, and manage insurance policies
4. **Claim Processing**: Claims are submitted against policies and tracked through status updates
5. **File Management**: Document uploads are securely stored in the uploads directory
6. **Notifications**: System generates notifications for policy expiration and claim updates

## External Dependencies

- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Flask-Login**: Authentication management
- **WTForms**: Form handling and validation
- **Bootstrap 5**: Frontend UI framework
- **Font Awesome**: Icon library
- **Gunicorn**: WSGI server for production deployment

## Deployment Strategy

The application is configured for deployment on Replit with:
- **Development**: Flask development server with debug mode
- **Production**: Gunicorn WSGI server with autoscale deployment
- **Database**: PostgreSQL module configured with SQLite fallback
- **Environment Variables**: Session secrets and database URLs via environment variables

The application supports both SQLite (for development) and PostgreSQL (for production) databases through environment configuration.

## Changelog

- June 20, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.