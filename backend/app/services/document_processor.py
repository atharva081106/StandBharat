import os
import mimetypes
from sqlalchemy.orm import Session
from app.models.all_models import BrandDocument
from fastapi import UploadFile

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

def extract_text_from_file(file_path: str, file_ext: str) -> str:
    text = ""
    try:
        if file_ext == '.pdf':
            import fitz
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
            
        elif file_ext == '.docx':
            import docx
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            
        elif file_ext in ['.txt', '.md', '.csv']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
            
        return text.strip()
    except Exception as e:
        raise Exception(f"Text extraction failed: {str(e)}")

def process_document(db: Session, document_id: str):
    doc = db.query(BrandDocument).filter(BrandDocument.id == document_id).first()
    if not doc:
        return
        
    if not doc.file_path or not os.path.exists(doc.file_path):
        doc.processing_status = "FAILED"
        doc.metadata_json = doc.metadata_json or {}
        doc.metadata_json["error"] = "File not found on disk"
        db.commit()
        return

    try:
        doc.processing_status = "PROCESSING"
        db.commit()
        
        file_ext = get_file_extension(doc.name)
        extracted_text = extract_text_from_file(doc.file_path, file_ext)
        
        doc.extracted_text = extracted_text
        
        # update metadata
        doc.metadata_json = doc.metadata_json or {}
        doc.metadata_json["character_count"] = len(extracted_text)
        doc.metadata_json["word_count"] = len(extracted_text.split())
        
        # Vector / RAG indexing would happen here. For now, NOT_CONFIGURED.
        doc.retrieval_status = "NOT_CONFIGURED"
        doc.processing_status = "READY"
        db.commit()
        
    except ValueError as e:
        doc.processing_status = "UNSUPPORTED"
        doc.metadata_json = doc.metadata_json or {}
        doc.metadata_json["error"] = str(e)
        db.commit()
    except Exception as e:
        doc.processing_status = "FAILED"
        doc.metadata_json = doc.metadata_json or {}
        doc.metadata_json["error"] = str(e)
        db.commit()
