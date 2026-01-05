"""
ODT Generator for Scam Report Builder
Generates ODT documents from report data with embedded images.
"""

import zipfile
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from io import BytesIO
from PIL import Image


class ODTGenerator:
    """Generate ODT documents with embedded images"""
    
    @staticmethod
    def create_odt(content: Dict[str, Any], output_path: str, 
                   images: Dict[str, List[Tuple[str, Optional[bytes]]]]) -> bool:
        """
        Generate an ODT document with embedded images.
        
        Args:
            content: Dictionary containing report data
            output_path: Path to save the ODT file
            images: Dictionary mapping categories to lists of (name, data) tuples
        
        Returns:
            bool: True if generation was successful
        """
        print(f"Generating ODT document: {output_path}")
        
        # Create temporary directory for ODT components
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create ODT structure
            try:
                # 1. Create required directories
                (temp_path / 'Pictures').mkdir(exist_ok=True)
                (temp_path / 'META-INF').mkdir(exist_ok=True)
                
                # 2. Process images
                image_entries = ODTGenerator._process_images(images, temp_path)
                
                # 3. Create ODT files
                ODTGenerator._create_mimetype(temp_path)
                ODTGenerator._create_manifest(temp_path, image_entries)
                ODTGenerator._create_content_xml(content, image_entries, temp_path)
                ODTGenerator._create_styles_xml(temp_path)
                ODTGenerator._create_meta_xml(temp_path)
                
                # 4. Create final ODT (ZIP file)
                ODTGenerator._create_odt_zip(temp_path, output_path, image_entries)
                
                print(f"✓ ODT generation completed")
                return True
                
            except Exception as e:
                print(f"✗ Error during ODT generation: {e}")
                return False
    
    @staticmethod
    def _process_images(images: Dict[str, List[Tuple[str, Optional[bytes]]]], 
                       temp_path: Path) -> List[Dict[str, Any]]:
        """Process all images and save them to temp directory"""
        image_entries = []
        image_counter = 1
        
        for category, img_list in images.items():
            for img_name, img_data in img_list:
                if img_data:  # Skip None/empty image data
                    # Generate filename
                    img_filename = f"image_{image_counter}.jpg"
                    img_path = temp_path / 'Pictures' / img_filename
                    
                    # Save image
                    with open(img_path, 'wb') as f:
                        f.write(img_data)
                    
                    # Get image dimensions for ODT
                    try:
                        with Image.open(BytesIO(img_data)) as img:
                            width_px, height_px = img.size
                            # Convert to inches (96 DPI typical)
                            width_in = width_px / 96
                            height_in = height_px / 96
                            
                            # Limit width to 6 inches max
                            if width_in > 6:
                                scale_factor = 6 / width_in
                                width_in = 6
                                height_in = height_in * scale_factor
                            
                            odt_width = f"{width_in:.2f}in"
                            odt_height = f"{height_in:.2f}in"
                    except Exception:
                        odt_width = "4in"
                        odt_height = "3in"
                    
                    # Create entry
                    entry = {
                        'filename': img_filename,
                        'category': category,
                        'name': img_name,
                        'width': odt_width,
                        'height': odt_height,
                        'index': image_counter
                    }
                    image_entries.append(entry)
                    
                    image_counter += 1
        
        return image_entries
    
    @staticmethod
    def _create_mimetype(temp_path: Path):
        """Create mimetype file (must be first in ODT)"""
        mimetype_path = temp_path / 'mimetype'
        with open(mimetype_path, 'w') as f:
            f.write('application/vnd.oasis.opendocument.text')
    
    @staticmethod
    def _create_manifest(temp_path: Path, image_entries: List[Dict[str, Any]]):
        """Create manifest.xml with file entries"""
        manifest_path = temp_path / 'META-INF' / 'manifest.xml'
        
        manifest = '''<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
  <manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/>
  <manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>
  <manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/>
  <manifest:file-entry manifest:full-path="meta.xml" manifest:media-type="text/xml"/>'''
        
        # Add image entries
        for entry in image_entries:
            manifest += f'\n  <manifest:file-entry manifest:full-path="Pictures/{entry["filename"]}" manifest:media-type="image/jpeg"/>'
        
        manifest += '\n</manifest:manifest>'
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(manifest)
    
    @staticmethod
    def _create_content_xml(content: Dict[str, Any], image_entries: List[Dict[str, Any]], 
                           temp_path: Path):
        """Create content.xml with report data and image references"""
        content_path = temp_path / 'content.xml'
        
        # Start XML document with Liberation Serif font
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
  xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
  xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
  office:version="1.3">
  
  <office:scripts/>
  <office:font-face-decls>
    <style:font-face style:name="Liberation Serif" svg:font-family="&apos;Liberation Serif&apos;" style:font-family-generic="roman" style:font-pitch="variable"/>
  </office:font-face-decls>
  
  <office:automatic-styles>'''
        
        # Add styles for images
        for entry in image_entries:
            xml += f'''
    <style:style style:name="fr{entry['index']}" style:family="graphic">
      <style:graphic-properties style:horizontal-pos="center" style:horizontal-rel="paragraph"/>
    </style:style>'''
        
        # Add text styles for formatting
        xml += '''
    <style:style style:name="T1" style:family="text">
      <style:text-properties fo:font-size="12pt" fo:font-family="Liberation Serif" style:font-name="Liberation Serif"/>
    </style:style>
    <style:style style:name="T1BoldUnderline" style:family="text">
      <style:text-properties fo:font-size="12pt" fo:font-family="Liberation Serif" style:font-name="Liberation Serif" fo:font-weight="bold" style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"/>
    </style:style>
    <style:style style:name="T1Underline" style:family="text">
      <style:text-properties fo:font-size="12pt" fo:font-family="Liberation Serif" style:font-name="Liberation Serif" style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"/>
    </style:style>
    <style:style style:name="T1Bold" style:family="text">
      <style:text-properties fo:font-size="12pt" fo:font-family="Liberation Serif" style:font-name="Liberation Serif" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="P1" style:family="paragraph">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0.1in"/>
      <style:text-properties fo:font-size="12pt" fo:font-family="Liberation Serif" style:font-name="Liberation Serif"/>
    </style:style>
    <style:style style:name="P1BoldUnderline" style:family="paragraph">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0.1in"/>
      <style:text-properties fo:font-size="12pt" fo:font-family="Liberation Serif" style:font-name="Liberation Serif" fo:font-weight="bold" style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"/>
    </style:style>
    <style:style style:name="ListBullet" style:family="paragraph">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in" fo:margin-left="0.2in" fo:text-indent="0in" style:auto-text-indent="false"/>
      <style:text-properties fo:font-size="12pt" fo:font-family="Liberation Serif" style:font-name="Liberation Serif"/>
    </style:style>
    <style:style style:name="PageBreak" style:family="paragraph">
      <style:paragraph-properties fo:break-before="page"/>
      <style:text-properties fo:font-size="12pt" fo:font-family="Liberation Serif" style:font-name="Liberation Serif"/>
    </style:style>
  </office:automatic-styles>
  
  <office:body>
    <office:text>
      <text:sequence-decls>
        <text:sequence-decl text:display-outline-level="0" text:name="Illustration"/>
      </text:sequence-decls>'''
        
        # Main title: "Report for [type] scammer '[alias]'" - bold, underlined
        scam_type = content.get('type', 'Unknown Type')
        # Remove "(419)" from "Advance-Fee Scam (419)" if present
        if scam_type == "Advance-Fee Scam (419)":
            scam_type = "Advance-Fee Scam"
        
        xml += f'''
      <text:p text:style-name="P1BoldUnderline">Report for {scam_type} scammer "{ODTGenerator._get_main_alias(content)}"</text:p>
      <text:p text:style-name="P1">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</text:p>
      <text:p text:style-name="P1"/>'''
        
        # Add report sections
        xml = ODTGenerator._add_report_sections(xml, content)
        
        # Add images and evidence section
        xml = ODTGenerator._add_images_to_xml(xml, image_entries, content)
        
        # Close XML
        xml += '''
    </office:text>
  </office:body>
</office:document-content>'''
        
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(xml)
    
    @staticmethod
    def _get_main_alias(content: Dict[str, Any]) -> str:
        """Extract the main alias from content"""
        if content.get('alias'):
            if isinstance(content['alias'], list) and len(content['alias']) > 0:
                return content['alias'][0]
            else:
                return str(content['alias'])
        return "Unknown"
    
    @staticmethod
    def _add_report_sections(xml: str, content: Dict[str, Any]) -> str:
        """Add report sections to XML"""
        
        # Type of scam
        scam_type = content.get('type', '')
        # Remove "(419)" from "Advance-Fee Scam (419)" if present
        if scam_type == "Advance-Fee Scam (419)":
            scam_type = "Advance-Fee Scam"
        
        if scam_type:
            xml += f'''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">Type of scam:</text:span> {scam_type}</text:p>'''
        
        # Short summary
        if content.get('summary'):
            xml += f'''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">Short summary:</text:span> {content["summary"]}</text:p>'''
        
        xml += '''
      <text:p text:style-name="P1"/>'''
        
        # Contact information
        
        # Scammer's aliases
        if content.get('alias'):
            aliases = content['alias']
            if isinstance(aliases, list):
                display_aliases = ", ".join(aliases)
            else:
                display_aliases = str(aliases)
            xml += f'''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">Scammers aliase(s):</text:span> {display_aliases}</text:p>'''
        
        # Emails
        if content.get('emails'):
            emails = content['emails']
            if isinstance(emails, list):
                display_emails = ", ".join(emails)
            else:
                display_emails = str(emails)
            xml += f'''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">Email(s):</text:span> {display_emails}</text:p>'''
        
        # Websites
        if content.get('websites'):
            websites = content['websites']
            if isinstance(websites, list):
                display_websites = ", ".join(websites)
            else:
                display_websites = str(websites)
            xml += f'''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">Website(s):</text:span> {display_websites}</text:p>'''
        
        # IPs
        if content.get('ips'):
            ips = content['ips']
            if isinstance(ips, list):
                display_ips = ", ".join(ips)
            else:
                display_ips = str(ips)
            xml += f'''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">IPs:</text:span> {display_ips}</text:p>'''
        
        # Locations
        if content.get('locations'):
            locations = content['locations']
            if isinstance(locations, list):
                display_locations = " / ".join(locations)
            else:
                display_locations = str(locations)
            xml += f'''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">Geo location(s):</text:span> {display_locations}</text:p>'''
        
        if content.get('started'):
            xml += f'''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">Started:</text:span> {content["started"]}</text:p>'''
        
        xml += '''
      <text:p text:style-name="P1"/>'''
        
        # BANK ACCOUNTS
        bank_accounts = content.get('bank_info', [])
        if bank_accounts:
            xml += '''
      <text:p text:style-name="P1BoldUnderline">BANK ACCOUNTS</text:p>'''
            
            if isinstance(bank_accounts, str):
                xml += '''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">Bank Account 1:</text:span></text:p>'''
                lines = bank_accounts.split('\n')
                for line in lines:
                    if line.strip():
                        xml += f'''
      <text:p text:style-name="P1">{line.strip()}</text:p>'''
                xml += '''
      <text:p text:style-name="P1"/>'''
                
            elif isinstance(bank_accounts, list):
                for i, bank_account in enumerate(bank_accounts, 1):
                    xml += f'''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">Bank Account {i}:</text:span></text:p>'''
                    
                    if isinstance(bank_account, str):
                        lines = bank_account.split('\n')
                        for line in lines:
                            if line.strip():
                                xml += f'''
      <text:p text:style-name="P1">{line.strip()}</text:p>'''
                    else:
                        xml += f'''
      <text:p text:style-name="P1">{bank_account}</text:p>'''
                    
                    xml += '''
      <text:p text:style-name="P1"/>'''
            
            xml += '''
      <text:p text:style-name="P1"/>'''
        
        # Other Payment Methods
        if content.get('other_payments'):
            xml += '''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">Other payment methods:</text:span></text:p>'''
            
            if isinstance(content['other_payments'], list):
                for payment in content['other_payments']:
                    if isinstance(payment, dict):
                        payment_type = payment.get('type', 'Unknown')
                        payment_details = payment.get('details', 'N/A')
                        
                        xml += f'''
      <text:p text:style-name="ListBullet">- <text:span text:style-name="T1Underline">{payment_type}:</text:span></text:p>'''
                        
                        if '\n' in payment_details:
                            lines = payment_details.split('\n')
                            for line in lines:
                                if line.strip():
                                    xml += f'''
      <text:p text:style-name="P1">{line.strip()}</text:p>'''
                        else:
                            xml += f'''
      <text:p text:style-name="P1">{payment_details}</text:p>'''
                    else:
                        payment_str = str(payment)
                        xml += f'''
      <text:p text:style-name="ListBullet">- {payment_str}</text:p>'''
            
            xml += '''
      <text:p text:style-name="P1"/>'''
        
        # Fee/Amount section - CHANGED from "Amount:" to "Fee/Amount:"
        if content.get('amount'):
            xml += f'''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">Fee/Amount:</text:span> {content["amount"]}</text:p>
      <text:p text:style-name="P1"/>
      <text:p text:style-name="P1"/>'''
        
        # Remarks section
        if content.get('remarks'):
            xml += '''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">Remarks:</text:span></text:p>'''
            if isinstance(content['remarks'], list):
                for remark in content['remarks']:
                    xml += f'''
      <text:p text:style-name="ListBullet">- {remark}</text:p>'''
            else:
                xml += f'''
      <text:p text:style-name="ListBullet">- {content["remarks"]}</text:p>'''
            xml += '''
      <text:p text:style-name="P1"/>'''
        
        return xml
    
    @staticmethod
    def _add_images_to_xml(xml: str, image_entries: List[Dict[str, Any]], content: Dict[str, Any]) -> str:
        """Add image references to XML with descriptive captions"""
        # Check if we should show the "Evidence" section
        scammer_names = content.get('scammer_names', [])
        has_scammer_names = scammer_names and isinstance(scammer_names, list) and len(scammer_names) > 0
        has_scammer_real_name = bool(content.get('scammer_real_name'))
        has_images = len(image_entries) > 0
        
        should_show_evidence = has_scammer_names or has_scammer_real_name or has_images
        
        if not should_show_evidence:
            return xml  # Don't add the section at all
        
        # Add page break before "Evidence" section only if it has content
        xml += '''
      <text:p text:style-name="PageBreak"/>'''
        
        # Add "Evidence" section header
        xml += '''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">Evidence:</text:span></text:p>'''
        
        # Scammer's real name - FIXED: Only show if a name was actually entered
        real_name = None
        
        # First priority: scammer_names list (first entry)
        if has_scammer_names:
            real_name = scammer_names[0]
            # Check if the name is not empty and not placeholder text
            if real_name and real_name.strip() and real_name.strip() != "(to be collected)":
                xml += f'''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">Scammers real name:</text:span> {real_name}</text:p>'''
        
        # Second priority: legacy scammer_real_name field
        elif has_scammer_real_name:
            real_name = content.get('scammer_real_name')
            # Check if the name is not empty and not placeholder text
            if real_name and real_name.strip() and real_name.strip() != "(to be collected)":
                xml += f'''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">Scammers real name:</text:span> {real_name}</text:p>'''
        
        # Add images if any
        if has_images:
            category_labels = {
                'passport_ids': "Scammers passport/ID:",
                'scammer_photos': "Photo of scammer (video available):",
                'victim_ids': "Possible Victim / Money-Mule ID:",
                'others': "Others:"
            }
            
            # Group images by category for page-break logic
            images_by_category = {}
            for entry in image_entries:
                category = entry['category']
                if category not in images_by_category:
                    images_by_category[category] = []
                images_by_category[category].append(entry)
            
            # Define the order of categories (others should be last)
            category_order = ['passport_ids', 'scammer_photos', 'victim_ids', 'others']
            
            # Filter to only include categories that exist in our images
            existing_categories = [cat for cat in category_order if cat in images_by_category]
            
            # Add images with page-breaks between categories
            for i, category in enumerate(existing_categories):
                category_images = images_by_category[category]
                
                # Add page-break before each image category (except the first one)
                if i > 0:
                    xml += '''
      <text:p text:style-name="PageBreak"/>'''
                
                category_label = category_labels.get(category, 
                                                   category.replace('_', ' ').title() + ":")
                xml += f'''
      <text:p text:style-name="P1"><text:span text:style-name="T1Underline">{category_label}</text:span></text:p>'''
                
                for entry in category_images:
                    xml += f'''
      <text:p text:style-name="P1">
        <draw:frame draw:style-name="fr{entry['index']}" draw:name="Image{entry['index']}" 
          text:anchor-type="as-char" svg:width="{entry['width']}" svg:height="{entry['height']}" draw:z-index="0">
          <draw:image xlink:href="Pictures/{entry['filename']}" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>
          <svg:desc>{entry['name']}</svg:desc>
        </draw:frame>
      </text:p>'''
        
        # Final spacing after evidence section
        xml += '''
      <text:p text:style-name="P1"/>'''
            
        return xml
    
    @staticmethod
    def _create_styles_xml(temp_path: Path):
        """Create styles.xml"""
        styles_path = temp_path / 'styles.xml'
        
        styles = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  office:version="1.3">
  
  <office:styles>
    <style:style style:name="Standard" style:family="paragraph">
      <style:text-properties fo:font-size="12pt" fo:font-family="Liberation Serif"/>
    </style:style>
    <style:style style:name="Graphics" style:family="graphic">
      <style:graphic-properties text:anchor-type="paragraph" 
        style:horizontal-pos="center" style:horizontal-rel="paragraph"/>
    </style:style>
  </office:styles>
</office:document-styles>'''
        
        with open(styles_path, 'w', encoding='utf-8') as f:
            f.write(styles)
    
    @staticmethod
    def _create_meta_xml(temp_path: Path):
        """Create meta.xml"""
        meta_path = temp_path / 'meta.xml'
        
        meta = f'''<?xml version="1.0" encoding="UTF-8"?>
<office:document-meta xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  office:version="1.3">
  
  <office:meta>
    <meta:generator>Scam Report Builder</meta:generator>
    <dc:creator>Scam Report Builder</dc:creator>
    <dc:date>{datetime.now().isoformat()}</dc:date>
    <meta:creation-date>{datetime.now().isoformat()}</meta:creation-date>
  </office:meta>
</office:document-meta>'''
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            f.write(meta)
    
    @staticmethod
    def _create_odt_zip(temp_path: Path, output_path: str, image_entries: List[Dict[str, Any]]):
        """Create the final ODT ZIP file"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as odt_zip:
            # mimetype must be first and uncompressed (ODF specification)
            mimetype_path = temp_path / 'mimetype'
            odt_zip.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)
            
            # Add XML files
            for xml_file in ['content.xml', 'styles.xml', 'meta.xml']:
                xml_path = temp_path / xml_file
                if xml_path.exists():
                    odt_zip.write(xml_path, xml_file)
            
            # Add manifest
            manifest_path = temp_path / 'META-INF' / 'manifest.xml'
            if manifest_path.exists():
                odt_zip.write(manifest_path, 'META-INF/manifest.xml')
            
            # Add images
            for entry in image_entries:
                img_path = temp_path / 'Pictures' / entry['filename']
                if img_path.exists():
                    odt_zip.write(img_path, f'Pictures/{entry["filename"]}')