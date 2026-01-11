"""
Template Manager for Scam Report Builder
Manages scam report templates and field definitions.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import sys


class TemplateManager:
    """Manages report templates and field definitions"""
    
    TEMPLATES = {
        "advance-fee": {
            "name": "Advance-Fee Scam",
            "description": "Fee to be paid to receive an inheritance",
            "sections": {
                "Main Info:": [
                    "type",
                    "summary",
                    "alias",
                    "emails",
                "websites",
                "social_media",
                "ips",
                "locations",
                "other_info",
                "started"
                ],
                "Payment Information:": [
                    "amount",
                    "bank_info",
                    "other_payments"
                ],
                "Evidence:": [
                    "scammer_names",
                    "passport_ids",
                    "scammer_photos",
                    "victim_ids",
                    "others"
                ],
                "Remarks:": [
                    "remarks"
                ]
            },
            "fields": {
                "type": {
                    "type": "text",
                    "label": "Type of scam",
                    "default": "Advance-Fee Scam"
                },
                "summary": {
                    "type": "text",
                    "label": "Short summary",
                    "default": "Fee to be paid to receive an inheritance"
                },
                "alias": {
                    "type": "list",
                    "label": "Scammer Alias(es)",
                    "button": "+ Add alias",
                    "default": [""]
                },
                "emails": {
                    "type": "list",
                    "label": "Scammer Email(s)",
                    "button": "+ Add email",
                    "default": [""]
                },
                "websites": {
                    "type": "list",
                    "label": "Scammer Website(s)",
                    "button": "+ Add Scammer Website"
                },
                "social_media": {
                    "type": "list",
                    "label": "Scammer Social Media(s)",
                    "button": "+ Add other social media"
                },
                "ips": {
                    "type": "list",
                    "label": "IP(s)",
                    "button": "+ Add IP"
                },
                "locations": {
                    "type": "list",
                    "label": "Geolocation(s)",
                    "button": "+ Add geolocation"
                },
                "other_info": {
                    "type": "list",
                    "label": "Other info",
                    "button": "+ Add other info"
                },
                "started": {
                    "type": "date",
                    "label": "Started",
                    "format": "MM/DD/YY"
                },
                "bank_info": {
                    "type": "multiline",
                    "label": "Bank Information",
                    "placeholder": "Paste bank details from scammer email here..."
                },
                "other_payments": {
                    "type": "other_payments",
                    "label": "Other Payment Methods"
                },
                "amount": {
                    "type": "text",
                    "label": "Fee/Amount"
                },
                "scammer_names": {
                    "type": "list",
                    "label": "Scammers real name:",
                    "button": "+ Add name"
                },
                "passport_ids": {
                    "type": "image_list",
                    "label": "Scammer's Passport/ID",
                    "button": "+ Add Passport/ID"
                },
                "scammer_photos": {
                    "type": "image_list",
                    "label": "Photo of Scammer",
                    "button": "+ Add Photo"
                },
                "victim_ids": {
                    "type": "image_list",
                    "label": "Possible Victim / Money-Mule ID",
                    "button": "+ Add ID"
                },
                "others": {
                    "type": "images",
                    "label": "Others",
                    "button": "+ Add Image",
                    "placeholder": "Add other scam-related images/screenshots"
                },
                "remarks": {
                    "type": "list",
                    "label": "Remarks",
                    "button": "+ Add remark"
                }
            }
        }
    }
    
    @staticmethod
    def get_template(template_key: str) -> Optional[Dict[str, Any]]:
        """Get template definition by key (includes custom templates)"""
        # First check built-in templates
        if template_key in TemplateManager.TEMPLATES:
            return TemplateManager.TEMPLATES[template_key]
        
        # Then check custom templates
        custom_templates = TemplateManager.load_custom_templates()
        return custom_templates.get(template_key)
    
    @staticmethod
    def get_all_templates() -> Dict[str, Dict[str, Any]]:
        """Get all available templates"""
        return TemplateManager.TEMPLATES
    
    @staticmethod
    def get_template_names() -> List[str]:
        """Get list of template names"""
        all_templates = TemplateManager.get_all_templates()
        return [template["name"] for template in all_templates.values()]
    
    @staticmethod
    def get_template_key_by_name(name: str) -> str:
        """Get template key by its display name"""
        all_templates = TemplateManager.get_all_templates()
        for key, template in all_templates.items():
            if template["name"] == name:
                return key
        return ""
    
    # Available field definitions for custom templates
    AVAILABLE_FIELDS = {
        "type": {
            "type": "text",
            "label": "Type of scam",
            "category": "Main Info"
        },
        "summary": {
            "type": "text",
            "label": "Short summary",
            "category": "Main Info"
        },
        "alias": {
            "type": "list",
            "label": "Scammer Alias(es)",
            "button": "+ Add alias",
            "category": "Main Info"
        },
        "emails": {
            "type": "list",
            "label": "Scammer Email(s)",
            "button": "+ Add email",
            "category": "Main Info"
        },
        "websites": {
            "type": "list",
            "label": "Scammer Website(s)",
            "button": "+ Add Scammer Website",
            "category": "Main Info"
        },
        "social_media": {
            "type": "list",
            "label": "Scammer Social Media(s)",
            "button": "+ Add other social media",
            "category": "Main Info"
        },
        "ips": {
            "type": "list",
            "label": "IP(s)",
            "button": "+ Add IP",
            "category": "Main Info"
        },
        "locations": {
            "type": "list",
            "label": "Geolocation(s)",
            "button": "+ Add geolocation",
            "category": "Main Info"
        },
        "other_info": {
            "type": "list",
            "label": "Other info",
            "button": "+ Add other info",
            "category": "Main Info"
        },
        "started": {
            "type": "date",
            "label": "Started",
            "format": "MM/DD/YY",
            "category": "Main Info"
        },
        "amount": {
            "type": "text",
            "label": "Fee/Amount",
            "category": "Payment Information"
        },
        "bank_info": {
            "type": "multiline",
            "label": "Bank Information",
            "placeholder": "Paste bank details from scammer email here...",
            "category": "Payment Information"
        },
        "other_payments": {
            "type": "other_payments",
            "label": "Other Payment Methods",
            "category": "Payment Information"
        },
        "scammer_names": {
            "type": "list",
            "label": "Scammers real name:",
            "button": "+ Add name",
            "category": "Evidence"
        },
        "passport_ids": {
            "type": "image_list",
            "label": "Scammer's Passport/ID",
            "button": "+ Add Passport/ID",
            "category": "Evidence"
        },
        "scammer_photos": {
            "type": "image_list",
            "label": "Photo of Scammer",
            "button": "+ Add Photo",
            "category": "Evidence"
        },
        "victim_ids": {
            "type": "image_list",
            "label": "Possible Victim / Money-Mule ID",
            "button": "+ Add ID",
            "category": "Evidence"
        },
        "others": {
            "type": "images",
            "label": "Others",
            "button": "+ Add Image",
            "placeholder": "Add other scam-related images/screenshots",
            "category": "Evidence"
        },
        "remarks": {
            "type": "list",
            "label": "Remarks",
            "button": "+ Add remark",
            "category": "Remarks"
        }
    }
    
    @staticmethod
    def _get_custom_templates_folder() -> Path:
        """Get the custom templates folder path"""
        if getattr(sys, 'frozen', False):
            # Running as EXE
            app_root = Path(sys.executable).parent
        else:
            # Running as script
            app_root = Path(__file__).parent.parent
        
        custom_folder = app_root / "templates" / "custom"
        custom_folder.mkdir(parents=True, exist_ok=True)
        return custom_folder
    
    @staticmethod
    def load_custom_templates() -> Dict[str, Dict[str, Any]]:
        """Load all custom templates from templates/custom/ folder"""
        custom_templates = {}
        custom_folder = TemplateManager._get_custom_templates_folder()
        
        if not custom_folder.exists():
            return custom_templates
        
        for json_file in custom_folder.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    
                # Validate template structure
                if TemplateManager._validate_template(template_data):
                    # Use filename (without extension) as key
                    template_key = f"custom-{json_file.stem}"
                    custom_templates[template_key] = template_data
            except Exception:
                # Skip invalid templates
                continue
        
        return custom_templates
    
    @staticmethod
    def _validate_template(template_data: Dict[str, Any]) -> bool:
        """Validate template structure"""
        required_fields = ['name', 'description', 'fields']
        if not all(field in template_data for field in required_fields):
            return False
        
        # Validate fields structure
        if not isinstance(template_data['fields'], dict):
            return False
        
        # Each field must have at least 'type' and 'label'
        for field_key, field_def in template_data['fields'].items():
            if not isinstance(field_def, dict):
                return False
            if 'type' not in field_def or 'label' not in field_def:
                return False
        
        return True
    
    @staticmethod
    def save_custom_template(name: str, description: str, fields: Dict[str, Dict[str, Any]], 
                             sections: Optional[Dict[str, List[str]]] = None) -> str:
        """Save a custom template to templates/custom/ folder
        
        Args:
            name: Template name
            description: Template description
            fields: Dictionary of field definitions
            sections: Optional sections organization (if None, auto-generate)
            
        Returns:
            Template key (filename without extension)
        """
        # Generate safe filename from template name
        safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in name)
        safe_name = safe_name.lower()[:50]  # Limit length
        
        # Ensure unique filename
        custom_folder = TemplateManager._get_custom_templates_folder()
        counter = 1
        filename = safe_name
        while (custom_folder / f"{filename}.json").exists():
            filename = f"{safe_name}_{counter}"
            counter += 1
        
        # Auto-generate sections if not provided
        if sections is None:
            sections = TemplateManager._generate_sections_from_fields(fields)
        
        # Build template structure
        template_data = {
            "name": name,
            "description": description,
            "category": "custom",
            "sections": sections,
            "fields": fields,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "version": "1.0"
        }
        
        # Save to file
        template_path = custom_folder / f"{filename}.json"
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    @staticmethod
    def _generate_sections_from_fields(fields: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate sections organization from fields based on category"""
        sections = {
            "Main Info:": [],
            "Payment Information:": [],
            "Evidence:": [],
            "Remarks:": []
        }
        
        # Special handling for filename_name - always goes after summary in Main Info
        main_info_ordered = []
        filename_name_field = None
        
        for field_key, field_def in fields.items():
            category = field_def.get('category', 'Main Info')
            
            # Skip always-included fields (handled separately)
            if field_key in ['type', 'summary', 'filename_name', 'remarks']:
                if field_key == 'filename_name':
                    filename_name_field = field_key
                continue  # Will add them separately in correct order
            
            if category == "Main Info":
                main_info_ordered.append(field_key)
            elif category == "Payment Information":
                sections["Payment Information:"].append(field_key)
            elif category == "Evidence":
                sections["Evidence:"].append(field_key)
            elif category == "Remarks":
                # Skip remarks - it's handled separately
                pass
            else:
                main_info_ordered.append(field_key)  # Default
        
        # Add fields to Main Info section in order: type, summary, filename_name (if exists), then others
        if 'type' in fields:
            sections["Main Info:"].append('type')
        if 'summary' in fields:
            sections["Main Info:"].append('summary')
        if filename_name_field:
            sections["Main Info:"].append(filename_name_field)
        # Add other main info fields
        for field_key in main_info_ordered:
            if field_key not in ['type', 'summary']:
                sections["Main Info:"].append(field_key)
        
        if 'remarks' in fields:
            sections["Remarks:"].append('remarks')
        
        # Remove empty sections
        sections = {k: v for k, v in sections.items() if v}
        
        return sections
    
    @staticmethod
    def delete_custom_template(template_key: str) -> bool:
        """Delete a custom template by key"""
        if not template_key.startswith("custom-"):
            return False
        
        filename = template_key.replace("custom-", "")
        custom_folder = TemplateManager._get_custom_templates_folder()
        template_path = custom_folder / f"{filename}.json"
        
        if template_path.exists():
            try:
                template_path.unlink()
                return True
            except Exception:
                return False
        
        return False
    
    @staticmethod
    def get_all_templates() -> Dict[str, Dict[str, Any]]:
        """Get all available templates (built-in + custom)"""
        all_templates = TemplateManager.TEMPLATES.copy()
        custom_templates = TemplateManager.load_custom_templates()
        all_templates.update(custom_templates)
        return all_templates
    
    @staticmethod
    def get_template(template_key: str) -> Optional[Dict[str, Any]]:
        """Get template definition by key (includes custom templates)"""
        # First check built-in templates
        if template_key in TemplateManager.TEMPLATES:
            return TemplateManager.TEMPLATES[template_key]
        
        # Then check custom templates
        custom_templates = TemplateManager.load_custom_templates()
        return custom_templates.get(template_key)
    
    @staticmethod
    def get_template_names() -> List[str]:
        """Get list of template names"""
        all_templates = TemplateManager.get_all_templates()
        return [template["name"] for template in all_templates.values()]
    
    @staticmethod
    def get_available_fields() -> Dict[str, Dict[str, Any]]:
        """Get all available field definitions for custom templates"""
        return TemplateManager.AVAILABLE_FIELDS.copy()