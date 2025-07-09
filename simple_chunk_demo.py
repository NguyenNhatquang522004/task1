"""
Script đơn giản để extract chunks từ document và lưu thành file text
Chạy script này để xem cách hệ thống LLM Graph Builder chia document thành chunks
"""

import hashlib
import os
from datetime import datetime

def simple_chunk_extractor(text, chunk_size=512, chunk_overlap=50):
    """
    Chia text thành chunks đơn giản theo character count
    
    Args:
        text: Text cần chia
        chunk_size: Kích thước chunk
        chunk_overlap: Độ overlap
    
    Returns:
        List chunks
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Di chuyển start position với overlap
        start = end - chunk_overlap
        
        # Tránh infinite loop
        if start >= len(text):
            break
    
    return chunks

def extract_chunks_from_text(input_text, output_file="chunks_output.txt"):
    """
    Extract chunks từ text và lưu thành file
    
    Args:
        input_text: Text input
        output_file: File output
    """
    # Parameters giống hệ thống gốc
    chunk_size = 512
    chunk_overlap = 50
    
    # Preprocessing như trong hệ thống gốc
    bad_chars = ['"', "\n", "'"]
    cleaned_text = input_text
    for char in bad_chars:
        if char == '\n':
            cleaned_text = cleaned_text.replace(char, ' ')
        else:
            cleaned_text = cleaned_text.replace(char, '')
    
    # Tạo chunks
    chunks = simple_chunk_extractor(cleaned_text, chunk_size, chunk_overlap)
    
    # Tạo chunk info như trong hệ thống gốc
    chunk_info_list = []
    current_chunk_id = ""
    offset = 0
    
    for i, chunk in enumerate(chunks):
        # Tạo SHA1 hash ID
        page_content_sha1 = hashlib.sha1(chunk.encode())
        previous_chunk_id = current_chunk_id
        current_chunk_id = page_content_sha1.hexdigest()
        
        position = i + 1
        if i > 0:
            offset += len(chunks[i-1])
        
        chunk_info = {
            "chunk_id": current_chunk_id,
            "position": position,
            "length": len(chunk),
            "content_offset": offset,
            "previous_chunk_id": previous_chunk_id if i > 0 else None,
            "is_first_chunk": i == 0,
            "content": chunk
        }
        
        chunk_info_list.append(chunk_info)
    
    # Lưu thành file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("DOCUMENT CHUNKS EXTRACTED FROM LLM GRAPH BUILDER LOGIC\n")
        f.write("="*80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total chunks: {len(chunk_info_list)}\n")
        f.write(f"Chunk size: {chunk_size}\n")
        f.write(f"Chunk overlap: {chunk_overlap}\n")
        f.write(f"Original text length: {len(input_text)}\n")
        f.write(f"Cleaned text length: {len(cleaned_text)}\n")
        f.write("="*80 + "\n\n")
        
        for chunk_info in chunk_info_list:
            f.write(f"CHUNK #{chunk_info['position']}\n")
            f.write("-" * 50 + "\n")
            f.write(f"Chunk ID (SHA1): {chunk_info['chunk_id']}\n")
            f.write(f"Position: {chunk_info['position']}\n")
            f.write(f"Length: {chunk_info['length']} characters\n")
            f.write(f"Content Offset: {chunk_info['content_offset']}\n")
            f.write(f"Is First Chunk: {chunk_info['is_first_chunk']}\n")
            f.write(f"Previous Chunk ID: {chunk_info['previous_chunk_id']}\n")
            
            f.write("\n--- CONTENT ---\n")
            f.write(chunk_info['content'])
            f.write("\n\n" + "="*80 + "\n\n")
        
        # Neo4j Cypher queries tương ứng
        f.write("NEO4J RELATIONSHIPS THAT WOULD BE CREATED:\n")
        f.write("="*50 + "\n\n")
        
        for i, chunk_info in enumerate(chunk_info_list):
            f.write(f"// Chunk {chunk_info['position']}\n")
            f.write(f"MERGE (c{i}:Chunk {{id: '{chunk_info['chunk_id']}'}})\n")
            f.write(f"SET c{i}.text = '{chunk_info['content'][:50]}...'\n")
            f.write(f"SET c{i}.position = {chunk_info['position']}\n")
            f.write(f"SET c{i}.length = {chunk_info['length']}\n")
            f.write(f"MERGE (c{i})-[:PART_OF]->(d:Document)\n")
            
            if chunk_info['is_first_chunk']:
                f.write(f"MERGE (d)-[:FIRST_CHUNK]->(c{i})\n")
            
            if chunk_info['previous_chunk_id']:
                prev_index = i - 1
                f.write(f"MERGE (c{prev_index})-[:NEXT_CHUNK]->(c{i})\n")
            
            f.write("\n")
    
    print(f"✅ Chunks extracted and saved to: {output_file}")
    print(f"📊 Total chunks created: {len(chunk_info_list)}")
    return chunk_info_list

# Sample text để test
SAMPLE_TEXT = """
Apple Inc. is an American multinational technology company headquartered in Cupertino, California, that designs, develops, and sells consumer electronics, computer software, and online services. The company's hardware products include the iPhone smartphone, the iPad tablet computer, the Mac personal computer, the iPod portable media player, the Apple Watch smartwatch, the Apple TV digital media player, the AirPods wireless earbuds, and the HomePod smart speaker. Apple's software includes the macOS, iOS, iPadOS, watchOS, and tvOS operating systems, the iTunes media player, the Safari web browser, the Shazam music identifier, and the iLife and iWork creativity and productivity suites, as well as professional applications like Final Cut Pro, Logic Pro, and Xcode. Its online services include the iTunes Store, the iOS App Store, Mac App Store, Apple Music, Apple TV+, Apple Fitness+, iMessage, and iCloud. Other services include Apple Store, Genius Bar, AppleCare, Apple Pay, Apple Pay Cash, and Apple Card.

Apple was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in April 1976 to develop and sell Wozniak's Apple I personal computer. It was incorporated as Apple Computer, Inc. in January 1977, and sales of its computers, including the Apple II, grew quickly. Within a few years, Jobs and Wozniak had hired a staff of computer designers and had a production line. Apple went public in December 1980 to instant financial success. Over the next few years, Apple shipped new computers featuring innovative graphical user interfaces, such as the original Macintosh in 1984, and Apple's marketing advertisements for its products received widespread critical acclaim. However, the high price of its products and limited application library caused problems, as did power struggles between executives. In 1985, Wozniak departed Apple amicably and remained an honorary employee, while Jobs resigned to found NeXT, taking several Apple employees with him.

During the COVID-19 pandemic, Apple demonstrated remarkable resilience and adaptability. The company quickly pivoted to support remote work and learning, seeing increased demand for its products and services. Apple's stock price reached new highs during this period, reflecting investor confidence in the company's ability to navigate challenging market conditions. The pandemic accelerated digital transformation trends that benefited Apple's ecosystem of products and services.
"""

if __name__ == "__main__":
    print("🚀 Starting chunk extraction...")
    chunks = extract_chunks_from_text(SAMPLE_TEXT, "apple_chunks_demo.txt")
    print(f"🎯 Check the output file 'apple_chunks_demo.txt' to see the chunking results!")
