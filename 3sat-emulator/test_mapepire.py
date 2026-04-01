#!/usr/bin/env python3
"""Test Mapepire connection to IBM i"""

import getpass
from mapepire_python.client.sql_job import SQLJob
from mapepire_python.data_types import DaemonServer

def test_connection():
    """Test basic Mapepire connection"""
    print("Testing Mapepire connection to IBM i...")
    
    host = (input("Enter IBM i hostname/IP: ").strip() or "idevphp.idevcloud.com")
    username = (input("Enter username: ").strip() or "jgorzins")
    password = getpass.getpass("Enter password: ")
    port = int(input("Enter port (default 8076): ").strip() or "8076")
    
    try:
        daemon_server = DaemonServer(
            host=host,
            port=port,
            user=username,
            password=password
        )
        
        sql_job = SQLJob()
        sql_job.connect(daemon_server)
        
        print("✓ Connection successful!")
        
        # Test query
        print("\nTesting query: SELECT CURRENT_USER...")
        query = sql_job.query("SELECT CURRENT_USER FROM SYSIBM.SYSDUMMY1")
        result = query.run()
        
        if result.get("success") and result.get("data"):
            # Data is a list of dictionaries, get first row and first column value
            first_row = result['data'][0]
            # Get the first value from the dictionary (column name might vary)
            current_user = list(first_row.values())[0]
            print(f"✓ Current user: {current_user}")
        else:
            print(f"✗ Query failed: {result.get('error', 'Unknown error')}")
        
        # Test THREESAT function
        print("\nTesting THREESAT function...")
        query = sql_job.query("SELECT * FROM TABLE(JESSEG.THREESAT()) AS t")
        result = query.run()
        
        if result.get("success") and result.get("data"):
            print(f"✓ THREESAT function returned: {len(result['data'])} rows")
            print(f"✓ Sample data (first row): {result['data'][0]}")
            
            # The THREESAT function returns rows with columns C1, C2, C3, C4
            # representing clauses in 3SAT format
            print(f"✓ Data structure: Each row represents a clause with literals")
            print(f"✓ All rows:")
            for i, row in enumerate(result['data'][:5]):  # Show first 5 rows
                print(f"   Row {i+1}: {row}")
        else:
            print(f"✗ THREESAT query failed: {result.get('error', 'No data returned')}")
        
        sql_job.close()
        print("\n✓ Connection closed successfully")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()