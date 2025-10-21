"""
Enhanced PDF Report Generator
Generates comprehensive case reports with analyst activities
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os
from io import BytesIO

class CaseReportGenerator:
    """Generate comprehensive PDF reports for cases"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            borderPadding=5,
            borderColor=colors.HexColor('#3498db'),
            borderWidth=0,
            leftIndent=0
        ))
        
        # Subsection heading
        self.styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ))
        
        # Metadata text
        self.styles.add(ParagraphStyle(
            name='Metadata',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=4
        ))
        
        # Activity title
        self.styles.add(ParagraphStyle(
            name='ActivityTitle',
            parent=self.styles['Heading4'],
            fontSize=11,
            textColor=colors.HexColor('#2980b9'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
    
    def generate_case_report(self, case, activities=None, content_items=None, output_path=None):
        """
        Generate a comprehensive case report PDF
        
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
        elements.extend(self._create_header(case))
        
        # Add case overview
        elements.extend(self._create_case_overview(case))
        
        # Add case details
        elements.extend(self._create_case_details(case))
        
        # Add analyst activities (if provided)
        if activities:
            elements.extend(self._create_activities_section(activities))
        
        # Add related content (if provided)
        if content_items:
            elements.extend(self._create_content_section(content_items))
        
        # Add findings and recommendations
        elements.extend(self._create_findings_section(case))
        
        # Add footer
        elements.extend(self._create_footer(case))
        
        # Build PDF
        pdf.build(elements)
        
        if output_path:
            return output_path
        else:
            buffer.seek(0)
            return buffer
    
    def _create_header(self, case):
        """Create report header"""
        elements = []
        
        # Title
        title = Paragraph(
            f"<b>Investigation Report</b><br/>{case.title}",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Case metadata table
        metadata = [
            ['Case Number:', case.case_number],
            ['Status:', case.status.value.upper() if case.status else 'N/A'],
            ['Priority:', case.priority.value.upper() if case.priority else 'N/A'],
            ['Risk Level:', case.risk_level.upper() if case.risk_level else 'N/A'],
            ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        table = Table(metadata, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#34495e')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_case_overview(self, case):
        """Create case overview section"""
        elements = []
        
        elements.append(Paragraph("Case Overview", self.styles['SectionHeading']))
        
        if case.description:
            elements.append(Paragraph(f"<b>Description:</b> {case.description}", self.styles['CustomBodyText']))
        
        if case.summary:
            elements.append(Paragraph(f"<b>Summary:</b> {case.summary}", self.styles['CustomBodyText']))
        
        if case.objectives:
            elements.append(Paragraph(f"<b>Objectives:</b> {case.objectives}", self.styles['CustomBodyText']))
        
        if case.methodology:
            elements.append(Paragraph(f"<b>Methodology:</b> {case.methodology}", self.styles['CustomBodyText']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_case_details(self, case):
        """Create detailed case information"""
        elements = []
        
        elements.append(Paragraph("Case Details", self.styles['SectionHeading']))
        
        # Timeline
        timeline_data = [
            ['Timeline', ''],
            ['Start Date:', case.start_date.strftime('%Y-%m-%d') if case.start_date else 'N/A'],
            ['Due Date:', case.due_date.strftime('%Y-%m-%d') if case.due_date else 'Not set'],
            ['Duration:', f"{case.get_duration_days()} days"],
            ['Progress:', f"{case.progress_percentage}%"]
        ]
        
        timeline_table = Table(timeline_data, colWidths=[2*inch, 3*inch])
        timeline_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#ecf0f1')),
        ]))
        
        elements.append(timeline_table)
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_activities_section(self, activities):
        """Create analyst activities section"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("Analyst Work & Activities", self.styles['SectionHeading']))
        
        if not activities:
            elements.append(Paragraph("No activities recorded for this case.", self.styles['CustomBodyText']))
            return elements
        
        # Filter only activities marked for report inclusion
        report_activities = [a for a in activities if a.include_in_report]
        
        if not report_activities:
            elements.append(Paragraph("No activities selected for report inclusion.", self.styles['CustomBodyText']))
            return elements
        
        # Group activities by type
        activities_by_type = {}
        for activity in report_activities:
            activity_type = activity.activity_type.value
            if activity_type not in activities_by_type:
                activities_by_type[activity_type] = []
            activities_by_type[activity_type].append(activity)
        
        # Add activities grouped by type
        for activity_type, activities_list in sorted(activities_by_type.items()):
            # Type heading
            type_heading = activity_type.replace('_', ' ').title()
            elements.append(Paragraph(f"{type_heading}s", self.styles['SubsectionHeading']))
            
            for activity in sorted(activities_list, key=lambda x: x.activity_date, reverse=True):
                # Activity block
                activity_elements = []
                
                # Title with date
                date_str = activity.activity_date.strftime('%Y-%m-%d %H:%M')
                analyst_name = activity.analyst.username if activity.analyst else 'Unknown'
                
                activity_elements.append(Paragraph(
                    f"<b>{activity.title}</b> <i>({date_str} by {analyst_name})</i>",
                    self.styles['ActivityTitle']
                ))
                
                # Description
                activity_elements.append(Paragraph(
                    activity.description,
                    self.styles['CustomBodyText']
                ))
                
                # Tags and metadata
                metadata_parts = []
                if activity.tags:
                    metadata_parts.append(f"Tags: {', '.join(activity.tags)}")
                if activity.priority:
                    metadata_parts.append(f"Priority: {activity.priority.upper()}")
                if activity.time_spent_minutes:
                    hours = activity.time_spent_minutes / 60
                    metadata_parts.append(f"Time: {hours:.1f}h")
                
                if metadata_parts:
                    activity_elements.append(Paragraph(
                        ' | '.join(metadata_parts),
                        self.styles['Metadata']
                    ))
                
                activity_elements.append(Spacer(1, 0.15*inch))
                
                # Keep activity together on same page
                elements.append(KeepTogether(activity_elements))
        
        return elements
    
    def _create_content_section(self, content_items):
        """Create related content section"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("Related Evidence & Content", self.styles['SectionHeading']))
        
        if not content_items:
            elements.append(Paragraph("No content items linked to this case.", self.styles['CustomBodyText']))
            return elements
        
        for content in content_items[:20]:  # Limit to 20 items
            content_elements = []
            
            # Content header
            author = content.author or 'Unknown'
            date_str = content.created_at.strftime('%Y-%m-%d') if content.created_at else 'N/A'
            
            content_elements.append(Paragraph(
                f"<b>{content.content_type.value if content.content_type else 'Content'}</b> by {author} ({date_str})",
                self.styles['SubsectionHeading']
            ))
            
            # Content text (truncated)
            text = content.text[:500] + '...' if len(content.text) > 500 else content.text
            content_elements.append(Paragraph(text, self.styles['CustomBodyText']))
            
            # Metadata
            metadata = f"Risk: {content.risk_level.value if content.risk_level else 'N/A'} | "
            metadata += f"Score: {content.suspicion_score or 0}/100"
            if content.is_flagged:
                metadata += " | FLAGGED"
            
            content_elements.append(Paragraph(metadata, self.styles['Metadata']))
            content_elements.append(Spacer(1, 0.15*inch))
            
            elements.append(KeepTogether(content_elements))
        
        return elements
    
    def _create_findings_section(self, case):
        """Create findings and recommendations section"""
        elements = []
        
        elements.append(PageBreak())
        
        # Findings
        if case.findings:
            elements.append(Paragraph("Key Findings", self.styles['SectionHeading']))
            elements.append(Paragraph(case.findings, self.styles['CustomBodyText']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Recommendations
        if case.recommendations:
            elements.append(Paragraph("Recommendations", self.styles['SectionHeading']))
            elements.append(Paragraph(case.recommendations, self.styles['CustomBodyText']))
            elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_footer(self, case):
        """Create report footer"""
        elements = []
        
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(
            "<i>This report is confidential and intended solely for authorized personnel.</i>",
            self.styles['Metadata']
        ))
        elements.append(Paragraph(
            f"<i>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>",
            self.styles['Metadata']
        ))
        
        return elements


# Convenience function
def generate_case_pdf_report(case, activities=None, content_items=None, output_path=None):
    """
    Generate a PDF report for a case
    
    Args:
        case: Case object
        activities: List of CaseActivity objects (optional)
        content_items: List of Content objects (optional)
        output_path: Where to save the PDF (optional, returns BytesIO if None)
    
    Returns:
        File path or BytesIO object containing the PDF
    """
    generator = CaseReportGenerator()
    return generator.generate_case_report(case, activities, content_items, output_path)

