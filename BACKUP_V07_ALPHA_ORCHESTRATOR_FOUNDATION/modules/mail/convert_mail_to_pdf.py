import os
from fpdf import FPDF

def convert_mail_to_pdf(email_text: str, subject: str, sender: str, date: str) -> str:
    """
    Wandelt den E-Mail-Text in ein PDF um und gibt den Dateipfad zurück.
    
    Args:
        email_text (str): Der Text der E-Mail.
        subject (str): Der Betreff der E-Mail.
        sender (str): Der Absender der E-Mail.
        date (str): Das Datum der E-Mail.
    
    Returns:
        str: Der Dateipfad des generierten PDFs.
    """
    # Erstelle ein PDF-Dokument
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Füge E-Mail-Metadaten hinzu
    pdf.cell(200, 10, txt=f"Betreff: {subject}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Von: {sender}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Datum: {date}", ln=True, align='L')
    pdf.ln(10)  # Leerzeile
    pdf.multi_cell(0, 10, txt=email_text)

    # Sicheren Dateinamen erstellen
    safe_subject = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in subject)
    file_path = f"/tmp/{safe_subject.replace(' ', '_')}_email.pdf"

    # PDF speichern
    pdf.output(file_path)
    return file_path