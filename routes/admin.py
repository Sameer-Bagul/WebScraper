from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from adapters import AdapterManager
from models import Analytics
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def admin_dashboard():
    """Admin dashboard"""
    from app import db
    
    if not db:
        flash('Database connection failed', 'error')
        return redirect(url_for('main.index'))
    
    analytics = Analytics(db)
    stats = analytics.get_dashboard_stats()
    
    adapter_manager = AdapterManager()
    adapters = adapter_manager.list_adapters()
    
    return render_template('admin.html', stats=stats, adapters=adapters)

@admin_bp.route('/adapters')
def manage_adapters():
    """Manage adapters page"""
    adapter_manager = AdapterManager()
    adapters = adapter_manager.list_adapters()
    
    return render_template('adapters.html', adapters=adapters)

@admin_bp.route('/adapter/new', methods=['GET', 'POST'])
def new_adapter():
    """Create new adapter"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            config_json = request.form.get('config', '')
            
            if not name:
                flash('Adapter name is required', 'error')
                return render_template('adapters.html')
            
            # Parse and validate JSON
            try:
                config = json.loads(config_json)
            except json.JSONDecodeError as e:
                flash(f'Invalid JSON configuration: {e}', 'error')
                return render_template('adapters.html')
            
            # Save adapter
            adapter_manager = AdapterManager()
            adapter_manager.save_adapter(name, config)
            
            flash(f'Adapter "{name}" created successfully', 'success')
            return redirect(url_for('admin.manage_adapters'))
            
        except Exception as e:
            flash(f'Error creating adapter: {e}', 'error')
    
    return render_template('adapters.html', new_adapter=True)

@admin_bp.route('/adapter/<name>/edit', methods=['GET', 'POST'])
def edit_adapter(name):
    """Edit existing adapter"""
    adapter_manager = AdapterManager()
    
    if request.method == 'POST':
        try:
            config_json = request.form.get('config', '')
            
            # Parse and validate JSON
            try:
                config = json.loads(config_json)
            except json.JSONDecodeError as e:
                flash(f'Invalid JSON configuration: {e}', 'error')
                return render_template('adapters.html')
            
            # Save adapter
            adapter_manager.save_adapter(name, config)
            
            flash(f'Adapter "{name}" updated successfully', 'success')
            return redirect(url_for('admin.manage_adapters'))
            
        except Exception as e:
            flash(f'Error updating adapter: {e}', 'error')
    
    # Load existing adapter
    config = adapter_manager.load_adapter(name)
    adapters = adapter_manager.list_adapters()
    
    return render_template('adapters.html', 
                         adapters=adapters, 
                         edit_adapter={'name': name, 'config': config})

@admin_bp.route('/adapter/<name>/delete', methods=['POST'])
def delete_adapter(name):
    """Delete adapter"""
    try:
        adapter_manager = AdapterManager()
        success = adapter_manager.delete_adapter(name)
        
        if success:
            flash(f'Adapter "{name}" deleted successfully', 'success')
        else:
            flash(f'Cannot delete adapter "{name}"', 'error')
    except Exception as e:
        flash(f'Error deleting adapter: {e}', 'error')
    
    return redirect(url_for('admin.manage_adapters'))

@admin_bp.route('/api/adapter/<name>')
def api_get_adapter(name):
    """Get adapter configuration via API"""
    adapter_manager = AdapterManager()
    config = adapter_manager.load_adapter(name)
    return jsonify({'name': name, 'config': config})
