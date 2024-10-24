# app/actions/chromadb_repo.py

import chromadb

class ChromaDBAction:
    def __init__(self, db_path="chromadb", collection_name="pdf_collection"):
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection_name = collection_name

    def store_chunks_in_chromadb(self, chunks_with_embeddings, pdf_path):
        """Vectoriza y almacena fragmentos de texto en ChromaDB."""
        collection = self.chroma_client.get_or_create_collection(self.collection_name)
        
        for i, (chunk, embedding) in enumerate(chunks_with_embeddings):
            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[f"{pdf_path}_chunk_{i}"]
            )
            print(f"Fragmento {i+1} del PDF {pdf_path} almacenado en ChromaDB.")

    def search_in_chromadb(self, query_embedding):
        """Busca en ChromaDB utilizando el embedding de una consulta."""
        collection = self.chroma_client.get_collection(self.collection_name)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3  # Número de resultados a devolver
        )
        if results['documents']:
            # Asegurarse de que 'documents' es una lista de cadenas de texto
            relevant_chunks = [doc[0] for doc in results['documents']]
            return relevant_chunks
        else:
            return ["No se encontró información relevante."]