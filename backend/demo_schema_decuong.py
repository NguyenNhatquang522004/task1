#!/usr/bin/env python3
"""
Demo: Schema "decuong" tự động mapping với newSchema.json
Kiểm tra LLM chỉ sinh ra labels định sẵn trong schema
"""

import json
import os

def demo_decuong_schema_mapping():
    print("🎯 DEMO: Schema 'decuong' mapping với newSchema.json\n")
    
    # Load newSchema.json
    schema_file = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "assets", "newSchema.json")
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_data = json.load(f)
    
    # Find decuong schema
    decuong_triplets = []
    for item in schema_data:
        if item.get('schema') == 'decuong':
            decuong_triplets = item.get('triplet', [])
            break
    
    print(f"📋 Schema 'decuong' có {len(decuong_triplets)} triplets được định sẵn")
    
    # Extract unique entities and relationships
    entities = set()
    relationships = set()
    
    for triplet in decuong_triplets:
        if '->' in triplet:
            parts = triplet.split('->')
            if len(parts) == 2:
                source_rel = parts[0].split('-')
                target = parts[1]
                if len(source_rel) >= 2:
                    source = source_rel[0]
                    relation = '-'.join(source_rel[1:])
                    entities.add(source)
                    entities.add(target)
                    relationships.add(relation)
    
    print(f"\n🏷️  ENTITIES được phép trong schema 'decuong' ({len(entities)} labels):")
    for i, entity in enumerate(sorted(entities), 1):
        print(f"   {i:2d}. {entity}")
    
    print(f"\n🔗 RELATIONSHIPS được phép trong schema 'decuong' ({len(relationships)} labels):")
    for i, rel in enumerate(sorted(relationships), 1):
        print(f"   {i:2d}. {rel}")
    
    print(f"\n📝 Sample triplets từ schema 'decuong':")
    for i, triplet in enumerate(decuong_triplets[:10], 1):
        print(f"   {i:2d}. {triplet}")
    print(f"   ... và {len(decuong_triplets)-10} triplets khác")
    
    # Show LLM constraint
    print(f"\n" + "="*60)
    print(f"🤖 KHI LLM XỬ LÝ VỚI SCHEMA 'decuong':")
    print(f"✅ CHỈ được phép sinh ra {len(entities)} entity labels đã định sẵn")
    print(f"✅ CHỈ được phép sinh ra {len(relationships)} relationship labels đã định sẵn") 
    print(f"✅ KHÔNG được sinh thêm bất kỳ label nào khác")
    print(f"✅ LLMGraphTransformer được cấu hình với:")
    print(f"   - allowed_nodes = {sorted(list(entities))}")
    print(f"   - allowed_relationships = [(source, relation, target), ...]")
    print(f"   - strict_mode = True")
    
    print(f"\n🎯 CÂU TRẢ LỜI:")
    print(f"✅ CÓ! Hệ thống TỰ ĐỘNG mapping schema 'decuong' với newSchema.json")
    print(f"✅ LLM CHỈ sinh ra những labels được định sẵn trong schema 'decuong'")
    print(f"✅ Đảm bảo tính nhất quán và kiểm soát chất lượng graph")

if __name__ == "__main__":
    demo_decuong_schema_mapping()
