import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import openpyxl
import os
import streamlit as st
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        pass

    def export_projects_to_pdf(self, df, filename):
        # Stub: Replace with actual PDF export logic
        # For now, just save as CSV and return filename
        temp_filename = filename.replace('.pdf', '.csv')
        df.to_csv(temp_filename, index=False)
        return temp_filename

    def export_meetings_to_pdf(self, df, filename):
        # Stub: Replace with actual PDF export logic
        temp_filename = filename.replace('.pdf', '.csv')
        df.to_csv(temp_filename, index=False)
        return temp_filename

    def export_issues_to_pdf(self, df, filename):
        # Stub: Replace with actual PDF export logic
        temp_filename = filename.replace('.pdf', '.csv')
        df.to_csv(temp_filename, index=False)
        return temp_filename

    def export_to_excel(self, df, filename):
        # Export DataFrame to Excel
        df.to_excel(filename, index=False)
        return filename

# PDF Export Functions
def export_projects_to_pdf(df, filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Project Summary", styles['Title']))
    elements.append(Spacer(1, 12))
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    return filename

def export_meetings_to_pdf(df, filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Meeting Log", styles['Title']))
    elements.append(Spacer(1, 12))
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    return filename

def export_issues_to_pdf(df, filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Issue Tracker", styles['Title']))
    elements.append(Spacer(1, 12))
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    return filename

# Excel Export Functions
def export_to_excel(df, filename):
    df.to_excel(filename, index=False)
    return filename 