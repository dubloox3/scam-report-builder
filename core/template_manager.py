"""
Template Manager for Scam Report Builder
Manages scam report templates and field definitions.
"""

from typing import Dict, Any, List


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
                    "ips",
                    "locations",
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
    def get_template(template_key: str) -> Dict[str, Any]:
        """Get template definition by key"""
        return TemplateManager.TEMPLATES.get(template_key)
    
    @staticmethod
    def get_all_templates() -> Dict[str, Dict[str, Any]]:
        """Get all available templates"""
        return TemplateManager.TEMPLATES
    
    @staticmethod
    def get_template_names() -> List[str]:
        """Get list of template names"""
        return [template["name"] for template in TemplateManager.TEMPLATES.values()]
    
    @staticmethod
    def get_template_key_by_name(name: str) -> str:
        """Get template key by its display name"""
        for key, template in TemplateManager.TEMPLATES.items():
            if template["name"] == name:
                return key
        return ""