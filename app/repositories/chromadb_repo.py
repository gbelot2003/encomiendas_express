from app.actions.chromadb_action import ChromaDBAction
from app.actions.embedding_processing_action import EmbeddingProcessingAction

class ChromaDBRepo:
    def __init__(self, chromadb_action=None):
        self.chromadb_action = chromadb_action or ChromaDBAction()

    def buscar_fragmentos_relevantes(self, prompt):
        # Obtener el embedding del prompt
        query_embedding = EmbeddingProcessingAction().get_embedding_for_chunk(prompt)
        
        # Buscar en ChromaDB los fragmentos más relevantes
        relevant_chunks = self.chromadb_action.search_in_chromadb(query_embedding)
        
        # Incluir los fragmentos relevantes en el prompt
        if relevant_chunks:
            relevant_info = "\n".join(relevant_chunks)
            return {
                "role": "system",
                "content": f"Información relevante:\n{relevant_info}",
            }
        return None