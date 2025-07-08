import json
import os
from datetime import datetime
from app import db
from models import User, Policy, Claim, Notification

class BackupManager:
    def __init__(self):
        self.backup_dir = 'backups'
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Create backup directory if it doesn't exist"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def backup_data(self):
        """Create JSON backup of all data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(self.backup_dir, f'backup_{timestamp}.json')
        
        # Collect all data
        backup_data = {
            'timestamp': timestamp,
            'users': [],
            'policies': [],
            'claims': [],
            'notifications': []
        }
        
        # Backup users
        users = User.query.all()
        for user in users:
            backup_data['users'].append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'password_hash': user.password_hash,
                'full_name': user.full_name,
                'role': user.role,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'is_active': user.is_active
            })
        
        # Backup policies
        policies = Policy.query.all()
        for policy in policies:
            backup_data['policies'].append({
                'id': policy.id,
                'policy_number': policy.policy_number,
                'policy_type': policy.policy_type,
                'provider_name': policy.provider_name,
                'provider_contact': policy.provider_contact,
                'premium_amount': float(policy.premium_amount),
                'coverage_amount': float(policy.coverage_amount),
                'issue_date': policy.issue_date.isoformat() if policy.issue_date else None,
                'expiry_date': policy.expiry_date.isoformat() if policy.expiry_date else None,
                'status': policy.status,
                'description': policy.description,
                'created_at': policy.created_at.isoformat() if policy.created_at else None,
                'updated_at': policy.updated_at.isoformat() if policy.updated_at else None,
                'user_id': policy.user_id
            })
        
        # Backup claims
        claims = Claim.query.all()
        for claim in claims:
            backup_data['claims'].append({
                'id': claim.id,
                'claim_number': claim.claim_number,
                'claim_amount': float(claim.claim_amount),
                'incident_date': claim.incident_date.isoformat() if claim.incident_date else None,
                'claim_date': claim.claim_date.isoformat() if claim.claim_date else None,
                'status': claim.status,
                'description': claim.description,
                'documents': claim.documents,
                'remarks': claim.remarks,
                'created_at': claim.created_at.isoformat() if claim.created_at else None,
                'updated_at': claim.updated_at.isoformat() if claim.updated_at else None,
                'user_id': claim.user_id,
                'policy_id': claim.policy_id
            })
        
        # Backup notifications
        notifications = Notification.query.all()
        for notification in notifications:
            backup_data['notifications'].append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'notification_type': notification.notification_type,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat() if notification.created_at else None,
                'user_id': notification.user_id
            })
        
        # Write to file
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        # Also create/update latest backup
        latest_backup = os.path.join(self.backup_dir, 'latest_backup.json')
        with open(latest_backup, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        return backup_file
    
    def restore_data(self, backup_file=None):
        """Restore data from JSON backup"""
        if not backup_file:
            backup_file = os.path.join(self.backup_dir, 'latest_backup.json')
        
        if not os.path.exists(backup_file):
            raise FileNotFoundError("Backup file not found")
        
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        # Clear existing data (be careful!)
        db.session.query(Notification).delete()
        db.session.query(Claim).delete()
        db.session.query(Policy).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        # Restore users
        for user_data in backup_data.get('users', []):
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                full_name=user_data['full_name'],
                role=user_data['role'],
                created_at=datetime.fromisoformat(user_data['created_at']) if user_data['created_at'] else None,
                is_active=user_data['is_active']
            )
            db.session.add(user)
        
        db.session.commit()
        
        # Restore policies
        for policy_data in backup_data.get('policies', []):
            policy = Policy(
                policy_number=policy_data['policy_number'],
                policy_type=policy_data['policy_type'],
                provider_name=policy_data['provider_name'],
                provider_contact=policy_data['provider_contact'],
                premium_amount=policy_data['premium_amount'],
                coverage_amount=policy_data['coverage_amount'],
                issue_date=datetime.fromisoformat(policy_data['issue_date']).date() if policy_data['issue_date'] else None,
                expiry_date=datetime.fromisoformat(policy_data['expiry_date']).date() if policy_data['expiry_date'] else None,
                status=policy_data['status'],
                description=policy_data['description'],
                created_at=datetime.fromisoformat(policy_data['created_at']) if policy_data['created_at'] else None,
                updated_at=datetime.fromisoformat(policy_data['updated_at']) if policy_data['updated_at'] else None,
                user_id=policy_data['user_id']
            )
            db.session.add(policy)
        
        db.session.commit()
        
        # Restore claims
        for claim_data in backup_data.get('claims', []):
            claim = Claim(
                claim_number=claim_data['claim_number'],
                claim_amount=claim_data['claim_amount'],
                incident_date=datetime.fromisoformat(claim_data['incident_date']).date() if claim_data['incident_date'] else None,
                claim_date=datetime.fromisoformat(claim_data['claim_date']).date() if claim_data['claim_date'] else None,
                status=claim_data['status'],
                description=claim_data['description'],
                documents=claim_data['documents'],
                remarks=claim_data['remarks'],
                created_at=datetime.fromisoformat(claim_data['created_at']) if claim_data['created_at'] else None,
                updated_at=datetime.fromisoformat(claim_data['updated_at']) if claim_data['updated_at'] else None,
                user_id=claim_data['user_id'],
                policy_id=claim_data['policy_id']
            )
            db.session.add(claim)
        
        db.session.commit()
        
        # Restore notifications
        for notification_data in backup_data.get('notifications', []):
            notification = Notification(
                title=notification_data['title'],
                message=notification_data['message'],
                notification_type=notification_data['notification_type'],
                is_read=notification_data['is_read'],
                created_at=datetime.fromisoformat(notification_data['created_at']) if notification_data['created_at'] else None,
                user_id=notification_data['user_id']
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return True
    
    def list_backups(self):
        """List all available backup files"""
        backups = []
        if os.path.exists(self.backup_dir):
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('backup_') and filename.endswith('.json'):
                    file_path = os.path.join(self.backup_dir, filename)
                    timestamp = os.path.getmtime(file_path)
                    backups.append({
                        'filename': filename,
                        'timestamp': datetime.fromtimestamp(timestamp),
                        'size': os.path.getsize(file_path)
                    })
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
