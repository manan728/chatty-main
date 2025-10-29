#!/usr/bin/env python3
"""
Database exploration script for Chatty Backend
"""
import sqlite3
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def explore_database():
    """Explore the SQLite database structure and data."""
    db_path = "chatty.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🗄️  Chatty Database Explorer")
        print("=" * 50)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📋 Tables found: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Show table schemas
        print("\n🏗️  Table Schemas:")
        print("-" * 30)
        
        for table in tables:
            table_name = table[0]
            print(f"\n📊 {table_name.upper()}:")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                pk_indicator = " (PRIMARY KEY)" if pk else ""
                null_indicator = " NOT NULL" if not_null else ""
                print(f"  - {col_name}: {col_type}{null_indicator}{pk_indicator}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"  📈 Rows: {count}")
            
            # Show sample data if any exists
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                sample_data = cursor.fetchall()
                print(f"  📝 Sample data:")
                for row in sample_data:
                    print(f"    {row}")
        
        # Show indexes
        print("\n🔍 Indexes:")
        print("-" * 20)
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL;")
        indexes = cursor.fetchall()
        
        for index_name, index_sql in indexes:
            print(f"  - {index_name}: {index_sql}")
        
        conn.close()
        print(f"\n✅ Database exploration complete!")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_sql_query(query):
    """Run a custom SQL query."""
    db_path = "chatty.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"🔍 Running query: {query}")
        print("-" * 50)
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            # Get column names
            column_names = [description[0] for description in cursor.description]
            print(f"Columns: {', '.join(column_names)}")
            print("-" * 50)
            
            for row in results:
                print(row)
        else:
            print("No results found.")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ SQL error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run custom query
        query = " ".join(sys.argv[1:])
        run_sql_query(query)
    else:
        # Explore database
        explore_database()
