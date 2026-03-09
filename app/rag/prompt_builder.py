def build_rag_prompt(query: str, retrieved_chunks: list[dict]) -> str:
    """Builds the prompt by injecting context chunks into the prompt template.
       If no chunks are provided, builds a basic conversational prompt."""
    
    if not retrieved_chunks:
        return f"""You are EchoRAG, a helpful and friendly AI assistant.

Please directly answer the user's question or engage in casual conversation.

Question:
{query}

Answer:"""

    context_text = "\n\n".join(
        f"Source: {chunk['metadata'].get('source', 'Unknown')}\n"
        f"Content: {chunk['text']}" 
        for chunk in retrieved_chunks
    )
    
    return f"""You are an AI assistant answering questions using retrieved documents.

Instructions:
- Explain answers clearly using your own words.
- Do not copy sentences directly from the context.
- Use the retrieved context as evidence.
- If the answer is not present in the documents, say the information is not available.

Context:
{context_text}

Question:
{query}

Answer: Explain clearly and list the source document names."""
