import os
from pinecone import Pinecone

from pinecone_upsert import get_text_embedding
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_API_KEY = "pcsk_6jqwp5_BLPY9FFhok3LcbUWMWpkjBouoobnRDgwn1KWLcwi1ncXiv1XSrTsWxBtpuvWd27"


def retrieve_relevant_docs(query, index_name, top_k=5):
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key="YOUR_PINECONE_API_KEY")
        index = pc.Index(index_name)

        # Get embedding for the query
        query_embedding = get_text_embedding(query)

        # Query the index
        query_result = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace='ns1'
        )

        # Sort by score in descending order for relevance
        sorted_results = sorted(query_result.matches,
                                key=lambda x: x.score, reverse=True)

        # Retrieve documents with full metadata
        relevant_docs = []
        for match in sorted_results:
            doc = {
                'text': match.metadata['text'],
                'product': match.metadata.get('product', 'Unknown'),
                'score': match.score,
                'website': match.metadata['website']
            }
            
            relevant_docs.append(doc)
            
        print(
            f"Retrieved {len(relevant_docs)} relevant docs for query: '{query}'")
        return relevant_docs

    except Exception as e:
        print(f"Error retrieving docs for query '{query}': {str(e)}")
        return []
