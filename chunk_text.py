import re
import tiktoken


def chunk_text(text, max_tokens=8000, overlap_fraction=0.5, encoding_name="cl100k_base"):
    """
    Split text into chunks with a maximum token limit and overlap, ensuring no chunk exceeds max_tokens.
    """
    # Load the tokenizer
    encoding = tiktoken.get_encoding(encoding_name)

    # First, split by major headers to identify chapters or large sections
    sections = re.split(r'\nChapter \d+:|\n\n', text)

    chunks = []
    for i, section in enumerate(sections):
        if i > 0:  # Skip the part before the first chapter or section
            # Handle chapter or section title
            if 'Chapter' in section:
                title = section.split('\n', 1)[0]
                chunks.append(title)
                section = section.split('\n', 1)[1] if len(
                    section.split('\n', 1)) > 1 else ""
            else:
                title = ""

            # Split into paragraphs, keeping lists and sub-sections together
            paragraphs = re.split(r'\n\s*\n', section)
            current_chunk = title
            for para in paragraphs:
                if re.match(r'^[A-Z][a-zA-Z\s]+$', para.strip()):
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para.strip()
                elif current_chunk and (re.match(r'^\s*•\s|^\s*\d+\.\s', para.strip()) or para.strip().startswith('We')):
                    current_chunk += '\n\n' + para.strip()
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para.strip()

            if current_chunk:
                chunks.append(current_chunk.strip())

    # Manage chunk size by token count with overlap, working with tokens directly
    refined_chunks = []
    # e.g., 4000 if max_tokens=8000 and overlap=0.5
    overlap_tokens = int(max_tokens * overlap_fraction)

    for chunk in chunks:
        chunk_tokens = encoding.encode(chunk)
        if len(chunk_tokens) <= max_tokens:
            refined_chunks.append(chunk)
        else:
            # Split into token-based sub-chunks with overlap
            start = 0
            while start < len(chunk_tokens):
                end = min(start + max_tokens, len(chunk_tokens))
                sub_chunk_tokens = chunk_tokens[start:end]
                sub_chunk = encoding.decode(sub_chunk_tokens)
                refined_chunks.append(sub_chunk)
                # Move start back by overlap_tokens, but not before 0
                start = max(
                    0, end - overlap_tokens) if end < len(chunk_tokens) else len(chunk_tokens)

    # Validate no chunk exceeds max_tokens
    for chunk in refined_chunks:
        token_count = len(encoding.encode(chunk))
        if token_count > max_tokens:
            raise ValueError(
                f"Chunk exceeds {max_tokens} tokens: {token_count} tokens found")

    return refined_chunks


# Example usage with debugging
if __name__ == "__main__":
    text = """
    Chapter 1: Introduction

    This is a long paragraph about something interesting. It goes on and on to test the chunking logic.

    • Item 1
    • Item 2

    Another paragraph here with more content that might exceed limits if we let it grow too much.

    Chapter 2: Next Topic

    Here’s another section with text.
    """
    chunks = chunk_text(text, max_tokens=50, overlap_fraction=0.5)
    for i, chunk in enumerate(chunks, 1):
        tokens = len(tiktoken.get_encoding("cl100k_base").encode(chunk))
        print(f"Chunk {i} ({tokens} tokens):\n{chunk}\n")
