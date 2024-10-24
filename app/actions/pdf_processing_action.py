# app/actions/pdf_processing_action.py

import fitz  # PyMuPDF

class PDFProcessingService:
    def extract_text_from_pdf(self, pdf_path):
        """Extrae el texto de un archivo PDF."""
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()  # type: ignore
        return text

    def split_text_into_chunks(self, text, max_tokens=100):
        """Divide el texto en fragmentos más pequeños para evitar los límites de la API."""
        words = text.split()
        chunks = []
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= max_tokens:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks