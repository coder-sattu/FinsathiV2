"""Email service for sending claim intimation confirmation via SMTP."""

import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any
from app.core.config import settings


def _send_smtp_email_sync(subject: str, html_content: str, recipients: list[str]) -> bool:
    """Synchronous SMTP email sender."""
    sender_email = getattr(settings, "smtp_user", "team.finsathi@gmail.com") or "team.finsathi@gmail.com"
    smtp_server = getattr(settings, "smtp_server", "smtp.gmail.com") or "smtp.gmail.com"
    smtp_port = getattr(settings, "smtp_port", 587)
    smtp_password = getattr(settings, "smtp_password", "")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"FinSaathi Claim Team <{sender_email}>"
    msg["To"] = ", ".join(recipients)

    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.ehlo()
            if smtp_port == 587:
                server.starttls()
                server.ehlo()
            if smtp_password:
                server.login(sender_email, smtp_password)
            server.sendmail(sender_email, recipients, msg.as_string())
        print(f"[SMTP Email Success] Email sent to {recipients} for subject '{subject}'")
        return True
    except Exception as e:
        print(f"[SMTP Email Notice] Could not send email via SMTP (Server: {smtp_server}:{smtp_port}): {e}")
        return False


async def send_claim_confirmation_email(data: dict[str, Any], policy_no: str = "") -> bool:
    """Asynchronous non-blocking wrapper to send claim confirmation email when process ends."""
    try:
        claim_no = data.get("claim_no", "CLM_PENDING")
        sr_number = data.get("sr_number", "N/A")
        patient_block = data.get("patient_block", {})
        admission_block = data.get("admission_block", {})
        hospital_block = data.get("hospital_block", {})
        claim_type = data.get("claim_type", "CASHLESS")

        patient_name = patient_block.get("patient") or data.get("patient_name", "N/A")
        intimator_email = patient_block.get("intimator_email", "")
        doa = admission_block.get("doa") or data.get("doa", "N/A")
        doctor_name = admission_block.get("doctor_name", "N/A")
        diagnosis = admission_block.get("diagnosis", "N/A")
        hospital_name = hospital_block.get("hospital_name") or hospital_block.get("hospital_id", "N/A")
        approx_cost = hospital_block.get("approx_cost", 0)

        # Target recipient as requested: iamsatvashil@gmail.com
        target_recipients = ["iamsatvashil@gmail.com"]
        if intimator_email and "@" in intimator_email and intimator_email not in target_recipients:
            target_recipients.append(intimator_email)

        subject = f"FinSaathi Claim Intimation Details - {claim_no}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body {{ font-family: 'Segoe UI', Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #1e293b; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; padding: 28px; border: 1px solid #e2e8f0; }}
            .header {{ background: #0052cc; color: #ffffff; padding: 18px 24px; border-radius: 8px; text-align: center; font-size: 20px; font-weight: bold; }}
            .content {{ margin-top: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
            td {{ padding: 10px 12px; border-bottom: 1px solid #f1f5f9; font-size: 14px; }}
            td.label {{ font-weight: 600; color: #475569; width: 40%; }}
            td.value {{ color: #0f172a; font-weight: 500; }}
            .badge {{ background: #e0e7ff; color: #3730a3; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; display: inline-block; }}
            .footer {{ margin-top: 24px; text-align: center; font-size: 12px; color: #94a3b8; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              FinSaathi Health Insurance Claim Summary
            </div>
            <div class="content">
              <p>Dear Customer / Assessor,</p>
              <p>A new health insurance claim intimation has been successfully completed and registered via <strong>FinSaathi Claim Assist</strong>.</p>
              
              <table>
                <tr>
                  <td class="label">Claim Number</td>
                  <td class="value"><strong>{claim_no}</strong></td>
                </tr>
                <tr>
                  <td class="label">Service Request (SR)</td>
                  <td class="value">{sr_number}</td>
                </tr>
                <tr>
                  <td class="label">Policy Number</td>
                  <td class="value">{policy_no or data.get("policy_no", "N/A")}</td>
                </tr>
                <tr>
                  <td class="label">Claim Type</td>
                  <td class="value"><span class="badge">{claim_type}</span></td>
                </tr>
                <tr>
                  <td class="label">Patient Name</td>
                  <td class="value">{patient_name}</td>
                </tr>
                <tr>
                  <td class="label">Date of Admission</td>
                  <td class="value">{doa}</td>
                </tr>
                <tr>
                  <td class="label">Doctor Name</td>
                  <td class="value">{doctor_name}</td>
                </tr>
                <tr>
                  <td class="label">Diagnosis</td>
                  <td class="value">{diagnosis}</td>
                </tr>
                <tr>
                  <td class="label">Hospital</td>
                  <td class="value">{hospital_name}</td>
                </tr>
                <tr>
                  <td class="label">Estimated Cost</td>
                  <td class="value">₹{approx_cost:,.2f}</td>
                </tr>
              </table>

              <p style="margin-top: 20px; font-size: 13px; color: #64748B;">
                All verified information has been securely dispatched to the backend claims adjudication engine.
              </p>
            </div>
            <div class="footer">
              Sent by team.finsathi@gmail.com · FinSaathi AI Health Insurance Platform
            </div>
          </div>
        </body>
        </html>
        """

        # Run SMTP send in background thread so API response is never delayed
        asyncio.create_task(asyncio.to_thread(_send_smtp_email_sync, subject, html_body, target_recipients))
        return True
    except Exception as err:
        print("[Email Service Warning]:", err)
        return False
