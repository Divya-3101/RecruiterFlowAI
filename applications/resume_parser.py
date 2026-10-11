import os
import logging
import zipfile
import xml.etree.ElementTree as ET
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def extract_docx_text(file_path):
    """
    Extracts text from a DOCX file using standard library zipfile and XML parsing.
    Requires no external dependencies.
    """
    try:
        with zipfile.ZipFile(file_path) as doc:
            tree = ET.fromstring(doc.read("word/document.xml"))
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            text_nodes = tree.findall(".//w:t", ns)
            text = " ".join(node.text for node in text_nodes if node.text)
            return text
    except Exception as e:
        logger.warning(f"Could not extract text from DOCX file {file_path}: {e}")
        return ""


def extract_pdf_text(file_path):
    """
    Extracts text from a PDF file using pypdf.
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        logger.warning(f"Could not extract text from PDF file {file_path}: {e}")
        return ""


def extract_resume_text(file_path):
    """
    Extracts text from candidate resumes supporting PDF, DOCX, and TXT files.
    Safely handles non-existent or corrupted files without throwing unhandled exceptions.
    """
    if not file_path or not os.path.exists(file_path):
        return ""

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_pdf_text(file_path).strip()
    elif ext in [".docx", ".doc"]:
        return extract_docx_text(file_path).strip()
    elif ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        except Exception as e:
            logger.warning(f"Could not read text file {file_path}: {e}")
            return ""
    else:
        # Fallback to PDF reader attempt
        return extract_pdf_text(file_path).strip()