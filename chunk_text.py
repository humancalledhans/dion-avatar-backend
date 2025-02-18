import re


def chunk_text(text):
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
                # If it's a new sub-section or header, start a new chunk
                if re.match(r'^[A-Z][a-zA-Z\s]+$', para.strip()):
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para.strip()
                elif current_chunk and (re.match(r'^\s*•\s|^\s*\d+\.\s', para.strip()) or para.strip().startswith('We')):
                    # Append to the last chunk if part of a list or continuation
                    current_chunk += '\n\n' + para.strip()
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para.strip()

            if current_chunk:
                chunks.append(current_chunk.strip())

    # Manage chunk size
    refined_chunks = []
    for chunk in chunks:
        if len(chunk) > 3000:  # Adjust this threshold as needed
            sub_chunks = []
            current_sub_chunk = ""
            for para in re.split(r'\n\n', chunk):
                if len(current_sub_chunk + para) > 3000:
                    sub_chunks.append(current_sub_chunk.strip())
                    current_sub_chunk = para
                else:
                    current_sub_chunk += '\n\n' + para
            sub_chunks.append(current_sub_chunk.strip())
            refined_chunks.extend(sub_chunks)
        else:
            refined_chunks.append(chunk)

    return refined_chunks


# Example usage
# (Use the text from any of the cases above here)
text = "..."
chunks = chunk_text(text)
for i, chunk in enumerate(chunks, 1):
    print(f"Chunk {i}:\n{chunk}\n")
