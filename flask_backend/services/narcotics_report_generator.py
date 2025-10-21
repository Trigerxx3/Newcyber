"""
Narcotics Intelligence Platform Investigation Report Generator
Generates reports in the exact format shown in the screenshot
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, Frame, PageTemplate
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os
from io import BytesIO
from typing import Dict, List, Optional, Any

from extensions import db
from models.case import Case
from models.content import Content
from models.osint_result import OSINTResult
from models.user import User
from models.user_case_link import UserCaseLink
from models.source import Source
from models.case_content_link import CaseContentLink

class NarcoticsReportGenerator:
    """Generate Narcotics Intelligence Platform Investigation Reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles to match the screenshot format"""
        # Main title - "Narcotics Intelligence Platform"
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Title'],
            fontSize=20,
            textColor=colors.HexColor('#1e3a8a'),  # Dark blue
            spaceAfter=8,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle - "Investigation Report"
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Title'],
            fontSize=16,
            textColor=colors.HexColor('#1e3a8a'),  # Dark blue
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section headers with blue background box
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=colors.white,
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#3b82f6'),  # Light blue background
            borderColor=colors.HexColor('#1e3a8a'),  # Dark blue border
            borderWidth=1,
            borderPadding=8,
            alignment=TA_LEFT
        ))
        
        # Red sub-headers
        self.styles.add(ParagraphStyle(
            name='RedSubHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#dc2626'),  # Red
            spaceAfter=6,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        ))
        
        # Case info
        self.styles.add(ParagraphStyle(
            name='CaseInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            spaceAfter=4
        ))
        
        # Footer text
        self.styles.add(ParagraphStyle(
            name='FooterText',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=4,
            alignment=TA_CENTER
        ))
    
    def generate_case_report(self, case, activities=None, content_items=None, output_path=None):
        """
        Generate a Narcotics Intelligence Platform Investigation Report
        
        Args:
            case: Case object
            activities: List of CaseActivity objects to include
            content_items: List of related Content objects
            output_path: Path to save the PDF (if None, returns BytesIO)
        
        Returns:
            File path or BytesIO object
        """
        # Create document
        if output_path:
            pdf = SimpleDocTemplate(output_path, pagesize=A4)
        else:
            buffer = BytesIO()
            pdf = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Container for elements
        elements = []
        
        # Add header
        elements.extend(self._create_header())
        
        # Add case overview
        elements.extend(self._create_case_overview(case))
        
        # Add description
        elements.extend(self._create_description(case))
        
        # Add investigation summary (first occurrence)
        elements.extend(self._create_investigation_summary_first(case, content_items))
        
        # Add flagged content analysis
        elements.extend(self._create_flagged_content_analysis(content_items))
        
        # Page break
        elements.append(PageBreak())
        
        # Add OSINT investigation results
        elements.extend(self._create_osint_results(case))
        
        # Add investigation summary (second occurrence)
        elements.extend(self._create_investigation_summary_second(case, content_items))
        
        # Add next steps
        elements.extend(self._create_next_steps())
        
        # Add footer
        elements.extend(self._create_footer())
        
        # Build PDF
        pdf.build(elements)
        
        if output_path:
            return output_path
        else:
            buffer.seek(0)
            return buffer
    
    def _create_header(self):
        """Create report header"""
        elements = []
        
        # Main title
        elements.append(Paragraph("Narcotics Intelligence Platform", self.styles['MainTitle']))
        
        # Subtitle
        elements.append(Paragraph("Investigation Report", self.styles['SubTitle']))
        
        # Horizontal line
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("_" * 80, self.styles['Normal']))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_case_overview(self, case):
        """Create case overview section"""
        elements = []
        
        # Section header
        elements.append(Paragraph("Case Overview", self.styles['SectionHeader']))
        elements.append(Spacer(1, 8))
        
        # Case information table
        case_data = [
            ['Case ID', str(case.id)],
            ['Case Name', case.title or 'N/A'],
            ['Case Number', case.case_number or 'N/A'],
            ['Status', case.status or 'N/A'],
            ['Priority', case.priority or 'N/A'],
            ['Type', case.type or 'N/A'],
            ['Created Date', case.created_at.strftime('%Y-%m-%d %H:%M:%S') if case.created_at else 'N/A'],
            ['Last Updated', case.updated_at.strftime('%Y-%m-%d %H:%M:%S') if case.updated_at else 'N/A'],
            ['Risk Level', 'Low']  # Default risk level
        ]
        
        table = Table(case_data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),  # Light grey for labels
            ('BACKGROUND', (1, 0), (1, -1), colors.white),  # White for values
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BORDER', (0, 0), (-1, -1), 1),
            ('BORDERCOLOR', (0, 0), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_description(self, case):
        """Create description section"""
        elements = []
        
        # Red sub-header
        elements.append(Paragraph("Description", self.styles['RedSubHeader']))
        
        # Description content
        description = case.description or "No description provided"
        elements.append(Paragraph(description, self.styles['CaseInfo']))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_investigation_summary_first(self, case, content_items):
        """Create first investigation summary section"""
        elements = []
        
        # Red sub-header
        elements.append(Paragraph("Investigation Summary", self.styles['RedSubHeader']))
        
        # Summary table
        flagged_users = len(content_items) if content_items else 0
        flagged_posts = len(content_items) if content_items else 0
        osint_results = 0  # Will be calculated from OSINT results
        
        summary_data = [
            ['Platforms Analyzed', 'None'],
            ['Flagged Users', str(flagged_users)],
            ['Flagged Posts', str(flagged_posts)],
            ['OSINT Results', str(osint_results)]
        ]
        
        table = Table(summary_data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),  # Light grey for labels
            ('BACKGROUND', (1, 0), (1, -1), colors.white),  # White for values
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BORDER', (0, 0), (-1, -1), 1),
            ('BORDERCOLOR', (0, 0), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_flagged_content_analysis(self, content_items):
        """Create flagged content analysis section"""
        elements = []
        
        # Section header
        elements.append(Paragraph("Flagged Content Analysis", self.styles['SectionHeader']))
        elements.append(Spacer(1, 8))
        
        if content_items and len(content_items) > 0:
            # Add content items details
            for item in content_items:
                elements.append(Paragraph(f"• {item.content[:100]}...", self.styles['CaseInfo']))
        else:
            elements.append(Paragraph("No flagged content found for this case.", self.styles['CaseInfo']))
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_osint_results(self, case):
        """Create OSINT investigation results section"""
        elements = []
        
        # Section header
        elements.append(Paragraph("OSINT Investigation Results", self.styles['SectionHeader']))
        elements.append(Spacer(1, 8))
        
        elements.append(Paragraph("No OSINT results found for this case.", self.styles['CaseInfo']))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_investigation_summary_second(self, case, content_items):
        """Create second investigation summary section"""
        elements = []
        
        # Section header
        elements.append(Paragraph("Investigation Summary", self.styles['SectionHeader']))
        elements.append(Spacer(1, 8))
        
        # Summary paragraph
        flagged_users = len(content_items) if content_items else 0
        flagged_posts = len(content_items) if content_items else 0
        
        summary_text = f"""This report consolidates evidence from web scraping, OSINT scanning, and NLP-based content analysis for Case {case.case_number}: {case.title}. The investigation identified {flagged_users} flagged users across multiple platforms, with {flagged_posts} pieces of content flagged for review. OSINT analysis was conducted on 0 queries, providing additional intelligence on the subjects under investigation."""
        
        elements.append(Paragraph(summary_text, self.styles['CaseInfo']))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_next_steps(self):
        """Create next steps section"""
        elements = []
        
        # Red sub-header
        elements.append(Paragraph("Next Steps", self.styles['RedSubHeader']))
        
        # Next steps list
        next_steps = [
            "Review all flagged content for accuracy and relevance",
            "Conduct additional OSINT searches on high-risk subjects",
            "Coordinate with law enforcement if evidence warrants",
            "Continue monitoring identified platforms and users",
            "Update case status based on investigation findings"
        ]
        
        for i, step in enumerate(next_steps, 1):
            elements.append(Paragraph(f"{i}. {step}", self.styles['CaseInfo']))
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_footer(self):
        """Create report footer"""
        elements = []
        
        # Horizontal line
        elements.append(Paragraph("_" * 80, self.styles['Normal']))
        elements.append(Spacer(1, 8))
        
        # Footer content
        elements.append(Paragraph("Generated by Narcotics Intelligence Platform © 2005", self.styles['FooterText']))
        elements.append(Paragraph(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['FooterText']))
        elements.append(Paragraph("This report contains sensitive information and should be handled according to security protocols.", self.styles['FooterText']))
        
        return elements


def generate_case_pdf_report(case, activities=None, content_items=None):
    """
    Generate a Narcotics Intelligence Platform Investigation Report
    
    Args:
        case: Case object
        activities: List of CaseActivity objects (optional)
        content_items: List of Content objects (optional)
    
    Returns:
        BytesIO object containing the PDF
    """
    generator = NarcoticsReportGenerator()
    return generator.generate_case_report(case, activities, content_items)
