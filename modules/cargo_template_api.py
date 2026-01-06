"""
Cargo Template API Endpoints

API endpoints for managing cargo templates with cost allocations.
These endpoints can be registered with the main Flask app.
"""

from flask import jsonify, request
import logging
from typing import Any, Dict
from modules.cargo_template_manager import CargoTemplateManager
from modules.rbac import Permission

logger = logging.getLogger(__name__)


def register_cargo_template_endpoints(app, require_auth=None):
    """
    Register cargo template API endpoints with the Flask app.
    
    Parameters: 
        app: Flask application instance
        require_auth: Authentication decorator function (optional)
    """
    
    # Initialize template manager
    template_manager = CargoTemplateManager()
    
    # Helper for auth (no-op if not provided)
    def _require_auth(permission=None):
        if require_auth:
            return require_auth(permission)
        def decorator(f):
            return f
        return decorator
    
    @dataclass
    class CargoTemplateSchema:
        """JSON schema for cargo templates."""
        name: str
        commodity: str
        description: str = ''
        quantity: Optional[float] = None
        loadPort: str = ''
        dischPort: str = ''
        freightRate: Optional[float] = None
        operationalCost: float = 0
        overheadCost: float = 0
        otherCost: float = 0
        isDefault: bool = False
        
        @staticmethod
        def validate(data: Dict[str, Any]) -> 'CargoTemplateSchema':
            """Validate and parse cargo template data."""
            name = data.get('name')
            if not name or not isinstance(name, str) or len(name) > 200:
                raise ValueError('Invalid name: must be non-empty string <= 200 chars')
            
            commodity = data.get('commodity')
            if not commodity or not isinstance(commodity, str) or len(commodity) > 100:
                raise ValueError('Invalid commodity: must be non-empty string <= 100 chars')
            
            description = data.get('description', '')
            if not isinstance(description, str) or len(description) > 1000:
                raise ValueError('Invalid description: must be string <= 1000 chars')
            
            quantity = data.get('quantity')
            if quantity is not None:
                try:
                    quantity = float(quantity)
                    if quantity < 0:
                        raise ValueError('Quantity cannot be negative')
                except (ValueError, TypeError):
                    raise ValueError('Invalid quantity: must be a number')
            
            freight_rate = data.get('freightRate')
            if freight_rate is not None:
                try:
                    freight_rate = float(freight_rate)
                    if freight_rate < 0:
                        raise ValueError('Freight rate cannot be negative')
                except (ValueError, TypeError):
                    raise ValueError('Invalid freight rate: must be a number')
            
            # Validate cost fields
            operational_cost = float(data.get('operationalCost', 0))
            overhead_cost = float(data.get('overheadCost', 0))
            other_cost = float(data.get('otherCost', 0))
            
            if operational_cost < 0 or overhead_cost < 0 or other_cost < 0:
                raise ValueError('Cost values cannot be negative')
            
            is_default = bool(data.get('isDefault', False))
            
            return CargoTemplateSchema(
                name=name,
                commodity=commodity,
                description=description,
                quantity=quantity,
                loadPort=data.get('loadPort', ''),
                dischPort=data.get('dischPort', ''),
                freightRate=freight_rate,
                operationalCost=operational_cost,
                overheadCost=overhead_cost,
                otherCost=other_cost,
                isDefault=is_default
            )
    
    # ======================
    # GET /api/cargo-templates
    # ======================
    @app.route('/api/cargo-templates', methods=['GET'])
    def get_cargo_templates():
        """
        Get all cargo templates.
        
        Returns:
            JSON with templates array
        """
        try:
            templates = template_manager.get_all()
            
            logger.info(f"Returning {len(templates)} cargo templates")
            return jsonify({
                'templates': templates,
                'total': len(templates)
            })
        
        except Exception as e:
            logger.exception(f"Error getting cargo templates: {e}")
            return jsonify({'error': str(e), 'templates': []}), 500
    
    # ======================
    # GET /api/cargo-templates/default
    # ======================
    @app.route('/api/cargo-templates/default', methods=['GET'])
    def get_default_cargo_template():
        """
        Get the default cargo template.
        
        Returns:
            JSON with default template or 404 if none set
        """
        try:
            template = template_manager.get_default()
            
            if not template:
                return jsonify({'error': 'No default template set'}), 404
            
            return jsonify({'template': template})
        
        except Exception as e:
            logger.exception(f"Error getting default template: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ======================
    # GET /api/cargo-templates/:id
    # ======================
    @app.route('/api/cargo-templates/<template_id>', methods=['GET'])
    def get_cargo_template(template_id: str):
        """
        Get a specific cargo template by ID.
        
        Parameters:
            template_id: Template ID
            
        Returns:
            JSON with template data or 404 if not found
        """
        try:
            template = template_manager.get_by_id(template_id)
            
            if not template:
                return jsonify({'error': f'Template {template_id} not found'}), 404
            
            return jsonify({'template': template})
        
        except Exception as e:
            logger.exception(f"Error getting template {template_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ======================
    # POST /api/cargo-templates
    # ======================
    @app.route('/api/cargo-templates', methods=['POST'])
    @_require_auth(Permission.CREATE_SCHEDULES if Permission else None)
    def create_cargo_template():
        """
        Create a new cargo template.
        
        Request Body:
            JSON with template data (name, commodity, costs, etc.)
            
        Returns:
            JSON with created template
        """
        try:
            if not request.json:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            # Validate schema
            schema = CargoTemplateSchema.validate(request.json)
            
            # Create template
            template = template_manager.create({
                'name': schema.name,
                'description': schema.description,
                'commodity': schema.commodity,
                'quantity': schema.quantity,
                'loadPort': schema.loadPort,
                'dischPort': schema.dischPort,
                'freightRate': schema.freightRate,
                'operationalCost': schema.operationalCost,
                'overheadCost': schema.overheadCost,
                'otherCost': schema.otherCost,
                'isDefault': schema.isDefault
            })
            
            logger.info(f"Created cargo template {template['id']}: {template['name']}")
            return jsonify({
                'success': True,
                'template': template,
                'message': 'Template created successfully'
            }), 201
        
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.exception(f"Error creating template: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ======================
    # PUT /api/cargo-templates/:id
    # ======================
    @app.route('/api/cargo-templates/<template_id>', methods=['PUT'])
    @_require_auth(Permission.EDIT_SCHEDULES if Permission else None)
    def update_cargo_template(template_id: str):
        """
        Update an existing cargo template.
        
        Parameters:
            template_id: Template ID to update
            
        Request Body:
            JSON with updated template data
            
        Returns:
            JSON with updated template or 404 if not found
        """
        try:
            if not request.json:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            # Validate schema
            schema = CargoTemplateSchema.validate(request.json)
            
            # Update template
            template = template_manager.update(template_id, {
                'name': schema.name,
                'description': schema.description,
                'commodity': schema.commodity,
                'quantity': schema.quantity,
                'loadPort': schema.loadPort,
                'dischPort': schema.dischPort,
                'freightRate': schema.freightRate,
                'operationalCost': schema.operationalCost,
                'overheadCost': schema.overheadCost,
                'otherCost': schema.otherCost,
                'isDefault': schema.isDefault
            })
            
            if not template:
                return jsonify({'error': f'Template {template_id} not found'}), 404
            
            logger.info(f"Updated cargo template {template_id}: {template['name']}")
            return jsonify({
                'success': True,
                'template': template,
                'message': 'Template updated successfully'
            })
        
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.exception(f"Error updating template {template_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ======================
    # DELETE /api/cargo-templates/:id
    # ======================
    @app.route('/api/cargo-templates/<template_id>', methods=['DELETE'])
    @_require_auth(Permission.DELETE_SCHEDULES if Permission else None)
    def delete_cargo_template(template_id: str):
        """
        Delete a cargo template.
        
        Parameters:
            template_id: Template ID to delete
            
        Returns:
            JSON with success message or 404 if not found
        """
        try:
            success = template_manager.delete(template_id)
            
            if not success:
                return jsonify({'error': f'Template {template_id} not found'}), 404
            
            logger.info(f"Deleted cargo template {template_id}")
            return jsonify({
                'success': True,
                'message': f'Template {template_id} deleted successfully'
            })
        
        except Exception as e:
            logger.exception(f"Error deleting template {template_id}:{e}")
            return jsonify({'error': str(e)}), 500
    
    # ======================
    # POST /api/cargo-templates/:id/apply
    # ======================
    @app.route('/api/cargo-templates/<template_id>/apply', methods=['POST'])
    def apply_cargo_template(template_id: str):
        """
        Apply a template to create cargo commitment data.
        
        Parameters:
            template_id: Template ID to apply
            
        Request Body (optional):
            JSON with cargo-specific overrides
            
        Returns:
            JSON with cargo data pre-filled from template
        """
        try:
            cargo_overrides = request.json if request.json else {}
            
            cargo_data = template_manager.apply_template(template_id, cargo_overrides)
            
            if not cargo_data:
                return jsonify({'error': f'Template {template_id} not found'}), 404
            
            logger.info(f"Applied template {template_id}")
            return jsonify({
                'success': True,
                'cargo': cargo_data,
                'message': 'Template applied successfully'
            })
        
        except Exception as e:
            logger.exception(f"Error applying template {template_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    logger.info("[OK] Cargo template API endpoints registered successfully")


# Import at module level for validation schema
from dataclasses import dataclass
from typing import Optional
