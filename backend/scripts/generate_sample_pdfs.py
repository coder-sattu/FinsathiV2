"""Script to generate realistic sample PDF documents for reimbursement testing."""

import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def create_sample_pdf(file_path: Path, title: str, subtitle: str, lines: list[str]) -> None:
    """Generate a clean, professional PDF file with reportlab for test upload."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(file_path), pagesize=letter)
    
    # Header Banner
    c.setFillColorRGB(0.0, 0.32, 0.8) # Royal Blue #0052CC
    c.rect(0, 730, 612, 62, fill=True, stroke=False)
    
    c.setFillColorRGB(1.0, 1.0, 1.0)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, 755, title)
    c.setFont("Helvetica", 11)
    c.drawString(40, 738, subtitle)

    # Document Body
    c.setFillColorRGB(0.12, 0.16, 0.23) # Slate Text
    c.setFont("Helvetica", 11)
    y = 690
    for line in lines:
        if line.startswith("---"):
            c.setStrokeColorRGB(0.88, 0.91, 0.94)
            c.line(40, y, 572, y)
            y -= 15
        elif line.isupper() and ":" not in line:
            c.setFont("Helvetica-Bold", 12)
            c.setFillColorRGB(0.0, 0.32, 0.8)
            c.drawString(40, y, line)
            c.setFont("Helvetica", 11)
            c.setFillColorRGB(0.12, 0.16, 0.23)
            y -= 22
        else:
            c.drawString(40, y, line)
            y -= 20
            
    # Footer
    c.setStrokeColorRGB(0.88, 0.91, 0.94)
    c.line(40, 50, 572, 50)
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColorRGB(0.4, 0.45, 0.55)
    c.drawString(40, 35, "Official Sample Document for FinSaathi Reimbursement Testing · Page 1 of 1")
    c.save()


def generate_all_samples(target_dir: Path) -> dict[str, Path]:
    """Generate 7 test reimbursement PDFs."""
    target_dir.mkdir(parents=True, exist_ok=True)
    generated = {}

    # 1. Signed Claim Form
    f1 = target_dir / "01_Signed_Claim_Form.pdf"
    create_sample_pdf(
        f1,
        "HEALTH INSURANCE CLAIM FORM (PART A & B)",
        "FinSaathi Claims Intimation Reference Form",
        [
            "PATIENT & POLICY DETAILS",
            "---",
            "Policy Number: HP-RET-2026-0011",
            "Policyholder Name: Neha Shah",
            "Patient Name: Neha Shah",
            "Relationship: SELF",
            "Mobile Number: 9000000011",
            "Email: neha.shah@example.com",
            "",
            "HOSPITALIZATION DETAILS",
            "---",
            "Hospital Name: Lilavati Hospital & Research Centre",
            "Hospital Pincode: 400050 (Bandra West, Mumbai)",
            "Date of Admission: 24/09/2026",
            "Date of Discharge: 27/09/2026",
            "Total Claim Amount Claimed: Rs. 142,500",
            "",
            "DECLARATION & SIGNATURE",
            "---",
            "I hereby declare that all information supplied is true and accurate.",
            "Signature: [Signed by Neha Shah]",
        ],
    )
    generated["claim_form"] = f1

    # 2. Discharge Summary (Matching)
    f2 = target_dir / "02_Discharge_Summary.pdf"
    create_sample_pdf(
        f2,
        "LILAVATI HOSPITAL & RESEARCH CENTRE",
        "Discharge Summary · Inpatient Department",
        [
            "PATIENT RECORD",
            "---",
            "Patient Name: Neha Shah",
            "IPD No: IPD-2026-99214",
            "Age / Gender: 37 Yrs / Female",
            "Date of Admission: 24/09/2026",
            "Date of Discharge: 27/09/2026",
            "Treating Consultant: Dr. Deshmukh (M.S., General Surgery)",
            "",
            "CLINICAL SUMMARY",
            "---",
            "Final Diagnosis: Acute Appendicitis (ICD Code: D101)",
            "Surgical Procedure: Laparoscopic Appendectomy performed on 24/09/2026",
            "Treatment Given: IV Antibiotics, Analgesics, Surgical Resection",
            "Condition at Discharge: Hemodynamically stable, afebrile, wound clean",
        ],
    )
    generated["discharge_summary"] = f2

    # 3. Final Hospital Bill
    f3 = target_dir / "03_Final_Hospital_Bill.pdf"
    create_sample_pdf(
        f3,
        "FINAL CONSOLIDATED HOSPITAL BILL",
        "Bill No: INV-2026-8812 · GSTIN: 27AAAAA0000A1Z5",
        [
            "BILLING BREAKDOWN",
            "---",
            "Patient Name: Neha Shah",
            "Bill Date: 27/09/2026",
            "Room Rent (Single Private A/C 3 Days @ Rs. 8,000): Rs. 24,000",
            "ICU & Nursing Charges: Rs. 18,000",
            "Surgeon & OT Charges (Laparoscopic Appendectomy): Rs. 65,000",
            "Anaesthetist Charges: Rs. 15,000",
            "Medicines & Consumables: Rs. 14,500",
            "Diagnostic & Lab Investigation Reports: Rs. 6,000",
            "---",
            "TOTAL NET AMOUNT PAYABLE: Rs. 142,500",
            "Payment Status: PAID IN FULL BY CASH / CARD",
        ],
    )
    generated["hospital_bill"] = f3

    # 4. Payment Receipts
    f4 = target_dir / "04_Payment_Receipts.pdf"
    create_sample_pdf(
        f4,
        "OFFICIAL HOSPITAL PAYMENT RECEIPT",
        "Receipt No: RCP-2026-4412",
        [
            "RECEIPT ACKNOWLEDGEMENT",
            "---",
            "Received with thanks from: Neha Shah",
            "Amount Received: Rs. 142,500 (Rupees One Lakh Forty Two Thousand Five Hundred Only)",
            "Payment Mode: Credit Card / HDFC NetBanking",
            "Transaction Ref: TXN9988221104",
            "Payment Date: 27/09/2026",
            "Seal & Signature: [Lilavati Hospital Accounts Dept]",
        ],
    )
    generated["payment_receipt"] = f4

    # 5. Cancelled Cheque / Bank Details
    f5 = target_dir / "05_Cancelled_Cheque_Bank.pdf"
    create_sample_pdf(
        f5,
        "BANK ACCOUNT PROOF - CANCELLED CHEQUE",
        "Direct Benefit Transfer Verification",
        [
            "BANK DETAILS",
            "---",
            "Account Holder Name: Neha Shah",
            "Bank Name: HDFC Bank",
            "Branch: Bandra West Branch, Mumbai",
            "Account Number: 50100299881144",
            "IFSC Code: HDFC0000012",
            "MICR Code: 400240002",
            "Status: CANCELLED FOR VERIFICATION",
        ],
    )
    generated["cancelled_cheque"] = f5

    # 6. Prescription / Photo ID
    f6 = target_dir / "06_Prescription_Photo_ID.pdf"
    create_sample_pdf(
        f6,
        "PRESCRIPTION & PHOTO ID PROOF",
        "Medical Doctor Prescription Copy",
        [
            "PRESCRIPTION DETAILS",
            "---",
            "Prescription Date: 24/09/2026",
            "Doctor Name: Dr. Verma",
            "Rx: Tab Paracetamol 650mg, Inj Pantoprazole",
            "Document Type: PRESCRIPTION",
        ],
    )
    generated["photo_id"] = f6
    generated["prescription"] = f6

    # 7. Discharge Summary Mismatch Patient (John Doe vs Rahul Sharma)
    f7 = target_dir / "07_Discharge_Summary_Mismatch_Patient.pdf"
    create_sample_pdf(
        f7,
        "LILAVATI HOSPITAL - DISCHARGE SUMMARY (MISMATCH PATIENT)",
        "Gemini Document AI Validation Test",
        [
            "PATIENT RECORD (MISMATCH TEST)",
            "---",
            "Patient Name: John Doe",
            "DOA: 24/09/2026",
            "Diagnosis: Viral Fever",
        ],
    )
    generated["mismatch_patient"] = f7

    # 8. Discharge Summary Mismatch DOA (2026-01-01 vs 2026-09-20)
    f8 = target_dir / "08_Discharge_Summary_Mismatch_DOA.pdf"
    create_sample_pdf(
        f8,
        "LILAVATI HOSPITAL - DISCHARGE SUMMARY (MISMATCH DOA)",
        "Gemini Document AI Validation Test",
        [
            "PATIENT RECORD (MISMATCH TEST)",
            "---",
            "Patient Name: Rahul Sharma",
            "DOA: 2026-01-01",
            "Diagnosis: Appendicitis",
        ],
    )
    generated["mismatch_doa"] = f8

    return generated


if __name__ == "__main__":
    out_dir = Path(__file__).parent.parent / "sample_docs"
    res = generate_all_samples(out_dir)
    print(f"Generated {len(res)} sample test PDFs in {out_dir.resolve()}:")
    for p in res:
        print(f" - {p.name}")
