"""
Script để trích xuất và lưu chunks từ document thành file text
Giúp hiểu rõ cách hệ thống chia document thành các chunks
"""

import os
import hashlib
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import logging

logging.basicConfig(level=logging.INFO)

class DocumentChunkExtractor:
    def __init__(self, chunk_size=512, chunk_overlap=50):
        """
        Khởi tạo extractor với parameters chunking
        
        Args:
            chunk_size: Kích thước mỗi chunk (default: 512)
            chunk_overlap: Độ overlap giữa chunks (default: 50)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
    def load_document(self, file_path):
        """
        Load document từ file path
        
        Args:
            file_path: Đường dẫn tới file
            
        Returns:
            List[Document]: Danh sách documents
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                loader = PyPDFLoader(file_path)
                documents = loader.load()
            elif file_extension in ['.txt', '.md']:
                loader = TextLoader(file_path, encoding='utf-8')
                documents = loader.load()
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
            logging.info(f"Loaded {len(documents)} pages from {file_path}")
            return documents
            
        except Exception as e:
            logging.error(f"Error loading document: {e}")
            return []
    
    def preprocess_document(self, documents):
        """
        Tiền xử lý document như trong hệ thống gốc
        
        Args:
            documents: List documents
            
        Returns:
            List[Document]: Documents đã được clean
        """
        bad_chars = ['"', "\n", "'"]
        
        for i in range(len(documents)):
            text = documents[i].page_content
            for char in bad_chars:
                if char == '\n':
                    text = text.replace(char, ' ')
                else:
                    text = text.replace(char, '')
            documents[i] = Document(
                page_content=str(text), 
                metadata=documents[i].metadata
            )
        
        logging.info("Document preprocessing completed")
        return documents
    
    def create_chunks(self, documents):
        """
        Tạo chunks từ documents
        
        Args:
            documents: List documents đã preprocess
            
        Returns:
            List[Document]: Danh sách chunks
        """
        chunks = self.text_splitter.split_documents(documents)
        logging.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def generate_chunk_info(self, chunks, file_name):
        """
        Tạo thông tin chi tiết cho từng chunk như trong hệ thống gốc
        
        Args:
            chunks: List chunks
            file_name: Tên file nguồn
            
        Returns:
            List[dict]: Thông tin chi tiết chunks
        """
        chunk_info_list = []
        current_chunk_id = ""
        offset = 0
        
        for i, chunk in enumerate(chunks):
            # Tạo SHA1 hash ID như trong hệ thống gốc
            page_content_sha1 = hashlib.sha1(chunk.page_content.encode())
            previous_chunk_id = current_chunk_id
            current_chunk_id = page_content_sha1.hexdigest()
            
            position = i + 1
            if i > 0:
                offset += len(chunks[i-1].page_content)
            
            chunk_info = {
                "chunk_id": current_chunk_id,
                "position": position,
                "length": len(chunk.page_content),
                "content_offset": offset,
                "previous_chunk_id": previous_chunk_id if i > 0 else None,
                "is_first_chunk": i == 0,
                "content": chunk.page_content,
                "source_file": file_name
            }
            
            # Thêm metadata bổ sung nếu có
            if hasattr(chunk, 'metadata') and chunk.metadata:
                if 'page' in chunk.metadata:
                    chunk_info['page_number'] = chunk.metadata['page']
                if 'source' in chunk.metadata:
                    chunk_info['source'] = chunk.metadata['source']
            
            chunk_info_list.append(chunk_info)
        
        return chunk_info_list
    
    def save_chunks_to_file(self, chunk_info_list, output_file):
        """
        Lưu chunks và metadata thành file text
        
        Args:
            chunk_info_list: Danh sách thông tin chunks
            output_file: Đường dẫn file output
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("DOCUMENT CHUNKING ANALYSIS REPORT\n")
                f.write("="*80 + "\n")
                f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total chunks: {len(chunk_info_list)}\n")
                f.write(f"Chunk size: {self.chunk_size}\n")
                f.write(f"Chunk overlap: {self.chunk_overlap}\n")
                f.write("="*80 + "\n\n")
                
                for i, chunk_info in enumerate(chunk_info_list):
                    f.write(f"CHUNK #{chunk_info['position']}\n")
                    f.write("-" * 50 + "\n")
                    f.write(f"Chunk ID: {chunk_info['chunk_id']}\n")
                    f.write(f"Position: {chunk_info['position']}\n")
                    f.write(f"Length: {chunk_info['length']} characters\n")
                    f.write(f"Content Offset: {chunk_info['content_offset']}\n")
                    f.write(f"Is First Chunk: {chunk_info['is_first_chunk']}\n")
                    f.write(f"Previous Chunk ID: {chunk_info['previous_chunk_id']}\n")
                    f.write(f"Source File: {chunk_info['source_file']}\n")
                    
                    if 'page_number' in chunk_info:
                        f.write(f"Page Number: {chunk_info['page_number']}\n")
                    
                    f.write("\nCONTENT:\n")
                    f.write("-" * 20 + "\n")
                    f.write(chunk_info['content'])
                    f.write("\n\n")
                    f.write("="*80 + "\n\n")
                
                # Thống kê tổng hợp
                f.write("SUMMARY STATISTICS\n")
                f.write("="*50 + "\n")
                total_length = sum(chunk['length'] for chunk in chunk_info_list)
                avg_length = total_length / len(chunk_info_list)
                min_length = min(chunk['length'] for chunk in chunk_info_list)
                max_length = max(chunk['length'] for chunk in chunk_info_list)
                
                f.write(f"Total characters: {total_length}\n")
                f.write(f"Average chunk length: {avg_length:.2f}\n")
                f.write(f"Minimum chunk length: {min_length}\n")
                f.write(f"Maximum chunk length: {max_length}\n")
                f.write(f"Total chunks: {len(chunk_info_list)}\n")
                
                # Phân tích overlap
                if len(chunk_info_list) > 1:
                    overlaps = []
                    for i in range(1, len(chunk_info_list)):
                        current_start = chunk_info_list[i]['content_offset']
                        previous_end = chunk_info_list[i-1]['content_offset'] + chunk_info_list[i-1]['length']
                        overlap = previous_end - current_start
                        if overlap > 0:
                            overlaps.append(overlap)
                    
                    if overlaps:
                        avg_overlap = sum(overlaps) / len(overlaps)
                        f.write(f"Average overlap: {avg_overlap:.2f} characters\n")
            
            logging.info(f"Chunks saved to: {output_file}")
            
        except Exception as e:
            logging.error(f"Error saving chunks: {e}")
    
    def extract_and_save(self, input_file, output_file=None):
        """
        Main method để extract và save chunks
        
        Args:
            input_file: Đường dẫn file input
            output_file: Đường dẫn file output (optional)
        """
        if output_file is None:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"{base_name}_chunks_analysis.txt"
        
        # Load document
        documents = self.load_document(input_file)
        if not documents:
            return
        
        # Preprocess
        documents = self.preprocess_document(documents)
        
        # Create chunks
        chunks = self.create_chunks(documents)
        
        # Generate chunk info
        file_name = os.path.basename(input_file)
        chunk_info_list = self.generate_chunk_info(chunks, file_name)
        
        # Save to file
        self.save_chunks_to_file(chunk_info_list, output_file)
        
        print(f"\n✅ Chunking completed!")
        print(f"📁 Input file: {input_file}")
        print(f"📄 Output file: {output_file}")
        print(f"📊 Total chunks: {len(chunk_info_list)}")
        print(f"⚙️  Chunk size: {self.chunk_size}")
        print(f"🔄 Chunk overlap: {self.chunk_overlap}")


def main():
    """
    Main function để test chunking với file mẫu
    """
    # Tạo extractor với parameters giống hệ thống gốc
    extractor = DocumentChunkExtractor(chunk_size=512, chunk_overlap=50)
    
    # Test với file PDF có sẵn
    test_file = "c:/edu/task1/llm-graph-builder/data/Apple stock during pandemic.pdf"
    
    if os.path.exists(test_file):
        print(f"🔍 Processing file: {test_file}")
        extractor.extract_and_save(test_file, "apple_stock_chunks_analysis.txt")
    else:
        print(f"❌ File not found: {test_file}")
        print("Please update the file path or place a test document")
        
        # Tạo file text mẫu để test
        sample_text = """
        Apple Inc. is a multinational technology company headquartered in Cupertino, California. 
        The company was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in April 1976.
        
        During the COVID-19 pandemic, Apple's stock performance showed remarkable resilience.
        The company adapted quickly to remote work trends and increased demand for technology products.
        
        Apple's product lineup includes the iPhone, iPad, Mac, Apple Watch, and Apple TV.
        The company also provides various services including the App Store, Apple Music, and iCloud.
        
        In 2020, Apple became the first U.S. company to reach a market capitalization of $2 trillion.
        This milestone reflected investor confidence in the company's ability to innovate and grow.
        """
        
        sample_file = "sample_document.txt"
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_text)
        
        print(f"📝 Created sample file: {sample_file}")
        extractor.extract_and_save(sample_file, "sample_chunks_analysis.txt")


if __name__ == "__main__":
    main()
