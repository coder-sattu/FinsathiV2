"""Script to generate all required PDF sample documents for all patient profiles (Neha Shah, Rohan Kulkarni, Priya Deshmukh)."""

import os
import shutil
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def create_pdf(filepath: str, title: str, subtitle: str, data_rows: list[tuple[str, str]], footer_note: str = ""):
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0052CC'),
        fontName='Helvetica-Bold',
        alignment=0,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#475569'),
        fontName='Helvetica',
        alignment=0,
        spaceAfter=12
    )

    cell_label_style = ParagraphStyle(
        'CellLabel',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#334155'),
        fontName='Helvetica-Bold'
    )

    cell_val_style = ParagraphStyle(
        'CellVal',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0F172A'),
        fontName='Helvetica'
    )

    footer_style = ParagraphStyle(
        'DocFooter',
        parent=styles['Italic'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748B'),
        alignment=1,
        spaceBefore=15
    )

    elements = []
    
    # Header
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(subtitle, subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0052CC'), spaceAfter=15))

    # Data Table
    table_data = []
    for label, val in data_rows:
        table_data.append([
            Paragraph(label, cell_label_style),
            Paragraph(val, cell_val_style)
        ])

    t = Table(table_data, colWidths=[180, 360])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=10, spaceAfter=10))
    
    note_text = footer_note or "Official Sample Document for FinSaathi Health Insurance Claim Testing"
    elements.append(Paragraph(note_text, footer_style))

    doc.build(elements)


def get_profile_docs(patient_name, policy_no, rmn, uhid, email, hospital_name, pincode, doa, dod, doctor_name, diagnosis, diagnosis_code, amount, bank_name, ifsc):
    return [
        (
            "01_Signed_Claim_Form.pdf",
            "HEALTH INSURANCE CLAIM FORM (PART A & B)",
            f"FinSaathi Claims Intimation Form · Code: CLAIM_FORM · {patient_name}",
            [
                ("Policy Number", policy_no),
                ("Policyholder Name", patient_name),
                ("Patient Name", f"{patient_name} (UHID: {uhid})"),
                ("Relationship with Holder", "SELF"),
                ("Mobile Number", rmn),
                ("Email Address", email),
                ("Hospital Name", hospital_name),
                ("Hospital Pincode", pincode),
                ("Date of Admission", doa),
                ("Date of Discharge", dod),
                ("Total Claim Amount", f"Rs. {amount:,}"),
                ("Declaration & Signature", f"I hereby declare all supplied details are correct. [Signed by {patient_name}]"),
            ]
        ),
        (
            "02_Discharge_Summary.pdf",
            hospital_name.upper(),
            f"Discharge Summary · Inpatient Department · Code: DISCHARGE · {patient_name}",
            [
                ("Patient Name", patient_name),
                ("UHID / IPD No", f"{uhid} / IPD-2026-8819"),
                ("Age / Gender", "35 Yrs / Adult"),
                ("Date of Admission", doa),
                ("Date of Discharge", dod),
                ("Treating Consultant", doctor_name),
                ("Final Diagnosis", f"{diagnosis} (ICD Code: {diagnosis_code})"),
                ("Procedure / Treatment", f"Standard Medical Treatment & Inpatient Protocol for {diagnosis}"),
                ("Condition at Discharge", "Hemodynamically stable, afebrile, discharged with medication"),
            ]
        ),
        (
            "03_Final_Hospital_Bill.pdf",
            hospital_name.upper(),
            f"Final Consolidated Itemized Hospital Bill · Code: FINAL_BILL · {patient_name}",
            [
                ("Patient Name", patient_name),
                ("Bill Number / Date", f"INV-2026-9011 / {dod}"),
                ("Room Rent & Nursing Charges", f"Rs. {int(amount * 0.3):,}"),
                ("Consultation & OT Charges", f"Rs. {int(amount * 0.4):,}"),
                ("Medicines & Consumables", f"Rs. {int(amount * 0.2):,}"),
                ("Diagnostics & Lab Reports", f"Rs. {int(amount * 0.1):,}"),
                ("TOTAL NET AMOUNT PAYABLE", f"Rs. {amount:,} (PAID IN FULL)"),
            ]
        ),
        (
            "04_Payment_Receipts.pdf",
            hospital_name.upper(),
            f"Official Payment Acknowledgment Receipt · Code: RECEIPTS · {patient_name}",
            [
                ("Receipt Number", "RCP-2026-5120"),
                ("Receipt Date", dod),
                ("Received From", patient_name),
                ("Amount Paid", f"Rs. {amount:,}"),
                ("Payment Mode", "Credit Card / NetBanking"),
                ("Transaction Reference", "TXN9988221104"),
                ("Payment Status", "FULL SETTLEMENT RECEIVED"),
            ]
        ),
        (
            "05_Cancelled_Cheque_Bank.pdf",
            f"{bank_name.upper()} - CANCELLED CHEQUE PROOF",
            f"Direct Benefit Transfer (NEFT) Account Verification · Code: BANK · {patient_name}",
            [
                ("Account Holder Name", patient_name),
                ("Bank Name", bank_name),
                ("Branch Name", "Main Branch"),
                ("Account Number", "50100299881144"),
                ("IFSC Code", ifsc),
                ("Cheque Status", "CANCELLED FOR VERIFICATION"),
            ]
        ),
        (
            "06_Photo_ID_Proof.pdf",
            "GOVERNMENT PHOTO ID PROOF",
            f"Identity Verification Document · Code: ID_PROOF · {patient_name}",
            [
                ("Document Type", "Aadhaar / Driving Licence / Passport"),
                ("Full Name", patient_name),
                ("Verification Status", "VERIFIED & VALID"),
            ]
        ),
        (
            "07_Investigation_Reports.pdf",
            f"{hospital_name.upper()} LAB & DIAGNOSTIC REPORTS",
            f"Diagnostic Investigation Summary · Code: REPORTS · {patient_name}",
            [
                ("Patient Name", patient_name),
                ("UHID / Lab Ref", f"{uhid} / LAB-2026-5542"),
                ("Report Date", doa),
                ("Diagnostic Finding", f"Clinical investigation confirms {diagnosis}"),
                ("Lab Technician Sign", f"Verified by Chief Pathologist, {hospital_name}"),
            ]
        ),
        (
            "08_Pharmacy_Bills.pdf",
            f"{hospital_name.upper()} PHARMACY BILL",
            f"Inpatient Pharmacy & Prescription Breakdown · Code: PHARMACY · {patient_name}",
            [
                ("Patient Name", patient_name),
                ("Pharmacy Bill No", "PH-2026-8820"),
                ("Bill Date", dod),
                ("Total Pharmacy Amount", f"Rs. {int(amount * 0.15):,} (PAID IN FULL)"),
            ]
        ),
    ]


def generate_all_sample_docs():
    backend_dir = Path(r"d:\FinsathiV2\backend\sample_docs")
    root_dir = Path(r"d:\FinsathiV2\sample_docs")

    # Clean existing directories
    for target in [backend_dir, root_dir]:
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)

    print("Generating clean PDF sample documents for all patient profiles...")

    profiles = [
        {
            "folder_name": "Neha_Shah",
            "patient_name": "Neha Shah",
            "policy_no": "HP-RET-2026-0011",
            "rmn": "9000000011",
            "uhid": "UH1000000020",
            "email": "iamsatvashil@gmail.com",
            "hospital_name": "Lilavati Hospital & Research Centre",
            "pincode": "400050 (Bandra West, Mumbai)",
            "doa": "03/10/2026",
            "dod": "06/10/2026",
            "doctor_name": "Dr. Deshmukh (M.S., General Surgery)",
            "diagnosis": "Acute Appendicitis",
            "diagnosis_code": "D101",
            "amount": 142500,
            "bank_name": "HDFC Bank",
            "ifsc": "HDFC0000012"
        },
        {
            "folder_name": "Rohan_Kulkarni",
            "patient_name": "Rohan Kulkarni",
            "policy_no": "HP-RET-2026-0001",
            "rmn": "9000000001",
            "uhid": "UH1000000001",
            "email": "rohan.kulkarni@example.com",
            "hospital_name": "Jupiter Hospital",
            "pincode": "411045 (Baner, Pune)",
            "doa": "03/10/2026",
            "dod": "06/10/2026",
            "doctor_name": "Dr. K. N. Patil (MD, Medicine)",
            "diagnosis": "Dengue Fever",
            "diagnosis_code": "D103",
            "amount": 150000,
            "bank_name": "ICICI Bank",
            "ifsc": "ICIC0000102"
        },
        {
            "folder_name": "Priya_Deshmukh",
            "patient_name": "Priya Deshmukh",
            "policy_no": "HP-GRP-2026-0001",
            "rmn": "9000000002",
            "uhid": "UH1000000004",
            "email": "priya.deshmukh@example.com",
            "hospital_name": "Lilavati Hospital & Research Centre",
            "pincode": "400050 (Bandra West, Mumbai)",
            "doa": "03/10/2026",
            "dod": "06/10/2026",
            "doctor_name": "Dr. S. Mehta (MD)",
            "diagnosis": "Acute Appendicitis",
            "diagnosis_code": "D101",
            "amount": 150000,
            "bank_name": "Axis Bank",
            "ifsc": "UTIB0000210"
        }
    ]

    for p in profiles:
        print(f"\n--- Generating Profile Docs for {p['patient_name']} ({p['folder_name']}) ---")
        
        # Profile subfolders
        b_sub = backend_dir / p["folder_name"]
        r_sub = root_dir / p["folder_name"]
        b_sub.mkdir(parents=True, exist_ok=True)
        r_sub.mkdir(parents=True, exist_ok=True)

        docs = get_profile_docs(
            patient_name=p["patient_name"],
            policy_no=p["policy_no"],
            rmn=p["rmn"],
            uhid=p["uhid"],
            email=p["email"],
            hospital_name=p["hospital_name"],
            pincode=p["pincode"],
            doa=p["doa"],
            dod=p["dod"],
            doctor_name=p["doctor_name"],
            diagnosis=p["diagnosis"],
            diagnosis_code=p["diagnosis_code"],
            amount=p["amount"],
            bank_name=p["bank_name"],
            ifsc=p["ifsc"]
        )

        for filename, title, subtitle, rows in docs:
            # Generate in profile folder
            create_pdf(str(b_sub / filename), title, subtitle, rows)
            create_pdf(str(r_sub / filename), title, subtitle, rows)

            # Also generate at top-level for Neha Shah (default test profile)
            if p["folder_name"] == "Neha_Shah":
                create_pdf(str(backend_dir / filename), title, subtitle, rows)
                create_pdf(str(root_dir / filename), title, subtitle, rows)
            
            print(f"  [PDF Created] {p['folder_name']}/{filename}")

    # Create Mismatch test doc
    mismatch_filename = "09_Discharge_Summary_Mismatch_Warning.pdf"
    mismatch_title = "LILAVATI HOSPITAL - DISCHARGE SUMMARY (MISMATCH TEST)"
    mismatch_sub = "Gemini Document AI Validation Test · Code: MISMATCH"
    mismatch_rows = [
        ("Patient Name", "John Doe"),
        ("UHID / IPD No", "UH9999999999 / IPD-MISMATCH-01"),
        ("Date of Admission", "24/09/2026"),
        ("Diagnosis", "Viral Fever"),
        ("Note for Testing", "Uploading this document tests Gemini Doc AI Mismatch Warning Card in FinSaathi Bot."),
    ]
    create_pdf(str(backend_dir / mismatch_filename), mismatch_title, mismatch_sub, mismatch_rows)
    create_pdf(str(root_dir / mismatch_filename), mismatch_title, mismatch_sub, mismatch_rows)
    print(f"\n  [PDF Created] {mismatch_filename} (Mismatch warning card test)")

    print("\nAll patient profile sample documents generated successfully!")


if __name__ == "__main__":
    generate_all_sample_docs()
