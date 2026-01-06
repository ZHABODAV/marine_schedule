"""
PDF Report Generation Module

Generates professional PDF reports for vessel scheduling, voyage summaries,
and financial analysis using ReportLab library with matplotlib integration.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime, date
from typing import List, Dict, Optional, Any
import pandas as pd
import os
from pathlib import Path
from modules.security_utils import SecurityUtils
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import io
import numpy as np


class PDFReportGenerator:
    """
    Generates professional PDF reports for maritime operations.
    
    Supports multiple report types:
    - Vessel Schedule Reports
    - Voyage Summary Reports
    - Financial Analysis Reports
    - Berth Utilization Reports
    - Fleet Overview Reports
    """
    
    def __init__(self, output_dir: str = "output/reports"):
        """
        Initialize PDF Report Generator.
        
        Parameters:
            output_dir: Directory for output PDF files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # Branding colors
        self.brand_primary = colors.HexColor('#2c3e50')
        self.brand_secondary = colors.HexColor('#3498db')
        self.brand_accent = colors.HexColor('#16a085')
        self.brand_warning = colors.HexColor('#e74c3c')
        
    def _setup_custom_styles(self):
        """Setup custom paragraph and table styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#3498db'),
            spaceBefore=12,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))
    
    def _add_header_footer(self, canvas_obj, doc):
        """Add header and footer to each page."""
        canvas_obj.saveState()
        
        # Header
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.setFillColor(colors.HexColor('#2c3e50'))
        canvas_obj.drawString(inch, doc.height + inch, "Maritime Logistics Report")
        canvas_obj.drawRightString(
            doc.width + inch, 
            doc.height + inch,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        # Footer
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawCentredString(
            doc.width / 2 + inch,
            0.5 * inch,
            f"Page {canvas_obj.getPageNumber()}"
        )
        
        canvas_obj.restoreState()
    
    def _create_chart_image(self, fig, width: float = 6, height: float = 4, dpi: int = 100) -> Image:
        """
        Convert matplotlib figure to ReportLab Image.
        
        Parameters:
            fig: Matplotlib figure object
            width: Width in inches
            height: Height in inches
            dpi: Resolution
            
        Returns:
            ReportLab Image object
        """
        img_buffer = io.BytesIO()
        fig.set_size_inches(width, height)
        fig.savefig(img_buffer, format='png', dpi=dpi, bbox_inches='tight')
        img_buffer.seek(0)
        img = Image(img_buffer, width=width*inch, height=height*inch)
        plt.close(fig)
        return img
    
    def _create_bar_chart(self, data: pd.DataFrame, x_col: str, y_col: str,
                          title: str, xlabel: str, ylabel: str, color='#3498db') -> Image:
        """Create bar chart from DataFrame."""
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(data[x_col], data[y_col], color=color, alpha=0.7, edgecolor='black')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return self._create_chart_image(fig)
    
    def _create_pie_chart(self, labels: List[str], values: List[float],
                          title: str, colors_list=None) -> Image:
        """Create pie chart."""
        fig, ax = plt.subplots(figsize=(7, 7))
        if colors_list is None:
            colors_list = plt.cm.Set3(range(len(labels)))
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90,
               colors=colors_list, textprops={'fontsize': 10})
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        return self._create_chart_image(fig)
    
    def _create_line_chart(self, data: pd.DataFrame, x_col: str, y_cols: List[str],
                           title: str, xlabel: str, ylabel: str) -> Image:
        """Create line chart from DataFrame."""
        fig, ax = plt.subplots(figsize=(8, 5))
        for y_col in y_cols:
            ax.plot(data[x_col], data[y_col], marker='o', label=y_col, linewidth=2)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return self._create_chart_image(fig)
    
    def _create_gantt_chart(self, tasks: List[Dict], title: str = "Schedule Timeline") -> Image:
        """
        Create Gantt chart visualization.
        
        Parameters:
            tasks: List of dicts with 'name', 'start', 'end', 'color' keys
            title: Chart title
            
        Returns:
            ReportLab Image object
        """
        # Limit chart height to fit on page
        chart_height = min(5.5, max(4, len(tasks) * 0.4))
        fig, ax = plt.subplots(figsize=(8, chart_height))
        
        # Sort tasks by start date
        tasks_sorted = sorted(tasks, key=lambda x: x['start'])
        
        for idx, task in enumerate(tasks_sorted):
            start = task['start']
            end = task['end']
            duration = (end - start).days
            color = task.get('color', '#3498db')
            
            ax.barh(idx, duration, left=mdates.date2num(start),
                   height=0.5, color=color, alpha=0.7, edgecolor='black')
            ax.text(mdates.date2num(start) + duration/2, idx, task['name'],
                   ha='center', va='center', fontsize=8, fontweight='bold')
        
        ax.set_yticks(range(len(tasks_sorted)))
        ax.set_yticklabels([t['name'] for t in tasks_sorted], fontsize=8)
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.set_xlabel('Date', fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return self._create_chart_image(fig, width=8, height=chart_height)
    
    def generate_comprehensive_report(
        self,
        voyage_data: pd.DataFrame,
        filename: str = "comprehensive_voyage_report.pdf",
        title: str = "Comprehensive Voyage Report"
    ) -> str:
        """
        Generate comprehensive voyage report with all details, leg-by-leg breakdown,
        and full calculations.
        
        Parameters:
            voyage_data: DataFrame with complete voyage information
                Expected columns: voyage_id, vessel_name, load_port, discharge_port,
                distance_nm, duration_days, cargo_mt, freight_rate, revenue_usd, cost_usd, etc.
            filename: Output PDF filename
            title: Report title
            
        Returns:
            Path to generated PDF file
        """
        filepath = SecurityUtils.validate_path(filename, self.output_dir,
                                               allowed_extensions=['.pdf'],
                                               allow_subdirectories=False)
        
        doc = SimpleDocTemplate(str(filepath), pagesize=landscape(A4),
                               topMargin=1.5*inch, bottomMargin=inch)
        story = []
        
        # Title
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        total_voyages = len(voyage_data)
        total_distance = voyage_data['distance_nm'].sum() if 'distance_nm' in voyage_data.columns else 0
        total_cargo = voyage_data['cargo_mt'].sum() if 'cargo_mt' in voyage_data.columns else 0
        total_revenue = voyage_data['revenue_usd'].sum() if 'revenue_usd' in voyage_data.columns else 0
        total_cost = voyage_data['cost_usd'].sum() if 'cost_usd' in voyage_data.columns else 0
        profit = total_revenue - total_cost
        
        summary_text = f"""
        <b>Reporting Period:</b> {datetime.now().strftime('%B %Y')}<br/>
        <b>Total Voyages:</b> {total_voyages}<br/>
        <b>Total Distance:</b> {total_distance:,.0f} NM<br/>
        <b>Total Cargo Moved:</b> {total_cargo:,.0f} MT<br/>
        <b>Total Revenue:</b> ${total_revenue:,.2f}<br/>
        <b>Total Cost:</b> ${total_cost:,.2f}<br/>
        <b>Net Profit:</b> ${profit:,.2f}<br/>
        <b>Profit Margin:</b> {(profit/total_revenue*100 if total_revenue > 0 else 0):.1f}%
        """
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Voyage by Voyage Breakdown
        story.append(PageBreak())
        story.append(Paragraph("Detailed Voyage Breakdown", self.styles['SectionHeader']))
        
        if not voyage_data.empty:
            # Select key columns for display
            display_cols = ['voyage_id', 'vessel_name', 'load_port', 'discharge_port',
                          'distance_nm', 'duration_days', 'cargo_mt', 'freight_rate',
                          'revenue_usd', 'cost_usd']
            available_cols = [col for col in display_cols if col in voyage_data.columns]
            
            if available_cols:
                table_data = [[col.replace('_', ' ').title() for col in available_cols]]
                
                for _, row in voyage_data[available_cols].iterrows():
                    formatted_row = []
                    for col, val in zip(available_cols, row):
                        if pd.isna(val):
                            formatted_row.append('')
                        elif col in ['revenue_usd', 'cost_usd', 'freight_rate']:
                            formatted_row.append(f'${float(val):,.2f}')
                        elif col in ['distance_nm', 'cargo_mt']:
                            formatted_row.append(f'{float(val):,.1f}')
                        elif col == 'duration_days':
                            formatted_row.append(f'{float(val):.1f}')
                        else:
                            formatted_row.append(str(val))
                    table_data.append(formatted_row)
                
                table = Table(table_data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.brand_primary),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))
                story.append(table)
        
        # Performance Charts
        if 'vessel_name' in voyage_data.columns and 'revenue_usd' in voyage_data.columns:
            story.append(PageBreak())
            story.append(Paragraph("Performance Analysis", self.styles['SectionHeader']))
            
            # Revenue by vessel
            vessel_revenue = voyage_data.groupby('vessel_name')['revenue_usd'].sum().reset_index()
            if not vessel_revenue.empty:
                chart = self._create_bar_chart(vessel_revenue, 'vessel_name', 'revenue_usd',
                                               'Revenue by Vessel', 'Vessel', 'Revenue (USD)',
                                               color='#16a085')
                story.append(chart)
                story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer,
                 onLaterPages=self._add_header_footer)
        
        return str(filepath)
    
    def generate_fleet_report(
        self,
        fleet_data: pd.DataFrame,
        utilization_data: Optional[pd.DataFrame] = None,
        performance_data: Optional[pd.DataFrame] = None,
        filename: str = "fleet_analysis_report.pdf"
    ) -> str:
        """
        Generate comprehensive fleet report with utilization charts, performance metrics,
        and comparison graphs.
        
        Parameters:
            fleet_data: DataFrame with fleet information
            utilization_data: DataFrame with vessel utilization metrics
            performance_data: DataFrame with performance metrics
            filename: Output PDF filename
            
        Returns:
            Path to generated PDF file
        """
        filepath = SecurityUtils.validate_path(filename, self.output_dir,
                                               allowed_extensions=['.pdf'],
                                               allow_subdirectories=False)
        
        doc = SimpleDocTemplate(str(filepath), pagesize=landscape(A4),
                               topMargin=1.5*inch, bottomMargin=inch)
        story = []
        
        # Title
        story.append(Paragraph("Fleet Performance & Utilization Report",
                              self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Fleet Summary
        story.append(Paragraph("Fleet Overview", self.styles['SectionHeader']))
        total_vessels = len(fleet_data)
        total_dwt = fleet_data['dwt_mt'].sum() if 'dwt_mt' in fleet_data.columns else 0
        avg_age = fleet_data['age_years'].mean() if 'age_years' in fleet_data.columns else 0
        avg_speed = fleet_data['speed_kts'].mean() if 'speed_kts' in fleet_data.columns else 0
        
        summary_text = f"""
        <b>Total Vessels:</b> {total_vessels}<br/>
        <b>Total Capacity:</b> {total_dwt:,.0f} MT (DWT)<br/>
        <b>Average Age:</b> {avg_age:.1f} years<br/>
        <b>Average Speed:</b> {avg_speed:.1f} knots<br/>
        <b>Report Date:</b> {datetime.now().strftime('%Y-%m-%d')}
        """
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Fleet Composition Table
        if not fleet_data.empty:
            story.append(Paragraph("Fleet Composition", self.styles['SectionHeader']))
            display_cols = ['vessel_name', 'vessel_type', 'dwt_mt', 'speed_kts',
                          'age_years', 'flag']
            available_cols = [col for col in display_cols if col in fleet_data.columns]
            
            if available_cols:
                table_data = [[col.replace('_', ' ').title() for col in available_cols]]
                for _, row in fleet_data[available_cols].iterrows():
                    table_data.append([str(val) if val is not None else '' for val in row])
                
                table = Table(table_data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.brand_accent),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.3*inch))
        
        # Utilization Charts
        if utilization_data is not None and not utilization_data.empty:
            story.append(PageBreak())
            story.append(Paragraph("Vessel Utilization Analysis", self.styles['SectionHeader']))
            
            if 'vessel_name' in utilization_data.columns and 'utilization_pct' in utilization_data.columns:
                # Utilization bar chart
                chart = self._create_bar_chart(utilization_data, 'vessel_name', 'utilization_pct',
                                               'Vessel Utilization (%)', 'Vessel', 'Utilization %',
                                               color='#e74c3c')
                story.append(chart)
                story.append(Spacer(1, 0.3*inch))
                
                # Utilization pie chart
                if len(utilization_data) <= 10:
                    labels = utilization_data['vessel_name'].tolist()
                    values = utilization_data['utilization_pct'].tolist()
                    pie_chart = self._create_pie_chart(labels, values,
                                                       'Fleet Utilization Distribution')
                    story.append(pie_chart)
        
        # Performance Metrics
        if performance_data is not None and not performance_data.empty:
            story.append(PageBreak())
            story.append(Paragraph("Performance Metrics", self.styles['SectionHeader']))
            
            # Performance comparison table
            table_data = [list(performance_data.columns)]
            for _, row in performance_data.iterrows():
                table_data.append([str(val) if val is not None else '' for val in row])
            
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.brand_secondary),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(table)
            
            # Performance comparison chart
            if 'vessel_name' in performance_data.columns:
                numeric_cols = performance_data.select_dtypes(include=[np.number]).columns.tolist()
                if len(numeric_cols) > 0:
                    story.append(Spacer(1, 0.3*inch))
                    compare_col = numeric_cols[0]
                    chart = self._create_bar_chart(performance_data, 'vessel_name', compare_col,
                                                   f'{compare_col.replace("_", " ").title()} Comparison',
                                                   'Vessel', compare_col.replace('_', ' ').title(),
                                                   color='#9b59b6')
                    story.append(chart)
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer,
                 onLaterPages=self._add_header_footer)
        
        return str(filepath)
    
    def generate_schedule_report(
        self,
        schedule_data: pd.DataFrame,
        milestones: Optional[List[Dict]] = None,
        filename: str = "schedule_timeline_report.pdf"
    ) -> str:
        """
        Generate schedule report with timeline visualization, Gantt chart rendering,
        and milestone tracking.
        
        Parameters:
            schedule_data: DataFrame with schedule information
                Expected columns: task_name, start_date, end_date, status, vessel_name
            milestones: Optional list of milestone dicts with 'name', 'date', 'description'
            filename: Output PDF filename
            
        Returns:
            Path to generated PDF file
        """
        filepath = SecurityUtils.validate_path(filename, self.output_dir,
                                               allowed_extensions=['.pdf'],
                                               allow_subdirectories=False)
        
        doc = SimpleDocTemplate(str(filepath), pagesize=landscape(A4),
                               topMargin=1.5*inch, bottomMargin=inch)
        story = []
        
        # Title
        story.append(Paragraph("Schedule Timeline & Gantt Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Schedule Summary
        story.append(Paragraph("Schedule Overview", self.styles['SectionHeader']))
        total_tasks = len(schedule_data)
        
        # Convert date columns if they're strings
        if 'start_date' in schedule_data.columns:
            schedule_data['start_date'] = pd.to_datetime(schedule_data['start_date'])
        if 'end_date' in schedule_data.columns:
            schedule_data['end_date'] = pd.to_datetime(schedule_data['end_date'])
        
        earliest_start = schedule_data['start_date'].min() if 'start_date' in schedule_data.columns else None
        latest_end = schedule_data['end_date'].max() if 'end_date' in schedule_data.columns else None
        
        summary_text = f"""
        <b>Total Tasks:</b> {total_tasks}<br/>
        <b>Start Date:</b> {earliest_start.strftime('%Y-%m-%d') if earliest_start else 'N/A'}<br/>
        <b>End Date:</b> {latest_end.strftime('%Y-%m-%d') if latest_end else 'N/A'}<br/>
        <b>Duration:</b> {(latest_end - earliest_start).days if earliest_start and latest_end else 0} days<br/>
        <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Schedule Table
        story.append(Paragraph("Detailed Schedule", self.styles['SectionHeader']))
        display_cols = ['task_name', 'vessel_name', 'start_date', 'end_date', 'status']
        available_cols = [col for col in display_cols if col in schedule_data.columns]
        
        if available_cols:
            table_data = [[col.replace('_', ' ').title() for col in available_cols]]
            for _, row in schedule_data[available_cols].iterrows():
                formatted_row = []
                for col, val in zip(available_cols, row):
                    if pd.isna(val):
                        formatted_row.append('')
                    elif col in ['start_date', 'end_date']:
                        formatted_row.append(val.strftime('%Y-%m-%d') if hasattr(val, 'strftime') else str(val))
                    else:
                        formatted_row.append(str(val))
                table_data.append(formatted_row)
            
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.brand_primary),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(table)
        
        # Gantt Chart
        if 'task_name' in schedule_data.columns and 'start_date' in schedule_data.columns and 'end_date' in schedule_data.columns:
            story.append(PageBreak())
            story.append(Paragraph("Gantt Chart Visualization", self.styles['SectionHeader']))
            
            # Prepare tasks for Gantt chart
            tasks = []
            color_map = {'completed': '#27ae60', 'in_progress': '#3498db',
                        'pending': '#95a5a6', 'delayed': '#e74c3c'}
            
            for _, row in schedule_data.iterrows():
                task = {
                    'name': row['task_name'],
                    'start': row['start_date'],
                    'end': row['end_date'],
                    'color': color_map.get(row.get('status', 'pending'), '#3498db')
                }
                tasks.append(task)
            
            if tasks:
                gantt_chart = self._create_gantt_chart(tasks, "Project Timeline")
                story.append(gantt_chart)
        
        # Milestones Section
        if milestones:
            story.append(PageBreak())
            story.append(Paragraph("Project Milestones", self.styles['SectionHeader']))
            
            milestone_data = []
            for milestone in milestones:
                milestone_text = f"""
                <b>{milestone.get('name', 'Milestone')}:</b> {milestone.get('date', 'TBD')}<br/>
                {milestone.get('description', '')}
                """
                story.append(Paragraph(milestone_text, self.styles['Normal']))
                story.append(Spacer(1, 0.15*inch))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer,
                 onLaterPages=self._add_header_footer)
        
        return str(filepath)
    
    def generate_financial_report(
        self,
        financial_data: pd.DataFrame,
        revenue_projections: Optional[pd.DataFrame] = None,
        filename: str = "financial_analysis_report.pdf"
    ) -> str:
        """
        Generate comprehensive financial report with cost breakdown charts,
        revenue projections, and profitability analysis.
        
        Parameters:
            financial_data: DataFrame with financial information
                Expected columns: cost_category, amount_usd, voyage_id, revenue_usd, etc.
            revenue_projections: Optional DataFrame with projected revenues
            filename: Output PDF filename
            
        Returns:
            Path to generated PDF file
        """
        filepath = SecurityUtils.validate_path(filename, self.output_dir,
                                               allowed_extensions=['.pdf'],
                                               allow_subdirectories=False)
        
        doc = SimpleDocTemplate(str(filepath), pagesize=letter,
                               topMargin=1.5*inch, bottomMargin=inch)
        story = []
        
        # Title
        story.append(Paragraph("Financial Analysis & Profitability Report",
                              self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Financial Summary
        story.append(Paragraph("Financial Summary", self.styles['SectionHeader']))
        
        total_revenue = financial_data['revenue_usd'].sum() if 'revenue_usd' in financial_data.columns else 0
        total_cost = financial_data['cost_usd'].sum() if 'cost_usd' in financial_data.columns else 0
        net_profit = total_revenue - total_cost
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        summary_text = f"""
        <b>Total Revenue:</b> ${total_revenue:,.2f}<br/>
        <b>Total Cost:</b> ${total_cost:,.2f}<br/>
        <b>Net Profit:</b> ${net_profit:,.2f}<br/>
        <b>Profit Margin:</b> {profit_margin:.2f}%<br/>
        <b>Report Period:</b> {datetime.now().strftime('%B %Y')}<br/>
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Cost Breakdown
        if 'cost_category' in financial_data.columns and 'cost_usd' in financial_data.columns:
            story.append(Paragraph("Cost Breakdown by Category", self.styles['SectionHeader']))
            
            cost_by_category = financial_data.groupby('cost_category')['cost_usd'].sum().reset_index()
            cost_by_category = cost_by_category.sort_values('cost_usd', ascending=False)
            
            # Cost breakdown table
            table_data = [['Cost Category', 'Amount (USD)', 'Percentage']]
            for _, row in cost_by_category.iterrows():
                pct = (row['cost_usd'] / total_cost * 100) if total_cost > 0 else 0
                table_data.append([
                    row['cost_category'],
                    f"${row['cost_usd']:,.2f}",
                    f"{pct:.1f}%"
                ])
            
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.brand_warning),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
            
            # Cost breakdown pie chart
            story.append(PageBreak())
            story.append(Paragraph("Cost Distribution Visualization", self.styles['SectionHeader']))
            labels = cost_by_category['cost_category'].tolist()
            values = cost_by_category['cost_usd'].tolist()
            pie_chart = self._create_pie_chart(labels, values, 'Cost Distribution by Category')
            story.append(pie_chart)
        
        # Revenue Analysis
        if 'voyage_id' in financial_data.columns and 'revenue_usd' in financial_data.columns:
            story.append(PageBreak())
            story.append(Paragraph("Revenue Analysis", self.styles['SectionHeader']))
            
            revenue_by_voyage = financial_data.groupby('voyage_id')['revenue_usd'].sum().reset_index()
            revenue_by_voyage = revenue_by_voyage.sort_values('revenue_usd', ascending=False).head(10)
            
            if not revenue_by_voyage.empty:
                chart = self._create_bar_chart(revenue_by_voyage, 'voyage_id', 'revenue_usd',
                                               'Top 10 Voyages by Revenue', 'Voyage ID', 'Revenue (USD)',
                                               color='#27ae60')
                story.append(chart)
        
        # Revenue Projections
        if revenue_projections is not None and not revenue_projections.empty:
            story.append(PageBreak())
            story.append(Paragraph("Revenue Projections", self.styles['SectionHeader']))
            
            # Projection table
            table_data = [list(revenue_projections.columns)]
            for _, row in revenue_projections.iterrows():
                formatted_row = []
                for val in row:
                    if isinstance(val, (int, float)):
                        formatted_row.append(f"${val:,.2f}")
                    else:
                        formatted_row.append(str(val))
                table_data.append(formatted_row)
            
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.brand_secondary),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
            
            # Projection line chart
            if 'period' in revenue_projections.columns:
                numeric_cols = [col for col in revenue_projections.columns
                               if col != 'period' and revenue_projections[col].dtype in [np.float64, np.int64]]
                if numeric_cols:
                    chart = self._create_line_chart(revenue_projections, 'period', numeric_cols,
                                                    'Revenue Projections Over Time',
                                                    'Period', 'Amount (USD)')
                    story.append(chart)
        
        # Profitability Analysis
        story.append(PageBreak())
        story.append(Paragraph("Profitability Analysis", self.styles['SectionHeader']))
        
        if 'voyage_id' in financial_data.columns and 'revenue_usd' in financial_data.columns and 'cost_usd' in financial_data.columns:
            profit_by_voyage = financial_data.groupby('voyage_id').agg({
                'revenue_usd': 'sum',
                'cost_usd': 'sum'
            }).reset_index()
            profit_by_voyage['profit'] = profit_by_voyage['revenue_usd'] - profit_by_voyage['cost_usd']
            profit_by_voyage['margin_pct'] = (profit_by_voyage['profit'] / profit_by_voyage['revenue_usd'] * 100).round(2)
            
            # Profitability table
            table_data = [['Voyage ID', 'Revenue', 'Cost', 'Profit', 'Margin %']]
            for _, row in profit_by_voyage.head(15).iterrows():
                table_data.append([
                    row['voyage_id'],
                    f"${row['revenue_usd']:,.2f}",
                    f"${row['cost_usd']:,.2f}",
                    f"${row['profit']:,.2f}",
                    f"{row['margin_pct']:.1f}%"
                ])
            
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.brand_accent),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(table)
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer,
                 onLaterPages=self._add_header_footer)
        
        return str(filepath)
    
    def generate_vessel_schedule_report(
        self,
        vessel_data: pd.DataFrame,
        filename: str = "vessel_schedule_report.pdf",
        title: str = "Vessel Schedule Report"
    ) -> str:
        """
        Generate vessel schedule PDF report.
        
        Parameters:
            vessel_data: DataFrame with vessel schedule data
            filename: Output PDF filename
            title: Report title
            
        Returns:
            Path to generated PDF file
        """
        # Validate output path
        filepath = SecurityUtils.validate_path(filename, self.output_dir, allowed_extensions=['.pdf'], allow_subdirectories=False)
        
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=landscape(letter),
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=1.5*inch,
            bottomMargin=inch
        )
        
        story = []
        
        # Title
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary section
        summary_text = f"""
        <b>Report Period:</b> {datetime.now().strftime('%B %Y')}<br/>
        <b>Total Vessels:</b> {len(vessel_data)}<br/>
        <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Vessel schedule table
        if not vessel_data.empty:
            story.append(Paragraph("Vessel Schedule", self.styles['SectionHeader']))
            
            # Prepare table data
            table_data = [list(vessel_data.columns)]
            for _, row in vessel_data.iterrows():
                table_data.append([str(val) if val is not None else '' for val in row])
            
            # Create table
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(table)
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        return str(filepath)
    
    def generate_voyage_summary_report(
        self,
        voyage_data: pd.DataFrame,
        filename: str = "voyage_summary_report.pdf",
        include_financials: bool = True
    ) -> str:
        """
        Generate voyage summary PDF report with optional financial analysis.
        
        Parameters:
            voyage_data: DataFrame with voyage data
            filename: Output PDF filename
            include_financials: Include financial metrics
            
        Returns:
            Path to generated PDF file
        """
        # Validate output path
        filepath = SecurityUtils.validate_path(filename, self.output_dir, allowed_extensions=['.pdf'], allow_subdirectories=False)
        
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        
        story = []
        
        # Title
        story.append(Paragraph("Voyage Summary Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        total_voyages = len(voyage_data)
        total_distance = voyage_data['distance_nm'].sum() if 'distance_nm' in voyage_data.columns else 0
        avg_duration = voyage_data['duration_days'].mean() if 'duration_days' in voyage_data.columns else 0
        
        summary_text = f"""
        <b>Total Voyages:</b> {total_voyages}<br/>
        <b>Total Distance:</b> {total_distance:,.0f} NM<br/>
        <b>Average Duration:</b> {avg_duration:.1f} days<br/>
        <b>Period:</b> {datetime.now().strftime('%B %Y')}
        """
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Voyage details table
        if not voyage_data.empty:
            story.append(Paragraph("Voyage Details", self.styles['SectionHeader']))
            
            # Select relevant columns
            display_cols = ['voyage_id', 'vessel_name', 'load_port', 'discharge_port', 
                          'distance_nm', 'duration_days']
            available_cols = [col for col in display_cols if col in voyage_data.columns]
            
            if available_cols:
                table_data = [available_cols]
                for _, row in voyage_data[available_cols].head(20).iterrows():
                    table_data.append([str(val) if val is not None else '' for val in row])
                
                table = Table(table_data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))
                
                story.append(table)
        
        # Financial section
        if include_financials and 'revenue_usd' in voyage_data.columns:
            story.append(PageBreak())
            story.append(Paragraph("Financial Analysis", self.styles['SectionHeader']))
            
            total_revenue = voyage_data['revenue_usd'].sum()
            total_cost = voyage_data['cost_usd'].sum() if 'cost_usd' in voyage_data.columns else 0
            
            financial_text = f"""
            <b>Total Revenue:</b> ${total_revenue:,.2f}<br/>
            <b>Total Cost:</b> ${total_cost:,.2f}
            """
            story.append(Paragraph(financial_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        return str(filepath)
    
    def generate_fleet_overview_report(
        self,
        fleet_data: pd.DataFrame,
        utilization_data: Optional[pd.DataFrame] = None,
        filename: str = "fleet_overview_report.pdf"
    ) -> str:
        """
        Generate comprehensive fleet overview PDF report.
        
        Parameters:
            fleet_data: DataFrame with fleet information
            utilization_data: Optional DataFrame with utilization metrics
            filename: Output PDF filename
            
        Returns:
            Path to generated PDF file
        """
        # Validate output path
        filepath = SecurityUtils.validate_path(filename, self.output_dir, allowed_extensions=['.pdf'], allow_subdirectories=False)
        
        doc = SimpleDocTemplate(str(filepath), pagesize=landscape(A4))
        
        story = []
        
        # Title
        story.append(Paragraph("Fleet Overview Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Fleet statistics
        story.append(Paragraph("Fleet Statistics", self.styles['SectionHeader']))
        
        total_vessels = len(fleet_data)
        total_dwt = fleet_data['dwt_mt'].sum() if 'dwt_mt' in fleet_data.columns else 0
        avg_speed = fleet_data['speed_kts'].mean() if 'speed_kts' in fleet_data.columns else 0
        
        stats_text = f"""
        <b>Total Vessels:</b> {total_vessels}<br/>
        <b>Total DWT:</b> {total_dwt:,.0f} MT<br/>
        <b>Average Speed:</b> {avg_speed:.1f} knots<br/>
        <b>Report Date:</b> {datetime.now().strftime('%Y-%m-%d')}
        """
        story.append(Paragraph(stats_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Fleet composition table
        story.append(Paragraph("Fleet Composition", self.styles['SectionHeader']))
        
        if not fleet_data.empty:
            table_data = [list(fleet_data.columns[:6])]  # First 6 columns
            for _, row in fleet_data.iterrows():
                table_data.append([str(val) if val is not None else '' for val in row[:6]])
            
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a085')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(table)
        
        # Utilization section
        if utilization_data is not None and not utilization_data.empty:
            story.append(PageBreak())
            story.append(Paragraph("Fleet Utilization", self.styles['SectionHeader']))
            
            util_table_data = [list(utilization_data.columns)]
            for _, row in utilization_data.iterrows():
                util_table_data.append([str(val) if val is not None else '' for val in row])
            
            util_table = Table(util_table_data, repeatRows=1)
            util_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(util_table)
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        return str(filepath)
    
    def generate_berth_utilization_report(
        self,
        berth_data: pd.DataFrame,
        port_name: str,
        filename: str = "berth_utilization_report.pdf"
    ) -> str:
        """
        Generate berth utilization PDF report.
        
        Parameters:
            berth_data: DataFrame with berth utilization data
            port_name: Name of the port
            filename: Output PDF filename
            
        Returns:
            Path to generated PDF file
        """
        # Validate output path
        filepath = SecurityUtils.validate_path(filename, self.output_dir, allowed_extensions=['.pdf'], allow_subdirectories=False)
        
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        
        story = []
        
        # Title
        title = f"Berth Utilization Report - {port_name}"
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Summary
        if not berth_data.empty:
            avg_utilization = berth_data['utilization_pct'].mean() if 'utilization_pct' in berth_data.columns else 0
            total_operations = len(berth_data)
            
            summary_text = f"""
            <b>Port:</b> {port_name}<br/>
            <b>Average Utilization:</b> {avg_utilization:.1f}%<br/>
            <b>Total Operations:</b> {total_operations}<br/>
            <b>Period:</b> {datetime.now().strftime('%B %Y')}
            """
            story.append(Paragraph(summary_text, self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Utilization table
            story.append(Paragraph("Berth Operations", self.styles['SectionHeader']))
            
            table_data = [list(berth_data.columns)]
            for _, row in berth_data.iterrows():
                table_data.append([str(val) if val is not None else '' for val in row])
            
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(table)
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        return str(filepath)
    
    def generate_custom_report(
        self,
        data_sections: List[Dict[str, Any]],
        title: str,
        filename: str
    ) -> str:
        """
        Generate custom PDF report with multiple data sections.
        
        Parameters:
            data_sections: List of dictionaries with 'title' and 'data' keys
            title: Report title
            filename: Output PDF filename
            
        Returns:
            Path to generated PDF file
        """
        # Validate output path
        filepath = SecurityUtils.validate_path(filename, self.output_dir, allowed_extensions=['.pdf'], allow_subdirectories=False)
        
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        
        story = []
        
        # Title
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Process each section
        for section in data_sections:
            section_title = section.get('title', 'Section')
            section_data = section.get('data')
            
            story.append(Paragraph(section_title, self.styles['SectionHeader']))
            
            if isinstance(section_data, pd.DataFrame) and not section_data.empty:
                table_data = [list(section_data.columns)]
                for _, row in section_data.iterrows():
                    table_data.append([str(val) if val is not None else '' for val in row])
                
                table = Table(table_data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))
                
                story.append(table)
            elif isinstance(section_data, str):
                story.append(Paragraph(section_data, self.styles['Normal']))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        return str(filepath)


def generate_pdf_report(
    report_type: str,
    data: pd.DataFrame,
    output_dir: str = "output/reports",
    **kwargs
) -> str:
    """
    Convenience function to generate PDF reports.
    
    Parameters:
        report_type: Type of report ('vessel_schedule', 'voyage_summary', 'fleet_overview', 'berth_utilization')
        data: DataFrame with report data
        output_dir: Output directory for PDF files
        **kwargs: Additional arguments for specific report types
        
    Returns:
        Path to generated PDF file
    """
    generator = PDFReportGenerator(output_dir=output_dir)
    
    if report_type == 'vessel_schedule':
        return generator.generate_vessel_schedule_report(data, **kwargs)
    elif report_type == 'voyage_summary':
        return generator.generate_voyage_summary_report(data, **kwargs)
    elif report_type == 'fleet_overview':
        return generator.generate_fleet_overview_report(data, **kwargs)
    elif report_type == 'berth_utilization':
        return generator.generate_berth_utilization_report(data, **kwargs)
    else:
        raise ValueError(f"Unknown report type: {report_type}")
