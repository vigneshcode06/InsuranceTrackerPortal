from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app, db
from models import User, Policy, Claim, Notification
from forms import LoginForm, RegistrationForm, PolicyForm, ClaimForm, ClaimUpdateForm, UserManagementForm
from backup_manager import BackupManager
import os
import json
from datetime import datetime, date, timedelta
from sqlalchemy import or_, and_

backup_manager = BackupManager()

@app.route('/')
def index():
    return render_template('index.html')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash('Logged in successfully!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        
        # Create backup
        backup_manager.backup_data()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Dashboard routes
@app.route('/dashboard')
@login_required
def dashboard():
    # Create notifications for expiring policies
    create_expiry_notifications()
    
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'agent':
        return redirect(url_for('agent_dashboard'))
    else:
        return redirect(url_for('user_dashboard'))

@app.route('/dashboard/user')
@login_required
def user_dashboard():
    if current_user.role not in ['user', 'agent']:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get user's policies and claims
    policies = Policy.query.filter_by(user_id=current_user.id).all()
    claims = Claim.query.filter_by(user_id=current_user.id).order_by(Claim.created_at.desc()).limit(5).all()
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
    
    # Calculate statistics
    total_policies = len(policies)
    active_policies = len([p for p in policies if p.status == 'active'])
    expiring_policies = len([p for p in policies if p.is_expiring_soon and p.status == 'active'])
    total_claims = Claim.query.filter_by(user_id=current_user.id).count()
    
    stats = {
        'total_policies': total_policies,
        'active_policies': active_policies,
        'expiring_policies': expiring_policies,
        'total_claims': total_claims
    }
    
    return render_template('dashboard/user.html', stats=stats, policies=policies, 
                         claims=claims, notifications=notifications)

@app.route('/dashboard/agent')
@login_required
def agent_dashboard():
    if current_user.role != 'agent':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get all policies and claims for agent view
    policies = Policy.query.all()
    claims = Claim.query.order_by(Claim.created_at.desc()).limit(10).all()
    
    # Calculate statistics
    total_policies = Policy.query.count()
    active_policies = Policy.query.filter_by(status='active').count()
    total_claims = Claim.query.count()
    pending_claims = Claim.query.filter_by(status='pending').count()
    
    stats = {
        'total_policies': total_policies,
        'active_policies': active_policies,
        'total_claims': total_claims,
        'pending_claims': pending_claims
    }
    
    return render_template('dashboard/agent.html', stats=stats, policies=policies, claims=claims)

@app.route('/dashboard/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get platform statistics
    total_users = User.query.count()
    total_policies = Policy.query.count()
    total_claims = Claim.query.count()
    pending_claims = Claim.query.filter_by(status='pending').count()
    
    # Recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_policies = Policy.query.order_by(Policy.created_at.desc()).limit(5).all()
    recent_claims = Claim.query.order_by(Claim.created_at.desc()).limit(5).all()
    
    stats = {
        'total_users': total_users,
        'total_policies': total_policies,
        'total_claims': total_claims,
        'pending_claims': pending_claims
    }
    
    return render_template('dashboard/admin.html', stats=stats, recent_users=recent_users,
                         recent_policies=recent_policies, recent_claims=recent_claims)

# Policy routes
@app.route('/policies')
@login_required
def policy_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    policy_type = request.args.get('type', '')
    status = request.args.get('status', '')
    
    query = Policy.query
    
    # Filter by user role
    if current_user.role == 'user':
        query = query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if search:
        query = query.filter(or_(
            Policy.policy_number.contains(search),
            Policy.provider_name.contains(search)
        ))
    
    if policy_type:
        query = query.filter_by(policy_type=policy_type)
    
    if status:
        query = query.filter_by(status=status)
    
    policies = query.order_by(Policy.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('policies/list.html', policies=policies, search=search,
                         policy_type=policy_type, status=status)

@app.route('/policies/add', methods=['GET', 'POST'])
@login_required
def add_policy():
    form = PolicyForm()
    
    if form.validate_on_submit():
        policy = Policy(
            policy_number=form.policy_number.data,
            policy_type=form.policy_type.data,
            provider_name=form.provider_name.data,
            provider_contact=form.provider_contact.data,
            premium_amount=form.premium_amount.data,
            coverage_amount=form.coverage_amount.data,
            issue_date=form.issue_date.data,
            expiry_date=form.expiry_date.data,
            description=form.description.data,
            user_id=current_user.id
        )
        
        db.session.add(policy)
        db.session.commit()
        
        # Create backup
        backup_manager.backup_data()
        
        flash('Policy added successfully!', 'success')
        return redirect(url_for('policy_list'))
    
    return render_template('policies/form.html', form=form, title='Add Policy')

@app.route('/policies/<int:id>')
@login_required
def view_policy(id):
    policy = Policy.query.get_or_404(id)
    
    # Check access permissions
    if current_user.role == 'user' and policy.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('policy_list'))
    
    claims = Claim.query.filter_by(policy_id=id).order_by(Claim.created_at.desc()).all()
    
    return render_template('policies/view.html', policy=policy, claims=claims)

@app.route('/policies/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_policy(id):
    policy = Policy.query.get_or_404(id)
    
    # Check access permissions
    if current_user.role == 'user' and policy.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('policy_list'))
    
    form = PolicyForm(obj=policy)
    form.policy_id = id  # For validation
    
    if form.validate_on_submit():
        policy.policy_number = form.policy_number.data
        policy.policy_type = form.policy_type.data
        policy.provider_name = form.provider_name.data
        policy.provider_contact = form.provider_contact.data
        policy.premium_amount = form.premium_amount.data
        policy.coverage_amount = form.coverage_amount.data
        policy.issue_date = form.issue_date.data
        policy.expiry_date = form.expiry_date.data
        policy.description = form.description.data
        policy.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Create backup
        backup_manager.backup_data()
        
        flash('Policy updated successfully!', 'success')
        return redirect(url_for('view_policy', id=id))
    
    return render_template('policies/form.html', form=form, title='Edit Policy', policy=policy)

@app.route('/policies/<int:id>/delete', methods=['POST'])
@login_required
def delete_policy(id):
    policy = Policy.query.get_or_404(id)
    
    # Check access permissions
    if current_user.role == 'user' and policy.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('policy_list'))
    
    db.session.delete(policy)
    db.session.commit()
    
    # Create backup
    backup_manager.backup_data()
    
    flash('Policy deleted successfully!', 'success')
    return redirect(url_for('policy_list'))

# Claim routes
@app.route('/claims')
@login_required
def claim_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    
    query = Claim.query
    
    # Filter by user role
    if current_user.role == 'user':
        query = query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if search:
        query = query.filter(or_(
            Claim.claim_number.contains(search),
            Claim.description.contains(search)
        ))
    
    if status:
        query = query.filter_by(status=status)
    
    claims = query.order_by(Claim.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('claims/list.html', claims=claims, search=search, status=status)

@app.route('/claims/add', methods=['GET', 'POST'])
@login_required
def add_claim():
    form = ClaimForm()
    
    # Populate policy choices
    if current_user.role == 'user':
        policies = Policy.query.filter_by(user_id=current_user.id, status='active').all()
    else:
        policies = Policy.query.filter_by(status='active').all()
    
    form.policy_id.choices = [(p.id, f"{p.policy_number} - {p.policy_type.title()}") for p in policies]
    
    if form.validate_on_submit():
        # Handle file uploads
        uploaded_files = []
        if form.documents.data:
            for file in form.documents.data:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    uploaded_files.append(filename)
        
        claim = Claim(
            claim_number=form.claim_number.data,
            policy_id=form.policy_id.data,
            claim_amount=form.claim_amount.data,
            incident_date=form.incident_date.data,
            description=form.description.data,
            documents=json.dumps(uploaded_files) if uploaded_files else None,
            user_id=current_user.id
        )
        
        db.session.add(claim)
        db.session.commit()
        
        # Create notification
        notification = Notification(
            title='New Claim Submitted',
            message=f'Claim {claim.claim_number} has been submitted for review.',
            notification_type='claim',
            user_id=current_user.id
        )
        db.session.add(notification)
        db.session.commit()
        
        # Create backup
        backup_manager.backup_data()
        
        flash('Claim submitted successfully!', 'success')
        return redirect(url_for('claim_list'))
    
    return render_template('claims/form.html', form=form, title='Submit Claim')

@app.route('/claims/<int:id>')
@login_required
def view_claim(id):
    claim = Claim.query.get_or_404(id)
    
    # Check access permissions
    if current_user.role == 'user' and claim.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('claim_list'))
    
    # Parse documents
    documents = []
    if claim.documents:
        try:
            documents = json.loads(claim.documents)
        except:
            pass
    
    return render_template('claims/view.html', claim=claim, documents=documents)

@app.route('/claims/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_claim(id):
    if current_user.role not in ['admin', 'agent']:
        flash('Access denied.', 'danger')
        return redirect(url_for('claim_list'))
    
    claim = Claim.query.get_or_404(id)
    form = ClaimUpdateForm(obj=claim)
    
    if form.validate_on_submit():
        old_status = claim.status
        claim.status = form.status.data
        claim.remarks = form.remarks.data
        claim.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Create notification if status changed
        if old_status != claim.status:
            notification = Notification(
                title='Claim Status Updated',
                message=f'Claim {claim.claim_number} status changed to {claim.status}.',
                notification_type='claim',
                user_id=claim.user_id
            )
            db.session.add(notification)
            db.session.commit()
        
        # Create backup
        backup_manager.backup_data()
        
        flash('Claim updated successfully!', 'success')
        return redirect(url_for('view_claim', id=id))
    
    return render_template('claims/form.html', form=form, title='Update Claim', claim=claim)

# File download route
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# Admin routes
@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role = request.args.get('role', '')
    
    query = User.query
    
    if search:
        query = query.filter(or_(
            User.username.contains(search),
            User.email.contains(search),
            User.full_name.contains(search)
        ))
    
    if role:
        query = query.filter_by(role=role)
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('admin/users.html', users=users, search=search, role=role)

@app.route('/admin/users/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_user_status(id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Cannot deactivate your own account.', 'warning')
        return redirect(url_for('admin_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    # Create backup
    backup_manager.backup_data()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin_users'))

# Notification routes
@app.route('/notifications/mark_read/<int:id>')
@login_required
def mark_notification_read(id):
    notification = Notification.query.get_or_404(id)
    if notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()
    return redirect(request.referrer or url_for('dashboard'))

# Backup routes
@app.route('/backup/create')
@login_required
def create_backup():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        backup_manager.backup_data()
        flash('Backup created successfully!', 'success')
    except Exception as e:
        flash(f'Error creating backup: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/backup/restore', methods=['POST'])
@login_required
def restore_backup():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        backup_manager.restore_data()
        flash('Data restored from backup successfully!', 'success')
    except Exception as e:
        flash(f'Error restoring backup: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

# Utility functions
def create_expiry_notifications():
    """Create notifications for policies expiring within 30 days"""
    expiring_policies = Policy.query.filter(
        and_(
            Policy.status == 'active',
            Policy.expiry_date <= date.today() + timedelta(days=30),
            Policy.expiry_date > date.today()
        )
    ).all()
    
    for policy in expiring_policies:
        # Check if notification already exists
        existing = Notification.query.filter_by(
            user_id=policy.user_id,
            notification_type='expiry',
            message=f'Policy {policy.policy_number} expires on {policy.expiry_date}.'
        ).first()
        
        if not existing:
            notification = Notification(
                title='Policy Expiring Soon',
                message=f'Policy {policy.policy_number} expires on {policy.expiry_date}.',
                notification_type='expiry',
                user_id=policy.user_id
            )
            db.session.add(notification)
    
    db.session.commit()

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
