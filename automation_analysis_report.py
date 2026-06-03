#!/usr/bin/env python3
"""
Nexlify Business Automation Analysis Report Template
Assesses an organization's workflows and identifies automation opportunities.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas
import datetime

# ── Brand Colors ──

PRIMARY = HexColor("#6c5ce7")
PRIMARY_LIGHT = HexColor("#a29bfe")
ACCENT_GREEN = HexColor("#00b894")
ACCENT_RED = HexColor("#e17055")
ACCENT_YELLOW = HexColor("#fdcb6e")
ACCENT_BLUE = HexColor("#0984e3")
TEXT_DARK = HexColor("#1a1a2e")
TEXT_MED = HexColor("#4a4a6a")
TEXT_LIGHT = HexColor("#8a8aaa")
BG_LIGHT = HexColor("#f8f9fc")
BG_CARD = HexColor("#ffffff")
BORDER_LIGHT = HexColor("#e8e8f0")
SECTION_BG = HexColor("#f0eeff")


def create_styles():
    styles = getSampleStyleSheet()

    custom_styles = {
        'ReportTitle': dict(parent=styles['Title'], fontName='Helvetica-Bold',
            fontSize=26, textColor=PRIMARY, spaceAfter=6, leading=32, alignment=TA_CENTER),
        'ReportSubtitle': dict(parent=styles['Normal'], fontName='Helvetica',
            fontSize=13, textColor=TEXT_MED, spaceAfter=20, leading=18, alignment=TA_CENTER),
        'SectionHeader': dict(parent=styles['Heading1'], fontName='Helvetica-Bold',
            fontSize=18, textColor=TEXT_DARK, spaceBefore=24, spaceAfter=12, leading=22),
        'SubHeader': dict(parent=styles['Heading2'], fontName='Helvetica-Bold',
            fontSize=13, textColor=TEXT_DARK, spaceBefore=14, spaceAfter=6, leading=16),
        'BodyText2': dict(parent=styles['Normal'], fontName='Helvetica',
            fontSize=10, textColor=TEXT_MED, spaceAfter=8, leading=15),
        'FooterStyle': dict(parent=styles['Normal'], fontName='Helvetica',
            fontSize=8, textColor=TEXT_LIGHT, alignment=TA_CENTER),
        'TableHeader': dict(fontName='Helvetica-Bold', fontSize=9, textColor=white, alignment=TA_CENTER),
        'TableCell': dict(fontName='Helvetica', fontSize=9, textColor=TEXT_DARK, leading=13),
        'TableCellCenter': dict(fontName='Helvetica', fontSize=9, textColor=TEXT_DARK, leading=13, alignment=TA_CENTER),
        'CoverClient': dict(fontName='Helvetica-Bold', fontSize=16, textColor=TEXT_DARK,
            alignment=TA_CENTER, spaceAfter=8),
        'CoverDate': dict(fontName='Helvetica', fontSize=11, textColor=TEXT_MED, alignment=TA_CENTER),
        'BrandMark': dict(parent=styles['Normal'], fontName='Helvetica-Bold',
            fontSize=14, textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=30),
        'Confidential': dict(parent=styles['Normal'], fontName='Helvetica-Oblique',
            fontSize=8, textColor=TEXT_LIGHT, alignment=TA_CENTER, leading=12),
        'MetricValue': dict(fontName='Helvetica-Bold', fontSize=26, textColor=PRIMARY, alignment=TA_CENTER),
        'MetricLabel': dict(fontName='Helvetica', fontSize=9, textColor=TEXT_MED, alignment=TA_CENTER),
        'BulletItem': dict(parent=styles['Normal'], fontName='Helvetica', fontSize=10,
            textColor=TEXT_MED, leftIndent=20, bulletIndent=8, spaceBefore=2, spaceAfter=2, leading=15),
    }

    for name, kwargs in custom_styles.items():
        styles.add(ParagraphStyle(name, **kwargs))

    return styles


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_extras(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _draw_extras(self, page_count):
        self.saveState()
        w, h = letter
        self.setStrokeColor(BORDER_LIGHT)
        self.setLineWidth(0.5)
        self.line(0.75 * inch, 0.6 * inch, w - 0.75 * inch, 0.6 * inch)
        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_LIGHT)
        self.drawString(0.75 * inch, 0.4 * inch,
                        "nexlify  |  nexlifylimited.com  |  hello@nexlifylimited.com")
        self.drawRightString(w - 0.75 * inch, 0.4 * inch,
                             f"Page {self._pageNumber} of {page_count}")
        self.setFillColor(PRIMARY)
        self.rect(0, h - 4, w, 4, fill=1, stroke=0)
        self.restoreState()


# ─── Helper: styled table ───

def make_table(styles, headers, rows, col_widths):
    header_row = [Paragraph(h, styles['TableHeader']) for h in headers]
    data = [header_row]
    for row in rows:
        data.append([Paragraph(str(cell), styles['TableCell']) for cell in row])

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BG_CARD, BG_LIGHT]),
    ]))
    return t


# ─── Helper: metric card row ───

def metric_cards(styles, metrics):
    """metrics = list of (label, value) tuples"""
    minis = []
    for label, value in metrics:
        mini_data = [
            [Paragraph(str(value), styles['MetricValue'])],
            [Paragraph(label, styles['MetricLabel'])],
        ]
        mini = Table(mini_data, colWidths=[1.4 * inch], rowHeights=[36, 20])
        mini.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, BORDER_LIGHT),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ]))
        minis.append(mini)

    n = len(minis)
    cw = [6.7 * inch / n] * n
    row = Table([minis], colWidths=cw)
    row.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    return row


def section_header(story, styles, num, title):
    story.append(Paragraph(f"{num}. {title}", styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_LIGHT, spaceAfter=12))


def generate_report(
    output_path="automation_analysis_report.pdf",
    client_name="[Client Name]",
    client_industry="[Industry]",
):
    date_str = datetime.date.today().strftime("%B %d, %Y")
    styles = create_styles()

    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        topMargin=0.75 * inch, bottomMargin=0.85 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    )

    story = []

    # ═══════════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════════
    story.append(Spacer(1, 2.0 * inch))
    story.append(Paragraph("✦  NEXLIFY", styles['BrandMark']))
    story.append(Paragraph("Business Automation<br/>Analysis Report", styles['ReportTitle']))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="30%", thickness=2, color=PRIMARY, spaceAfter=24, spaceBefore=8, hAlign='CENTER'))
    story.append(Paragraph(f"Prepared for: {client_name}", styles['CoverClient']))
    story.append(Paragraph(f"Industry: {client_industry}", styles['CoverDate']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Date: {date_str}", styles['CoverDate']))
    story.append(Paragraph("Prepared by: Nexlify Limited LLC", styles['CoverDate']))
    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph(
        "CONFIDENTIAL — This report is intended solely for the use of the named client. "
        "Reproduction or distribution without written consent from Nexlify Limited LLC is prohibited.",
        styles['Confidential']
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # TABLE OF CONTENTS
    # ═══════════════════════════════════════════
    story.append(Paragraph("Table of Contents", styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_LIGHT, spaceAfter=16))
    toc = [
        "1. Executive Summary",
        "2. Organization Overview &amp; Current Workflows",
        "3. Automation Opportunity Assessment",
        "4. Workflow-by-Workflow Analysis",
        "5. Estimated Time &amp; Cost Savings",
        "6. Recommended Automation Stack",
        "7. Implementation Roadmap",
        "8. Risk Considerations",
        "9. Investment &amp; ROI Projection",
        "10. Next Steps",
    ]
    for item in toc:
        story.append(Paragraph(item, ParagraphStyle('TOCItem', parent=styles['BodyText2'],
                                                      fontSize=11, spaceBefore=6, spaceAfter=6,
                                                      textColor=TEXT_DARK)))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 1. EXECUTIVE SUMMARY
    # ═══════════════════════════════════════════
    section_header(story, styles, 1, "Executive Summary")
    story.append(Paragraph(
        f"Nexlify conducted a comprehensive analysis of <b>{client_name}</b>'s core business operations "
        f"to identify tasks and workflows that can be automated using AI, integration platforms, and "
        f"intelligent systems. This report maps every major workflow, scores each for automation potential, "
        f"and provides a prioritized roadmap for implementation.",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Our analysis uncovered significant opportunities to reduce manual effort, eliminate bottlenecks, "
        "and free up your team to focus on high-value strategic work. Key findings are summarized below.",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 12))

    story.append(metric_cards(styles, [
        ("Workflows Analyzed", "[X]"),
        ("Automatable Tasks", "[X]"),
        ("Est. Hours Saved / Mo", "[X]"),
        ("Est. Monthly Savings", "$[X]"),
    ]))
    story.append(Spacer(1, 16))

    # Key findings summary box
    kf_data = [
        [Paragraph("<b>Key Findings</b>", ParagraphStyle('kf', fontName='Helvetica-Bold',
                                                           fontSize=12, textColor=PRIMARY))],
        [Paragraph(
            "•  [X]% of current workflows contain tasks suitable for full or partial automation<br/>"
            "•  The largest time savings opportunity is in [department/function]<br/>"
            "•  [X] workflows can be automated within 2 weeks using existing tools<br/>"
            "•  Estimated ROI payback period: [X] months",
            ParagraphStyle('kfb', parent=styles['BodyText2'], leftIndent=12, leading=18)
        )],
    ]
    kf = Table(kf_data, colWidths=[6.7 * inch])
    kf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SECTION_BG),
        ('BOX', (0, 0), (-1, -1), 1, PRIMARY),
        ('TOPPADDING', (0, 0), (0, 0), 12),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
    ]))
    story.append(kf)
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 2. ORGANIZATION OVERVIEW
    # ═══════════════════════════════════════════
    section_header(story, styles, 2, "Organization Overview &amp; Current Workflows")
    story.append(Paragraph(
        "This section documents the client's current operational structure, key departments, "
        "team size, and the primary tools and platforms in use.",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Company Profile", styles['SubHeader']))
    profile_rows = [
        ["Company Name", f"{client_name}"],
        ["Industry", f"{client_industry}"],
        ["Team Size", "[X employees / contractors]"],
        ["Primary Revenue Model", "[e.g., SaaS, services, e-commerce]"],
        ["Current Tech Stack", "[e.g., Google Workspace, Slack, QuickBooks, Shopify]"],
        ["CRM / Sales Tools", "[e.g., HubSpot, Salesforce, spreadsheets]"],
        ["Project Management", "[e.g., Asana, Trello, Notion, none]"],
    ]
    pt = Table(
        [[Paragraph(f"<b>{r[0]}</b>", styles['TableCell']),
          Paragraph(r[1], styles['TableCell'])] for r in profile_rows],
        colWidths=[2.2 * inch, 4.5 * inch]
    )
    pt.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ('BACKGROUND', (0, 0), (0, -1), BG_LIGHT),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(pt)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Current Workflow Map", styles['SubHeader']))
    story.append(Paragraph(
        "Below is a high-level inventory of the organization's core workflows. "
        "Each workflow was assessed during our discovery process through interviews, tool audits, and process observation.",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 6))

    workflow_map = make_table(styles,
        ["Workflow", "Owner / Dept", "Frequency", "Current Method", "Est. Time / Week"],
        [
            ["Lead capture &amp; follow-up", "[Sales]", "Daily", "[Manual email]", "[X] hrs"],
            ["Invoice creation &amp; sending", "[Finance]", "Weekly", "[QuickBooks manual]", "[X] hrs"],
            ["Social media posting", "[Marketing]", "Daily", "[Manual posting]", "[X] hrs"],
            ["Client onboarding", "[Operations]", "Per client", "[Email + docs]", "[X] hrs"],
            ["Appointment scheduling", "[Admin]", "Daily", "[Phone / email]", "[X] hrs"],
            ["Data entry &amp; reporting", "[Operations]", "Weekly", "[Spreadsheets]", "[X] hrs"],
            ["Customer support triage", "[Support]", "Daily", "[Email inbox]", "[X] hrs"],
            ["Employee time tracking", "[HR]", "Daily", "[Manual / honor]", "[X] hrs"],
            ["[Add more as discovered]", "[Dept]", "[Freq]", "[Method]", "[X] hrs"],
        ],
        [1.7 * inch, 1.1 * inch, 0.9 * inch, 1.5 * inch, 1.1 * inch]
    )
    story.append(workflow_map)
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 3. AUTOMATION OPPORTUNITY ASSESSMENT
    # ═══════════════════════════════════════════
    section_header(story, styles, 3, "Automation Opportunity Assessment")
    story.append(Paragraph(
        "Each workflow was scored on three dimensions to determine automation priority. "
        "The Automation Score (out of 10) combines these factors into a single ranking.",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 6))

    # Scoring criteria explanation
    criteria_data = [
        [Paragraph("<b>Criteria</b>", styles['TableHeader']),
         Paragraph("<b>What It Measures</b>", styles['TableHeader']),
         Paragraph("<b>Weight</b>", styles['TableHeader'])],
        [Paragraph("Repetitiveness", styles['TableCell']),
         Paragraph("How rule-based and predictable is the task?", styles['TableCell']),
         Paragraph("40%", styles['TableCellCenter'])],
        [Paragraph("Time Impact", styles['TableCell']),
         Paragraph("How many hours per month does this consume?", styles['TableCell']),
         Paragraph("35%", styles['TableCellCenter'])],
        [Paragraph("Error Risk", styles['TableCell']),
         Paragraph("How often do manual errors cause rework or lost revenue?", styles['TableCell']),
         Paragraph("25%", styles['TableCellCenter'])],
    ]
    ct = Table(criteria_data, colWidths=[1.5 * inch, 3.7 * inch, 1.0 * inch], repeatRows=1)
    ct.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BG_CARD, BG_LIGHT]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(ct)
    story.append(Spacer(1, 16))

    # Scored workflows
    story.append(Paragraph("Automation Scores by Workflow", styles['SubHeader']))

    def score_cell(score_str, styles):
        """Return a colored paragraph for the score."""
        try:
            val = float(score_str)
            if val >= 8:
                color = ACCENT_GREEN
            elif val >= 5:
                color = ACCENT_YELLOW
            else:
                color = ACCENT_RED
        except ValueError:
            color = TEXT_LIGHT
        return Paragraph(
            f"<font color='#{color.hexval()}'><b>{score_str}</b></font>",
            styles['TableCellCenter']
        )

    score_headers = [
        Paragraph("Workflow", styles['TableHeader']),
        Paragraph("Repetitive", styles['TableHeader']),
        Paragraph("Time Impact", styles['TableHeader']),
        Paragraph("Error Risk", styles['TableHeader']),
        Paragraph("Score", styles['TableHeader']),
        Paragraph("Priority", styles['TableHeader']),
    ]
    score_rows_data = [
        ("Lead follow-up emails", "9", "8", "6", "8.1", "High"),
        ("Invoice generation", "9", "7", "8", "8.0", "High"),
        ("Social media scheduling", "10", "7", "3", "7.5", "High"),
        ("Appointment booking", "10", "6", "4", "7.2", "High"),
        ("Client onboarding docs", "7", "7", "7", "7.0", "Medium"),
        ("Data entry &amp; reporting", "8", "6", "8", "7.2", "High"),
        ("Support ticket triage", "7", "6", "5", "6.2", "Medium"),
        ("Time tracking", "6", "4", "5", "5.0", "Medium"),
        ("[Additional workflow]", "[X]", "[X]", "[X]", "[X]", "[Priority]"),
    ]

    score_data = [score_headers]
    for wf, rep, time_i, err, total, priority in score_rows_data:
        p_color = {"High": ACCENT_RED, "Medium": ACCENT_YELLOW, "Low": ACCENT_GREEN}.get(priority, TEXT_LIGHT)
        score_data.append([
            Paragraph(wf, styles['TableCell']),
            Paragraph(rep, styles['TableCellCenter']),
            Paragraph(time_i, styles['TableCellCenter']),
            Paragraph(err, styles['TableCellCenter']),
            score_cell(total, styles),
            Paragraph(
                f"<font color='#{p_color.hexval()}'><b>{priority}</b></font>",
                styles['TableCellCenter']
            ),
        ])

    st = Table(score_data, colWidths=[1.8 * inch, 0.85 * inch, 0.85 * inch, 0.85 * inch, 0.75 * inch, 0.85 * inch],
               repeatRows=1)
    st.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BG_CARD, BG_LIGHT]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(st)
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 4. WORKFLOW-BY-WORKFLOW ANALYSIS
    # ═══════════════════════════════════════════
    section_header(story, styles, 4, "Workflow-by-Workflow Analysis")
    story.append(Paragraph(
        "This section provides a detailed breakdown of each high-priority workflow: "
        "what it looks like today, what it could look like automated, and the specific tools involved.",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 8))

    workflows_detail = [
        {
            "name": "Lead Follow-Up Emails",
            "current": "Sales team manually checks new leads in [CRM/spreadsheet], writes individual follow-up emails, and tracks responses in a separate doc. Average response time: [X] hours.",
            "automated": "New leads trigger an instant personalized email sequence via Mailchimp/ConvertKit. AI scores lead quality. Hot leads get routed to sales rep with context. Cold leads enter a nurture drip.",
            "tools": "Zapier, Mailchimp/ConvertKit, AI lead scoring, CRM integration",
            "time_saved": "[X] hrs/week",
        },
        {
            "name": "Invoice Generation &amp; Sending",
            "current": "Finance manually creates invoices in [tool], copies client details, calculates totals, and sends via email. Payment follow-ups are done manually.",
            "automated": "Invoices auto-generate when a project is marked complete or on a recurring schedule. Payment reminders sent automatically. Overdue alerts escalate to the team.",
            "tools": "QuickBooks/Stripe API, Zapier/Make.com, email automation",
            "time_saved": "[X] hrs/week",
        },
        {
            "name": "Social Media Scheduling",
            "current": "Marketing team manually logs into each platform, creates posts, and publishes one at a time. No consistent posting schedule.",
            "automated": "Content calendar managed in Notion/Airtable. Posts auto-scheduled via Buffer/Later. AI assists with caption generation and hashtag research.",
            "tools": "Buffer/Later, Notion, ChatGPT API, Zapier",
            "time_saved": "[X] hrs/week",
        },
        {
            "name": "Client Onboarding",
            "current": "New clients receive a manual welcome email. Documents are sent individually. Intake forms are handled via back-and-forth email.",
            "automated": "New client added to CRM triggers a full onboarding sequence: welcome email, intake form (Typeform), document sharing (Google Drive), and kickoff meeting scheduling (Calendly).",
            "tools": "Zapier/Make.com, Typeform, Calendly, Google Drive, CRM",
            "time_saved": "[X] hrs/client",
        },
    ]

    for wf in workflows_detail:
        wf_header = Table(
            [[Paragraph(f"  {wf['name']}", ParagraphStyle('wfh', fontName='Helvetica-Bold',
                                                            fontSize=12, textColor=white))]],
            colWidths=[6.7 * inch], rowHeights=[30]
        )
        wf_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(KeepTogether([
            wf_header,
            Spacer(1, 4),
            Paragraph("<b>Current Process:</b>", styles['BodyText2']),
            Paragraph(wf['current'], ParagraphStyle('wfc', parent=styles['BodyText2'], leftIndent=12)),
            Spacer(1, 4),
            Paragraph("<b>Automated Process:</b>", styles['BodyText2']),
            Paragraph(wf['automated'], ParagraphStyle('wfa', parent=styles['BodyText2'], leftIndent=12,
                                                        textColor=ACCENT_GREEN)),
            Spacer(1, 4),
            Paragraph(f"<b>Recommended Tools:</b> {wf['tools']}", styles['BodyText2']),
            Paragraph(f"<b>Estimated Time Saved:</b> {wf['time_saved']}", styles['BodyText2']),
            Spacer(1, 16),
        ]))

    story.append(Paragraph(
        "<i>[Repeat this section for each additional workflow identified during discovery.]</i>",
        styles['BodyText2']
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 5. TIME &amp; COST SAVINGS
    # ═══════════════════════════════════════════
    section_header(story, styles, 5, "Estimated Time &amp; Cost Savings")
    story.append(Paragraph(
        "The table below projects monthly time and cost savings based on current labor costs "
        "and the estimated reduction in manual effort after automation.",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 8))

    savings_table = make_table(styles,
        ["Workflow", "Current Hrs/Mo", "Post-Automation", "Hours Saved", "Cost Saved/Mo"],
        [
            ["Lead follow-up", "[X]", "[X]", "[X]", "$[X]"],
            ["Invoicing", "[X]", "[X]", "[X]", "$[X]"],
            ["Social media", "[X]", "[X]", "[X]", "$[X]"],
            ["Client onboarding", "[X]", "[X]", "[X]", "$[X]"],
            ["Data entry &amp; reporting", "[X]", "[X]", "[X]", "$[X]"],
            ["Appointment scheduling", "[X]", "[X]", "[X]", "$[X]"],
            ["Support triage", "[X]", "[X]", "[X]", "$[X]"],
            ["[Other]", "[X]", "[X]", "[X]", "$[X]"],
        ],
        [1.8 * inch, 1.1 * inch, 1.1 * inch, 1.1 * inch, 1.2 * inch]
    )
    story.append(savings_table)
    story.append(Spacer(1, 12))

    # Totals box
    totals_data = [
        [Paragraph("<b>Total Monthly Hours Saved</b>", styles['TableCell']),
         Paragraph("<b>[X] hours</b>", ParagraphStyle('tv', fontName='Helvetica-Bold',
                                                        fontSize=11, textColor=ACCENT_GREEN, alignment=TA_RIGHT))],
        [Paragraph("<b>Total Monthly Cost Savings</b>", styles['TableCell']),
         Paragraph("<b>$[X,XXX]</b>", ParagraphStyle('tv2', fontName='Helvetica-Bold',
                                                       fontSize=11, textColor=ACCENT_GREEN, alignment=TA_RIGHT))],
        [Paragraph("<b>Annual Projected Savings</b>", styles['TableCell']),
         Paragraph("<b>$[XX,XXX]</b>", ParagraphStyle('tv3', fontName='Helvetica-Bold',
                                                        fontSize=11, textColor=PRIMARY, alignment=TA_RIGHT))],
    ]
    totals = Table(totals_data, colWidths=[4.0 * inch, 2.7 * inch])
    totals.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SECTION_BG),
        ('BOX', (0, 0), (-1, -1), 1.5, PRIMARY),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(totals)
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<i>* Cost savings calculated using an estimated hourly rate of $[X]/hr for manual labor.</i>",
        ParagraphStyle('fn', parent=styles['BodyText2'], fontSize=8, textColor=TEXT_LIGHT)
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 6. RECOMMENDED AUTOMATION STACK
    # ═══════════════════════════════════════════
    section_header(story, styles, 6, "Recommended Automation Stack")
    story.append(Paragraph(
        "Based on your existing tools, budget, and technical capacity, we recommend the following "
        "automation stack. All tools integrate with each other and can be managed without a developer.",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 8))

    stack_table = make_table(styles,
        ["Category", "Tool", "Purpose", "Est. Cost/Mo"],
        [
            ["Workflow Orchestration", "Zapier / Make.com", "Connect apps and automate multi-step workflows", "$20-$70"],
            ["Email Automation", "Mailchimp / ConvertKit", "Drip sequences, follow-ups, newsletters", "$0-$30"],
            ["Scheduling", "Calendly", "Automated appointment booking", "$0-$12"],
            ["AI Chatbot", "Tidio / Intercom / Custom", "24/7 lead qualification and support", "$0-$50"],
            ["Forms &amp; Intake", "Typeform / Tally", "Client onboarding and data collection", "$0-$25"],
            ["CRM", "HubSpot Free / Notion", "Contact management and pipeline tracking", "$0"],
            ["Social Scheduling", "Buffer / Later", "Batch-schedule social content", "$0-$15"],
            ["AI Content Assist", "ChatGPT API / Claude API", "Draft emails, captions, reports", "$5-$20"],
        ],
        [1.4 * inch, 1.5 * inch, 2.5 * inch, 1.0 * inch]
    )
    story.append(stack_table)
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Estimated Total Tool Cost:</b> $[X] - $[X] / month (many tools have free tiers to start)",
        styles['BodyText2']
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 7. IMPLEMENTATION ROADMAP
    # ═══════════════════════════════════════════
    section_header(story, styles, 7, "Implementation Roadmap")
    story.append(Paragraph(
        "We recommend a phased rollout to minimize disruption and allow your team to adapt gradually.",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 8))

    phases = [
        ("Phase 1: Quick Wins (Week 1-2)", ACCENT_GREEN, [
            "Set up Calendly for automated scheduling — eliminate back-and-forth emails",
            "Connect lead capture form to email automation (instant follow-up sequence)",
            "Set up social media scheduling tool — batch one week of content",
            "Estimated effort: 4-6 hours of setup",
        ]),
        ("Phase 2: Core Automation (Week 3-4)", ACCENT_YELLOW, [
            "Build Zapier/Make.com workflows for invoicing and client onboarding",
            "Deploy AI chatbot on website for lead qualification",
            "Set up automated reporting dashboards",
            "Estimated effort: 8-12 hours of setup",
        ]),
        ("Phase 3: Advanced Optimization (Month 2)", ACCENT_BLUE, [
            "Integrate AI content generation for social media and email",
            "Connect all tools into a unified dashboard (e.g., Notion or Airtable)",
            "Train team on new automated workflows and monitor performance",
            "Establish KPIs and automation performance tracking",
            "Estimated effort: 10-16 hours of setup",
        ]),
    ]

    for phase_title, phase_color, bullets in phases:
        phase_header = Table(
            [[Paragraph(f"  {phase_title}", ParagraphStyle('ph', fontName='Helvetica-Bold',
                                                             fontSize=11, textColor=white))]],
            colWidths=[6.7 * inch], rowHeights=[28]
        )
        phase_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), phase_color),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ]))
        bullet_items = [Paragraph(f"• {b}", styles['BulletItem']) for b in bullets]
        story.append(KeepTogether([
            phase_header,
            Spacer(1, 4),
            *bullet_items,
            Spacer(1, 12),
        ]))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 8. RISK CONSIDERATIONS
    # ═══════════════════════════════════════════
    section_header(story, styles, 8, "Risk Considerations")
    story.append(Paragraph(
        "Automation brings significant benefits, but it is important to plan for potential risks. "
        "Below are common challenges and our recommended mitigation strategies.",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 8))

    risk_table = make_table(styles,
        ["Risk", "Likelihood", "Impact", "Mitigation Strategy"],
        [
            ["Over-automation without human oversight", "Medium", "High",
             "Build in human review checkpoints for critical decisions"],
            ["Tool/API changes breaking workflows", "Medium", "Medium",
             "Use reputable platforms with SLA guarantees; monitor regularly"],
            ["Team resistance to new systems", "Medium", "Medium",
             "Involve staff early; provide training and clear documentation"],
            ["Data privacy and compliance issues", "Low", "High",
             "Review GDPR/CCPA requirements; use compliant tools only"],
            ["Cost overrun on tool subscriptions", "Low", "Medium",
             "Start with free tiers; scale only after ROI is confirmed"],
            ["Integration failures between platforms", "Medium", "Medium",
             "Test all Zaps/workflows in staging before going live"],
        ],
        [1.8 * inch, 0.9 * inch, 0.7 * inch, 2.9 * inch]
    )
    story.append(risk_table)
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Note:</b> All automation workflows should be monitored for at least 30 days after launch "
        "to catch edge cases and ensure reliability before reducing human oversight.",
        ParagraphStyle('note', parent=styles['BodyText2'], leftIndent=12, textColor=TEXT_MED)
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 9. INVESTMENT &amp; ROI PROJECTION
    # ═══════════════════════════════════════════
    section_header(story, styles, 9, "Investment &amp; ROI Projection")
    story.append(Paragraph(
        "The following projection outlines the expected investment in automation setup and tooling "
        "versus the projected monthly savings, illustrating the return on investment timeline.",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Investment Breakdown", styles['SubHeader']))
    investment_table = make_table(styles,
        ["Item", "Type", "Est. Cost"],
        [
            ["Automation strategy &amp; setup (Nexlify)", "One-time", "$[X,XXX]"],
            ["Tool subscriptions (monthly)", "Recurring", "$[X] - $[X] / mo"],
            ["Staff training (hours × rate)", "One-time", "$[X]"],
            ["Ongoing maintenance / optimization", "Recurring", "$[X] / mo"],
        ],
        [2.8 * inch, 1.5 * inch, 2.0 * inch]
    )
    story.append(investment_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("ROI Summary", styles['SubHeader']))
    roi_data = [
        [Paragraph("<b>Metric</b>", styles['TableCell']),
         Paragraph("<b>Value</b>", styles['TableCell'])],
        [Paragraph("Total One-Time Investment", styles['TableCell']),
         Paragraph("$[X,XXX]", styles['TableCell'])],
        [Paragraph("Monthly Recurring Tool Cost", styles['TableCell']),
         Paragraph("$[X] / mo", styles['TableCell'])],
        [Paragraph("Estimated Monthly Savings", styles['TableCell']),
         Paragraph("<font color='#00b894'><b>$[X,XXX] / mo</b></font>", styles['TableCell'])],
        [Paragraph("Net Monthly Gain (after tools)", styles['TableCell']),
         Paragraph("<font color='#00b894'><b>$[X,XXX] / mo</b></font>", styles['TableCell'])],
        [Paragraph("Payback Period", styles['TableCell']),
         Paragraph("<font color='#6c5ce7'><b>[X] months</b></font>", styles['TableCell'])],
        [Paragraph("12-Month Net ROI", styles['TableCell']),
         Paragraph("<font color='#6c5ce7'><b>$[XX,XXX]</b></font>", styles['TableCell'])],
    ]
    roi_t = Table(roi_data, colWidths=[3.5 * inch, 2.9 * inch])
    roi_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BG_CARD, BG_LIGHT]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(roi_t)
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 10. NEXT STEPS
    # ═══════════════════════════════════════════
    section_header(story, styles, 10, "Next Steps")
    story.append(Paragraph(
        "We are ready to begin implementation as soon as you give the go-ahead. "
        "Here is how we recommend moving forward:",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 8))

    next_steps = [
        ("Review this report", "Share with your team and gather feedback on priorities and any workflows we may have missed."),
        ("Confirm scope &amp; budget", "Decide which phases you want to start with and confirm the budget for tooling and setup."),
        ("Sign the engagement agreement", "We will send over a proposal and agreement to formalize the project scope."),
        ("Kickoff discovery call", "A 60-minute call to finalize workflow details, access credentials, and set up a shared project workspace."),
        ("Phase 1 begins", "Nexlify sets up Phase 1 automations within the first week of the engagement."),
    ]

    for i, (step, desc) in enumerate(next_steps, 1):
        step_data = [
            [
                Paragraph(f"<b>{i}</b>", ParagraphStyle('sn', fontName='Helvetica-Bold',
                                                          fontSize=16, textColor=white, alignment=TA_CENTER)),
                Paragraph(f"<b>{step}</b><br/>{desc}",
                          ParagraphStyle('sd', parent=styles['BodyText2'], spaceBefore=0, spaceAfter=0))
            ]
        ]
        step_t = Table(step_data, colWidths=[0.5 * inch, 6.0 * inch], rowHeights=[40])
        step_t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), PRIMARY),
            ('BACKGROUND', (1, 0), (1, 0), SECTION_BG),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (0, 0), 8),
            ('RIGHTPADDING', (0, 0), (0, 0), 8),
            ('LEFTPADDING', (1, 0), (1, 0), 12),
            ('RIGHTPADDING', (1, 0), (1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ]))
        story.append(step_t)
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 20))

    # Closing CTA box
    cta_data = [
        [Paragraph(
            "Ready to automate your business?<br/>"
            "<font size='10'>Contact us at <b>hello@nexlifylimited.com</b> or book a call at "
            "<b>nexlifylimited.com</b></font>",
            ParagraphStyle('cta', fontName='Helvetica-Bold', fontSize=13, textColor=white,
                           alignment=TA_CENTER, leading=20)
        )]
    ]
    cta = Table(cta_data, colWidths=[6.7 * inch])
    cta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('LEFTPADDING', (0, 0), (-1, -1), 24),
        ('RIGHTPADDING', (0, 0), (-1, -1), 24),
        ('ROUNDEDCORNERS', [6]),
    ]))
    story.append(cta)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report generated: {output_path}")


if __name__ == "__main__":
    generate_report(
        output_path="automation_analysis_report.pdf",
        client_name="[Client Name]",
        client_industry="[Industry]",
    )
