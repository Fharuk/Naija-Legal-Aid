from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import datetime

class LegalDocBuilder:
    """
    Generates .docx files for legal correspondence locally.
    """
    
    @staticmethod
    def generate_letter(user_name: str, letter_data: dict) -> io.BytesIO:
        doc = Document()
        
        # Styling
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Times New Roman'
        font.size = Pt(12)

        # Date
        today = datetime.date.today().strftime("%B %d, %Y")
        p = doc.add_paragraph(today)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # Address Block
        doc.add_paragraph(f"To: {letter_data.get('recipient_type', 'Recipient')}")
        doc.add_paragraph("[Address - Please Fill Manually]")
        doc.add_paragraph("")
        
        # Salutation
        doc.add_paragraph("Dear Sir/Madam,")
        
        # Body
        doc.add_paragraph(f"SUBJECT: FORMAL NOTICE REGARDING {letter_data.get('recipient_type', 'LEGAL MATTER').upper()}")
        
        body_text = letter_data.get('formal_body', 'Content missing.')
        doc.add_paragraph(body_text)
        
        # Sign-off
        doc.add_paragraph("")
        doc.add_paragraph("Yours faithfully,")
        doc.add_paragraph("")
        doc.add_paragraph(user_name)
        
        # Output to memory buffer
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer