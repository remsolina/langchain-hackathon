# utils/pdf_loader.py

from langchain.document_loaders import PyPDFLoader

def load_preceptor_profiles_from_pdf(pdf_path: str):
    """
    Loads the PDF, splits it into Document objects, and returns them as a list.
    Each Document contains page_content + optionally metadata.
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load_and_split()  # You can also use .load() if you don't want splitting.
    return documents
