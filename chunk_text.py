import tiktoken
import re


def chunk_text(text, max_tokens=500, overlap_fraction=0.5, encoding_name="cl100k_base"):
    """
    Split text into chunks with a maximum token limit and overlap, handling chapters and newlines.
    """
    # Load the tokenizer
    encoding = tiktoken.get_encoding(encoding_name)

    # Split by chapter headers first (e.g., "Chapter 1:", "Chapter 2:")
    chapter_pattern = r'\nChapter \d+:'
    sections = re.split(chapter_pattern, text)
    chapter_titles = re.findall(chapter_pattern, text)

    # Prepend chapter titles to their respective sections
    chunks = []
    if chapter_titles:
        # Handle text before the first chapter (if any)
        if sections[0].strip():
            chunks.append(sections[0].strip())
        # Pair titles with sections
        for i, title in enumerate(chapter_titles):
            section = sections[i + 1].strip()
            if section:
                chunks.append(f"{title.strip()}\n{section}")
    else:
        # No chapters, treat as one section
        chunks = [text.strip()]

    # Further split each chunk by single newlines within sections
    refined_chunks = []
    for chunk in chunks:
        # Split by single newlines (sentences/paragraphs)
        paragraphs = chunk.split('\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        current_chunk = ""
        for para in paragraphs:
            para_tokens = encoding.encode(para)
            current_chunk_tokens = encoding.encode(current_chunk)

            # If adding this paragraph exceeds max_tokens, finalize current chunk
            if len(current_chunk_tokens) + len(para_tokens) > max_tokens:
                if current_chunk:
                    refined_chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                # Add paragraph to current chunk with a newline if not first
                current_chunk = f"{current_chunk}\n{para}" if current_chunk else para

        # Append any remaining chunk
        if current_chunk:
            refined_chunks.append(current_chunk.strip())

    # Refine chunks by token count with overlap
    final_chunks = []
    overlap_tokens = int(max_tokens * overlap_fraction)

    for chunk in refined_chunks:
        chunk_tokens = encoding.encode(chunk)
        if len(chunk_tokens) <= max_tokens:
            final_chunks.append(chunk)
        else:
            # Split into token-based sub-chunks with overlap
            start = 0
            while start < len(chunk_tokens):
                end = min(start + max_tokens, len(chunk_tokens))
                sub_chunk_tokens = chunk_tokens[start:end]
                sub_chunk = encoding.decode(sub_chunk_tokens)
                final_chunks.append(sub_chunk)
                start = max(
                    0, end - overlap_tokens) if end < len(chunk_tokens) else len(chunk_tokens)

    # Validate no chunk exceeds max_tokens
    for chunk in final_chunks:
        token_count = len(encoding.encode(chunk))
        if token_count > max_tokens:
            raise ValueError(
                f"Chunk exceeds {max_tokens} tokens: {token_count} tokens found")

    return final_chunks


# Test with a mixed-format string
if __name__ == "__main__":
    text = """Trade Like The Pros is committed to nurturing financial literacy.
This is a general intro sentence.
Here’s another one.

Chapter 1: Getting Started
Trade Like The Pros’s TLTP Trade Journal costs $60.
It tracks your progress toward profitability.
You can monitor live trades and habits.

Chapter 2: Advanced Tools
Trade Like The Pros’s TLTP Algo Bundle automates trading.
It uses cutting-edge algorithms.
Save time with data-driven trades."""

    # Small max_tokens for demonstration
    chunks = chunk_text(text, max_tokens=100)
    for i, chunk in enumerate(chunks):
        tokens = len(tiktoken.get_encoding("cl100k_base").encode(chunk))
        print(f"Chunk {i} ({tokens} tokens):\n{chunk}\n")
