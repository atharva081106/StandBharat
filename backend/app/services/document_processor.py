import os
import io
import mimetypes
from sqlalchemy.orm import Session
from app.models.all_models import BrandDocument
from app.services.storage import get_storage_service, StorageFileNotFoundError

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

def extract_text_from_bytes(data: bytes, file_ext: str) -> str:
    text = ""
    try:
        if file_ext == '.pdf':
            import fitz
            doc = fitz.open(stream=data, filetype="pdf")
            for page in doc:
                text += page.get_text()
            doc.close()
            
        elif file_ext == '.docx':
            import docx
            doc = docx.Document(io.BytesIO(data))
            text = "\n".join([para.text for para in doc.paragraphs])
            
        elif file_ext in ['.txt', '.md', '.csv']:
            text = data.decode('utf-8', errors='ignore')
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
            
        return text.strip()
    except Exception as e:
        raise Exception(f"Text extraction failed: {str(e)}")

def extract_text_from_file(file_path: str, file_ext: str) -> str:
    """Legacy helper for direct file path extraction."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "rb") as f:
        return extract_text_from_bytes(f.read(), file_ext)

def process_document(db: Session, document_id: str):
    doc = db.query(BrandDocument).filter(BrandDocument.id == document_id).first()
    if not doc:
        return
        
    storage = get_storage_service()
    data: bytes = b""

    # Backward compatibility: check if file exists directly on disk or in storage service
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            with open(doc.file_path, "rb") as f:
                data = f.read()
        except Exception as e:
            doc.processing_status = "FAILED"
            doc.metadata_json = doc.metadata_json or {}
            doc.metadata_json["error"] = f"Failed to read file from disk: {str(e)}"
            db.commit()
            return
    elif doc.file_path and storage.exists(doc.file_path):
        try:
            data = storage.read_file(doc.file_path)
        except Exception as e:
            doc.processing_status = "FAILED"
            doc.metadata_json = doc.metadata_json or {}
            doc.metadata_json["error"] = f"Failed to read file from storage: {str(e)}"
            db.commit()
            return
    else:
        doc.processing_status = "FAILED"
        doc.metadata_json = doc.metadata_json or {}
        doc.metadata_json["error"] = "File not found in storage"
        db.commit()
        return

    try:
        doc.processing_status = "PROCESSING"
        db.commit()
        
        file_ext = get_file_extension(doc.name)
        extracted_text = extract_text_from_bytes(data, file_ext)
        
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
