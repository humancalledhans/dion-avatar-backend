import os
from pinecone import Pinecone

from pinecone_upsert import get_text_embedding
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# PINECONE_API_KEY = "pcsk_6jqwp5_BLPY9FFhok3LcbUWMWpkjBouoobnRDgwn1KWLcwi1ncXiv1XSrTsWxBtpuvWd27"


def retrieve_relevant_docs(query, index_name, top_k=15, max_per_product=5):
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(index_name)

        # Get embedding for the query
        query_embedding = get_text_embedding(query)

        # Query the index with a higher initial fetch to ensure variety
        query_result = index.query(
            vector=query_embedding,
            # Fetch more to allow filtering (e.g., 20 for top_k=10)
            top_k=top_k * 2,
            include_metadata=True,
            namespace='ns1'
        )

        # Sort by score in descending order for relevance
        sorted_results = sorted(query_result.matches,
                                key=lambda x: x.score, reverse=True)

        # Group results by product to enforce variety
        product_groups = {}
        for match in sorted_results:
            product = match.metadata.get('product', 'Unknown')
            if product not in product_groups:
                product_groups[product] = []
            product_groups[product].append(match)

        # Select top results, limiting per product
        relevant_docs = []
        seen_products = set()
        for match in sorted_results:  # Re-iterate sorted results to maintain score priority
            product = match.metadata.get('product', 'Unknown')
            if len(product_groups[product]) <= max_per_product or product not in seen_products:
                doc = {
                    'text': match.metadata['text'],
                    'product': product,
                    'score': match.score,
                    'website': match.metadata.get('website', '')
                }
                relevant_docs.append(doc)
                seen_products.add(product)
                product_groups[product].remove(match)  # Remove to track count
                if len(relevant_docs) >= top_k:
                    break

        # If we don’t have enough docs, fill with remaining high-scoring results
        if len(relevant_docs) < top_k:
            for match in sorted_results:
                if len(relevant_docs) >= top_k:
                    break
                product = match.metadata.get('product', 'Unknown')
                if not any(d['product'] == product and d['text'] == match.metadata['text'] for d in relevant_docs):
                    doc = {
                        'text': match.metadata['text'],
                        'product': product,
                        'score': match.score,
                        'website': match.metadata.get('website', '')
                    }
                    relevant_docs.append(doc)

        print(
            f"Retrieved {len(relevant_docs)} relevant docs for query: '{query}' from {len(seen_products)} unique products")
        return relevant_docs

    except Exception as e:
        print(f"Error retrieving docs for query '{query}': {str(e)}")
        return []
