"""
Cargo Template Management Module

Handles CRUD operations for cargo templates with cost allocations.
Templates are stored in data/cargo_templates.json
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import logging
from modules.security_utils import SecurityUtils

logger = logging.getLogger(__name__)


class CargoTemplateManager:
    """Manages cargo templates with persistent storage."""
    
    def __init__(self, storage_path: str = 'data/cargo_templates.json'):
        """
        Initialize the cargo template manager.
        
        Parameters:
            storage_path: Path to the JSON storage file (relative to project root)
        """
        self.storage_path = Path(storage_path)
        self._ensure_storage_file()
    
    def _ensure_storage_file(self) -> None:
        """Ensure storage file and directory exist."""
        try:
            # Create directory if it doesn't exist
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Initialize file if it doesn't exist
            if not self.storage_path.exists():
                self._write_templates({})
                logger.info(f"Created cargo templates storage at {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to initialize storage file: {e}")
            raise
    
    def _read_templates(self) -> Dict[str, Any]:
        """Read all templates from storage."""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in templates file: {e}")
            return {}
        except FileNotFoundError:
            return {}
        except Exception as e:
            logger.error(f"Error reading templates: {e}")
            return {}
    
    def _write_templates(self, templates: Dict[str, Any]) -> None:
        """Write templates to storage."""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(templates, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to write templates: {e}")
            raise
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all cargo templates.
        
        Returns:
            List of template dictionaries
        """
        templates = self._read_templates()
        return list(templates.values())
    
    def get_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a template by ID.
        
        Parameters:
            template_id: Template ID
            
        Returns:
            Template dictionary or None if not found
        """
        templates = self._read_templates()
        return templates.get(template_id)
    
    def get_default(self) -> Optional[Dict[str, Any]]:
        """
        Get the default template (if any).
        
        Returns:
            Default template dictionary or None
        """
        templates = self._read_templates()
        for template in templates.values():
            if template.get('isDefault', False):
                return template
        return None
    
    def create(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new cargo template.
        
        Parameters:
            template_data: Template data
            
        Returns:
            Created template with generated ID and timestamps
        """
        templates = self._read_templates()
        
        # Generate unique ID
        template_id = f"tpl_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(templates)}"
        
        # Add metadata
        template = {
            'id': template_id,
            'name': template_data.get('name', 'Untitled Template'),
            'description': template_data.get('description', ''),
            'commodity': template_data.get('commodity', ''),
            'quantity': template_data.get('quantity'),
            'loadPort': template_data.get('loadPort', ''),
            'dischPort': template_data.get('dischPort', ''),
            'freightRate': template_data.get('freightRate'),
            'operationalCost': template_data.get('operationalCost', 0),
            'overheadCost': template_data.get('overheadCost', 0),
            'otherCost': template_data.get('otherCost', 0),
            'isDefault': template_data.get('isDefault', False),
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        # If this is set as default, clear other defaults
        if template['isDefault']:
            for tid, tmpl in templates.items():
                tmpl['isDefault'] = False
        
        # Store template
        templates[template_id] = template
        self._write_templates(templates)
        
        logger.info(f"Created template {template_id}: {template['name']}")
        return template
    
    def update(self, template_id: str, template_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing template.
        
        Parameters:
            template_id: Template ID to update
            template_data: Updated template data
            
        Returns:
            Updated template or None if not found
        """
        templates = self._read_templates()
        
        if template_id not in templates:
            logger.warning(f"Template {template_id} not found for update")
            return None
        
        # Update fields
        template = templates[template_id]
        template.update({
            'name': template_data.get('name', template['name']),
            'description': template_data.get('description', template.get('description', '')),
            'commodity': template_data.get('commodity', template['commodity']),
            'quantity': template_data.get('quantity', template.get('quantity')),
            'loadPort': template_data.get('loadPort', template.get('loadPort', '')),
            'dischPort': template_data.get('dischPort', template.get('dischPort', '')),
            'freightRate': template_data.get('freightRate', template.get('freightRate')),
            'operationalCost': template_data.get('operationalCost', template.get('operationalCost', 0)),
            'overheadCost': template_data.get('overheadCost', template.get('overheadCost', 0)),
            'otherCost': template_data.get('otherCost', template.get('otherCost', 0)),
            'isDefault': template_data.get('isDefault', template.get('isDefault', False)),
            'updatedAt': datetime.now().isoformat()
        })
        
        # If this is set as default, clear other defaults
        if template['isDefault']:
            for tid, tmpl in templates.items():
                if tid != template_id:
                    tmpl['isDefault'] = False
        
        templates[template_id] = template
        self._write_templates(templates)
        
        logger.info(f"Updated template {template_id}: {template['name']}")
        return template
    
    def delete(self, template_id: str) -> bool:
        """
        Delete a template.
        
        Parameters:
            template_id: Template ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        templates = self._read_templates()
        
        if template_id not in templates:
            logger.warning(f"Template {template_id} not found for deletion")
            return False
        
        del templates[template_id]
        self._write_templates(templates)
        
        logger.info(f"Deleted template {template_id}")
        return True
    
    def apply_template(self, template_id: str, cargo_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Apply a template to create cargo commitment data.
        
        Parameters:
            template_id: Template ID to apply
            cargo_data: Optional cargo-specific overrides
            
        Returns:
            Cargo commitment data with template values applied, or None if template not found
        """
        template = self.get_by_id(template_id)
        if not template:
            return None
        
        # Start with template values
        result = {
            'commodity': template.get('commodity', ''),
            'quantity': template.get('quantity', 0),
            'loadPort': template.get('loadPort', ''),
            'dischPort': template.get('dischPort', ''),
           'freightRate': template.get('freightRate'),
            'operationalCost': template.get('operationalCost', 0),
            'overheadCost': template.get('overheadCost', 0),
            'otherCost': template.get('otherCost', 0),
        }
        
        # Apply cargo-specific overrides
        if cargo_data:
            result.update(cargo_data)
        
        return result
