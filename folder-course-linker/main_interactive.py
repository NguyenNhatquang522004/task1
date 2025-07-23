"""
Interactive version with menu for Folder Course Linker
Phiên bản có menu cho những ai muốn chọn từng chức năng
"""
import logging
import sys
from data_analyzer import DataAnalyzer
from folder_node_creator import FolderNodeCreator
from relationship_builder import RelationshipBuilder
from config import PROJECT_NAME, VERSION, LOG_FORMAT, LOG_LEVEL

def setup_logging():
    """Thiết lập logging"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT
    )

def print_header():
    """In header của project"""
    print("=" * 80)
    print(f"🚀 {PROJECT_NAME} v{VERSION} - INTERACTIVE MODE")
    print("=" * 80)
    print("Chức năng:")
    print("1. Phân tích dữ liệu hiện tại")
    print("2. Tạo folder nodes với label = folder_name")
    print("3. Tạo relationships POINT_TO từ Course khung sườn đến folder nodes")
    print("=" * 80)

def main():
    """Main function with interactive menu"""
    setup_logging()
    print_header()
    
    # Initialize components
    analyzer = DataAnalyzer()
    creator = FolderNodeCreator()
    builder = RelationshipBuilder()
    
    try:
        while True:
            print("\n📋 MENU:")
            print("1. Phân tích dữ liệu hiện tại")
            print("2. Tạo folder nodes")
            print("3. Tạo relationships")
            print("4. Chạy toàn bộ quá trình (2+3)")
            print("5. Xóa tất cả dữ liệu đã tạo")
            print("0. Thoát")
            
            choice = input("\nChọn chức năng (0-5): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                print("\n📊 ANALYZING DATA...")
                analyzer.print_analysis_report()
            elif choice == "2":
                print("\n📁 CREATING FOLDER NODES...")
                creator.run_creation_process()
            elif choice == "3":
                print("\n🔗 CREATING RELATIONSHIPS...")
                builder.run_relationship_building()
            elif choice == "4":
                print("\n🚀 RUNNING FULL PROCESS...")
                print("\nStep 1: Creating folder nodes...")
                creator.run_creation_process()
                print("\nStep 2: Creating relationships...")
                builder.run_relationship_building()
                print("\n✅ Full process completed!")
            elif choice == "5":
                print("\n🗑️ CLEANING UP...")
                response = input("Are you sure you want to delete all created data? (y/N): ")
                if response.lower() == 'y':
                    # Delete relationships first
                    deleted_rels = builder.delete_all_relationships()
                    # Then delete nodes
                    deleted_nodes = creator.delete_all_folder_nodes()
                    print(f"✅ Cleanup completed: {deleted_rels} relationships and {deleted_nodes} nodes deleted")
                else:
                    print("❌ Cleanup cancelled")
            else:
                print("❌ Invalid choice. Please select 0-5.")
                
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        # Close all connections
        analyzer.close()
        creator.close()
        builder.close()
        print("\n🔌 Database connections closed")

if __name__ == "__main__":
    main()
