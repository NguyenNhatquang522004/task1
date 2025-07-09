#!/usr/bin/env python3
"""
Demo script to show comprehensive logging system in action
Run this to see how the logging system tracks the complete document processing workflow
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from src.process_logger import process_logger
import time
import json

async def demo_document_processing():
    """Demo function showing the complete logging workflow"""
    
    # Simulate document processing workflow
    file_name = "sample_document.pdf"
    model = "gemini-1.5-flash"
    
    print("🚀 Starting LLM Graph Builder Process Logging Demo")
    print("=" * 60)
    
    # Step 1: Start process
    process_logger.start_process(file_name, model, "local_file")
    
    # Step 2: Database connection
    await asyncio.sleep(0.2)  # Simulate connection time
    process_logger.log_step(
        "DB_CONNECTION_COMPLETE",
        "Database connection established",
        {
            'connection_time': '0.15s',
            'database': 'neo4j',
            'uri': 'neo4j+s://xxx.databases.neo4j.io'
        }
    )
    
    # Step 3: Document chunking
    await asyncio.sleep(1.0)  # Simulate chunking time
    process_logger.log_data_flow(
        "CHUNKING_COMPLETE",
        {
            'input_pages': 25,
            'token_chunk_size': 1024,
            'chunk_overlap': 100
        },
        {
            'total_chunks': 45,
            'chunk_list_length': 45,
            'avg_chunk_size': 950
        },
        1.23
    )
    
    # Step 4: Batch processing simulation
    batch_size = 10
    total_chunks = 45
    total_entities = 0
    total_relationships = 0
    
    for batch_num in range(0, total_chunks, batch_size):
        batch_end = min(batch_num + batch_size, total_chunks)
        
        process_logger.log_step(
            f"BATCH_{batch_num//batch_size + 1}_START",
            f"Processing batch {batch_num//batch_size + 1}",
            {
                'batch_number': batch_num//batch_size + 1,
                'chunk_range': f'{batch_num}-{batch_end}',
                'chunks_in_batch': batch_end - batch_num
            }
        )
        
        # Simulate LLM processing time
        llm_time = 5.0 + (batch_end - batch_num) * 0.3
        await asyncio.sleep(llm_time / 10)  # Speed up for demo
        
        # Simulate entity extraction results
        entities_extracted = (batch_end - batch_num) * 3
        relationships_extracted = (batch_end - batch_num) * 4
        total_entities += entities_extracted
        total_relationships += relationships_extracted
        
        process_logger.log_data_flow(
            f"BATCH_{batch_num//batch_size + 1}_ENTITY_EXTRACTION",
            {
                'input_chunks': batch_end - batch_num,
                'model': model,
                'chunks_to_combine': 2
            },
            {
                'entities_extracted': entities_extracted,
                'relationships_extracted': relationships_extracted,
                'processing_successful': True
            },
            llm_time
        )
        
        # Simulate database save
        await asyncio.sleep(0.3)
        process_logger.log_step(
            f"BATCH_{batch_num//batch_size + 1}_COMPLETE",
            f"Batch {batch_num//batch_size + 1} completed successfully",
            {
                'entities_saved': entities_extracted,
                'relationships_saved': relationships_extracted,
                'cumulative_entities': total_entities,
                'cumulative_relationships': total_relationships
            }
        )
    
    # Step 5: Final processing
    await asyncio.sleep(0.5)
    final_data = {
        'file_name': file_name,
        'node_count': total_entities + 45,  # entities + chunks
        'relationship_count': total_relationships + 44,  # relationships + chunk links
        'total_processing_time': 25.67,
        'model': model,
        'status': 'Completed'
    }
    
    process_logger.end_process("Completed", final_data)
    
    print("\n" + "=" * 60)
    print("✅ Demo completed! Check the generated log files:")
    print("📄 process_detailed.log - Detailed step-by-step logs")
    print(f"📊 process_log_{file_name}_*.json - Complete process data")
    print("\n🔍 Example log data structure:")
    
    # Show sample of the process data
    sample_data = {
        'file_name': file_name,
        'model': model,
        'total_steps': process_logger.step_counter,
        'status': 'Completed',
        'performance_summary': {
            'total_entities': total_entities,
            'total_relationships': total_relationships,
            'processing_time': '25.67s',
            'avg_entities_per_chunk': f'{total_entities/45:.1f}'
        }
    }
    
    print(json.dumps(sample_data, indent=2))

if __name__ == "__main__":
    print("🧪 LLM Graph Builder - Comprehensive Logging Demo")
    print("This demo shows how the logging system tracks every step of document processing")
    print("=" * 80)
    
    try:
        asyncio.run(demo_document_processing())
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
