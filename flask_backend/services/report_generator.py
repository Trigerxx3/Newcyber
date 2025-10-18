"""
Report Generator Service for generating PDF reports of investigation findings
"""
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import base64

from extensions import db
from models.case import Case
from models.content import Content
from models.osint_result import OSINTResult
from models.user import User
from models.user_case_link import UserCaseLink
from models.source import Source
from models.case_content_link import CaseContentLink


class ReportGenerator:
    """Service for generating investigation reports in PDF format"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.darkblue,
            borderPadding=5
        ))
        
        # Subheader style
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.darkred
        ))
        
        # Normal text style
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        # Warning text style
        self.styles.add(ParagraphStyle(
            name='WarningText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.red,
            spaceAfter=6
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey
        ))
    
    def generate_case_report(self, case_id: int) -> str:
        """
        Generate a comprehensive PDF report for a specific case
        
        Args:
            case_id (int): The ID of the case to generate report for
            
        Returns:
            str: Path to the generated PDF file
        """
        # Fetch case data
        case_data = self._fetch_case_data(case_id)
        if not case_data:
            raise ValueError(f"Case with ID {case_id} not found")
        
        # Create temporary file for PDF
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Case_{case_id}_Report_{timestamp}.pdf"
        pdf_path = os.path.join(temp_dir, filename)
        
        # Generate PDF
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        # Build story (content)
        story = []
        
        # Add header
        story.extend(self._create_header(case_data))
        
        # Add case overview
        story.extend(self._create_case_overview(case_data))
        
        # Add flagged content section
        story.extend(self._create_flagged_content_section(case_data))
        
        # Add OSINT results section
        story.extend(self._create_osint_results_section(case_data))
        
        # Add summary section
        story.extend(self._create_summary_section(case_data))
        
        # Add footer
        story.extend(self._create_footer())
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        
        return pdf_path
    
    def _fetch_case_data(self, case_id: int) -> Optional[Dict[str, Any]]:
        """Fetch all relevant data for a case"""
        case = Case.query.get(case_id)
        if not case:
            return None
        
        # Get case users (analysts)
        case_users = db.session.query(UserCaseLink, User).join(
            User, UserCaseLink.user_id == User.id
        ).filter(UserCaseLink.case_id == case_id).all()
        
        # Get flagged content linked to this case via CaseContentLink
        flagged_content = (
            db.session.query(Content)
            .join(CaseContentLink, CaseContentLink.content_id == Content.id)
            .filter(CaseContentLink.case_id == case_id, Content.is_flagged == True)
            .all()
        )
        
        # OSINT results: no direct link to case in current schema – derive none for now
        osint_results = []
        
        # Derive platform users from content authors as a fallback (unique authors)
        platform_users = []
        
        return {
            'case': case,
            'case_users': case_users,
            'flagged_content': flagged_content,
            'osint_results': osint_results,
            'platform_users': platform_users
        }
    
    def _create_header(self, case_data: Dict[str, Any]) -> List:
        """Create report header"""
        story = []
        
        # Main title
        story.append(Paragraph("Narcotics Intelligence Platform", self.styles['CustomTitle']))
        story.append(Paragraph("Investigation Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Horizontal line
        story.append(HRFlowable(width="100%", thickness=2, color=colors.darkblue))
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_case_overview(self, case_data: Dict[str, Any]) -> List:
        """Create case overview section"""
        story = []
        case = case_data['case']
        
        story.append(Paragraph("Case Overview", self.styles['CustomHeading1']))
        story.append(Spacer(1, 12))
        
        # Case details table
        case_details = [
            ['Case ID:', str(case.id)],
            ['Case Name:', case.title],
            ['Case Number:', case.case_number],
            ['Status:', case.status.value.title() if case.status else 'N/A'],
            ['Priority:', case.priority.value.title() if case.priority else 'N/A'],
            ['Type:', case.type.value.replace('_', ' ').title() if case.type else 'N/A'],
            ['Created Date:', case.created_at.strftime('%Y-%m-%d %H:%M:%S')],
            ['Last Updated:', case.updated_at.strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        # Add analyst information
        if case_data['case_users']:
            analysts = [f"{user.username} ({link.role.value})" for link, user in case_data['case_users']]
            case_details.append(['Analysts:', ', '.join(analysts)])
        
        # Add risk assessment
        if case.risk_score:
            case_details.append(['Risk Score:', f"{case.risk_score}/100"])
        if case.risk_level:
            case_details.append(['Risk Level:', case.risk_level.title()])
        
        table = Table(case_details, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Case description
        if case.description:
            story.append(Paragraph("Description", self.styles['CustomHeading2']))
            story.append(Paragraph(case.description, self.styles['CustomNormal']))
            story.append(Spacer(1, 12))
        
        # Summary statistics
        story.append(Paragraph("Investigation Summary", self.styles['CustomHeading2']))
        
        stats_data = [
            ['Platforms Analyzed:', self._get_platforms_analyzed(case_data)],
            ['Flagged Users:', str(len(case_data['platform_users']))],
            ['Flagged Posts:', str(len(case_data['flagged_content']))],
            ['OSINT Results:', str(len(case_data['osint_results']))]
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 4*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_flagged_content_section(self, case_data: Dict[str, Any]) -> List:
        """Create flagged content section"""
        story = []
        flagged_content = case_data['flagged_content']
        
        story.append(Paragraph("Flagged Content Analysis", self.styles['CustomHeading1']))
        story.append(Spacer(1, 12))
        
        if not flagged_content:
            story.append(Paragraph("No flagged content found for this case.", self.styles['CustomNormal']))
            story.append(Spacer(1, 20))
            return story
        
        for i, content in enumerate(flagged_content, 1):
            story.append(Paragraph(f"Content #{i}", self.styles['CustomHeading2']))
            
            # Content details
            content_details = [
                ['Username:', content.author or 'Unknown'],
                ['Platform:', content.source.platform.value if content.source else 'Unknown'],
                ['Content Type:', content.content_type.value if content.content_type else 'Text'],
                ['Suspicion Score:', f"{content.suspicion_score}/100"],
                ['Risk Level:', content.risk_level.value if content.risk_level else 'Low'],
                ['Intent:', content.intent or 'Unknown'],
                ['Date:', content.created_at.strftime('%Y-%m-%d %H:%M:%S')]
            ]
            
            if content.keywords:
                content_details.append(['Keywords:', ', '.join(content.keywords)])
            
            content_table = Table(content_details, colWidths=[1.5*inch, 4.5*inch])
            content_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(content_table)
            story.append(Spacer(1, 8))
            
            # Content text
            if content.text:
                story.append(Paragraph("Content:", self.styles['CustomHeading2']))
                # Truncate long content
                text = content.text[:500] + "..." if len(content.text) > 500 else content.text
                story.append(Paragraph(f'"{text}"', self.styles['WarningText']))
                story.append(Spacer(1, 8))
            
            # Analysis summary
            if content.analysis_summary:
                story.append(Paragraph("Analysis Summary:", self.styles['CustomHeading2']))
                story.append(Paragraph(content.analysis_summary, self.styles['CustomNormal']))
            
            story.append(Spacer(1, 15))
            
            # Add page break if this is not the last content item
            if i < len(flagged_content):
                story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
                story.append(Spacer(1, 10))
        
        return story
    
    def _create_osint_results_section(self, case_data: Dict[str, Any]) -> List:
        """Create OSINT results section"""
        story = []
        osint_results = case_data['osint_results']
        
        story.append(Paragraph("OSINT Investigation Results", self.styles['CustomHeading1']))
        story.append(Spacer(1, 12))
        
        if not osint_results:
            story.append(Paragraph("No OSINT results found for this case.", self.styles['CustomNormal']))
            story.append(Spacer(1, 20))
            return story
        
        for i, result in enumerate(osint_results, 1):
            story.append(Paragraph(f"OSINT Search #{i}", self.styles['CustomHeading2']))
            
            # OSINT details
            osint_details = [
                ['Query:', result.query],
                ['Search Type:', result.search_type.value if result.search_type else 'General'],
                ['Status:', result.status.value if result.status else 'Pending'],
                ['Risk Score:', f"{result.risk_score}/100"],
                ['Risk Level:', result.risk_level.title() if result.risk_level else 'Low'],
                ['Sources Searched:', str(result.total_sources_searched)],
                ['Successful Sources:', str(result.successful_sources)],
                ['Date:', result.created_at.strftime('%Y-%m-%d %H:%M:%S')]
            ]
            
            if result.completed_at:
                osint_details.append(['Completed:', result.completed_at.strftime('%Y-%m-%d %H:%M:%S')])
            
            osint_table = Table(osint_details, colWidths=[2*inch, 4*inch])
            osint_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(osint_table)
            story.append(Spacer(1, 8))
            
            # Summary
            if result.summary:
                story.append(Paragraph("Summary:", self.styles['CustomHeading2']))
                story.append(Paragraph(result.summary, self.styles['CustomNormal']))
                story.append(Spacer(1, 8))
            
            # Threat indicators
            if result.threat_indicators:
                story.append(Paragraph("Threat Indicators:", self.styles['CustomHeading2']))
                indicators_text = ', '.join(result.threat_indicators)
                story.append(Paragraph(indicators_text, self.styles['WarningText']))
            
            story.append(Spacer(1, 15))
            
            # Add page break if this is not the last result
            if i < len(osint_results):
                story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
                story.append(Spacer(1, 10))
        
        return story
    
    def _create_summary_section(self, case_data: Dict[str, Any]) -> List:
        """Create summary section"""
        story = []
        case = case_data['case']
        
        story.append(Paragraph("Investigation Summary", self.styles['CustomHeading1']))
        story.append(Spacer(1, 12))
        
        # Summary text
        summary_text = f"""
        This report consolidates evidence from web scraping, OSINT scanning, and NLP-based content analysis 
        for Case {case.case_number}: {case.title}.
        
        The investigation identified {len(case_data['platform_users'])} flagged users across multiple platforms, 
        with {len(case_data['flagged_content'])} pieces of content flagged for review. 
        OSINT analysis was conducted on {len(case_data['osint_results'])} queries, providing additional 
        intelligence on the subjects under investigation.
        """
        
        if case_data['flagged_content']:
            high_risk_content = [c for c in case_data['flagged_content'] if c.suspicion_score >= 80]
            if high_risk_content:
                summary_text += f"""
                
                Of particular concern are {len(high_risk_content)} pieces of content with suspicion scores 
                of 80 or higher, indicating strong intent of drug-related activities.
                """
        
        story.append(Paragraph(summary_text, self.styles['CustomNormal']))
        story.append(Spacer(1, 12))
        
        # Recommendations
        if case.recommendations:
            story.append(Paragraph("Recommendations", self.styles['CustomHeading2']))
            story.append(Paragraph(case.recommendations, self.styles['CustomNormal']))
            story.append(Spacer(1, 12))
        
        # Next steps
        story.append(Paragraph("Next Steps", self.styles['CustomHeading2']))
        next_steps = """
        1. Review all flagged content for accuracy and relevance
        2. Conduct additional OSINT searches on high-risk subjects
        3. Coordinate with law enforcement if evidence warrants
        4. Continue monitoring identified platforms and users
        5. Update case status based on investigation findings
        """
        story.append(Paragraph(next_steps, self.styles['CustomNormal']))
        
        return story
    
    def _create_footer(self) -> List:
        """Create report footer"""
        story = []
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        story.append(Spacer(1, 10))
        
        footer_text = f"""
        Generated by Narcotics Intelligence Platform © {datetime.now().year}<br/>
        Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        This report contains sensitive information and should be handled according to security protocols.
        """
        
        story.append(Paragraph(footer_text, self.styles['Footer']))
        
        return story
    
    def _add_page_number(self, canvas, doc):
        """Add page numbers to the PDF"""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(200*mm, 20*mm, text)
        canvas.restoreState()
    
    def _get_platforms_analyzed(self, case_data: Dict[str, Any]) -> str:
        """Get list of platforms analyzed"""
        platforms = set()
        
        # From flagged content
        for content in case_data['flagged_content']:
            if content.source and content.source.platform:
                platforms.add(content.source.platform.value)
        
        # From platform users
        for user in case_data['platform_users']:
            if user.source and user.source.platform:
                platforms.add(user.source.platform.value)
        
        return ', '.join(sorted(platforms)) if platforms else 'None'


# Global instance
report_generator = ReportGenerator()
