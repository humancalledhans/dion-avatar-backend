import os
from pinecone import Pinecone

from pinecone_upsert import get_text_embedding
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_API_KEY = "pcsk_6jqwp5_BLPY9FFhok3LcbUWMWpkjBouoobnRDgwn1KWLcwi1ncXiv1XSrTsWxBtpuvWd27"


def retrieve_relevant_docs(query, index_name, top_k=3):

    print("RRD 1", PINECONE_API_KEY)
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(index_name)

    print("RRD 2")

    # Get embedding for the query
    query_embedding = get_text_embedding(query)

    print("RRD 3", len(query_embedding))

    # Query the index
    query_result = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        namespace='ns1'
    )

    print("RRD 4", query_result)

    # Sort by score in descending order for relevance
    sorted_results = sorted(query_result.matches,
                            key=lambda x: x.score, reverse=True)

    print("RRD 5", sorted_results)

    # Retrieve documents
    relevant_docs = []
    for match in sorted_results:
        relevant_docs.append({
            'text': match.metadata['text'],
            'score': match.score
        })

        print('relevant docs', relevant_docs)

    return relevant_docs
