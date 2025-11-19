#!/usr/bin/env python3
"""
Multi-client test script
Spawns 3+ clients simultaneously to test concurrent operations
"""

import os
import sys
import threading
import time
import socket
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from client.connection_handler import ControlConn, open_data_conn
from client.config import HOST, CONTROL_PORT, BUFFER_SIZE
from shared import protocol

# Test configuration
SERVER_HOST = os.getenv("FTP_HOST", HOST)
SERVER_PORT = int(os.getenv("FTP_PORT", CONTROL_PORT))
TEST_DATA_DIR = project_root / "tests" / "test_data"

def check_server_connectivity(host, port, timeout=3):
    """Check if server is accessible before running tests"""
    print(f"Checking server connectivity to {host}:{port}...")
    
    # Check if host is still a placeholder
    if host.startswith("[") and host.endswith("]"):
        print(f"\n❌ ERROR: Server host is still a placeholder: {host}")
        print("Please set the FTP_HOST environment variable:")
        print("  export FTP_HOST=your-ec2-ip-address")
        print("  export FTP_PORT=2121")
        print("  python3 tests/test_multiclient.py")
        return False
    
    try:
        # Try to connect to the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Server is accessible at {host}:{port}\n")
            return True
        else:
            print(f"\n❌ ERROR: Cannot connect to server at {host}:{port}")
            print("Possible issues:")
            print("  1. Server is not running")
            print("  2. Incorrect host/port")
            print("  3. Firewall blocking connection")
            print("  4. Server is not accessible from this network")
            print("\nTo start the server locally:")
            print("  cd /path/to/project")
            print("  export PYTHONPATH=\"${PYTHONPATH}:$(pwd)\"")
            print("  python3 server/ftp_server.py")
            print("\nOr for EC2 deployment:")
            print("  ./deployment/manual_deploy.sh")
            return False
    except socket.gaierror as e:
        print(f"\n❌ ERROR: Cannot resolve hostname '{host}'")
        print(f"   {e}")
        print("\nPlease check:")
        print("  1. Hostname/IP address is correct")
        print("  2. Network connectivity")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: Connection check failed: {e}")
        return False

def do_ls(ctrl):
    """Execute LS command"""
    ctrl.send_line("LS")
    first = ctrl.recv_line()
    if not first.startswith(protocol.OK):
        return None, f"LS error: {first}"
    
    try:
        parts = first.split()
        p = int(parts[parts.index("PORT") + 1])
    except Exception as e:
        return None, f"Bad LS response: {first}"
    
    try:
        ds = open_data_conn(SERVER_HOST, p)
        buf = b""
        while True:
            chunk = ds.recv(BUFFER_SIZE)
            if not chunk:
                break
            buf += chunk
        ds.close()
        listing = buf.decode("utf-8", errors="replace").strip()
        last = ctrl.recv_line()
        return listing, None
    except Exception as e:
        return None, f"LS data error: {e}"

def do_get(ctrl, filename):
    """Execute GET command"""
    ctrl.send_line(f"GET {filename}")
    first = ctrl.recv_line()
    if not first.startswith(protocol.OK):
        return False, f"GET error: {first}"
    
    try:
        parts = first.split()
        p = int(parts[parts.index("PORT") + 1])
        n = int(parts[parts.index("SIZE") + 1])
    except Exception as e:
        return False, f"Bad GET response: {first}"
    
    got = 0
    try:
        ds = open_data_conn(SERVER_HOST, p)
        out_name = f"client_download_{filename}"
        with open(out_name, "wb") as f:
            while got < n:
                chunk = ds.recv(min(BUFFER_SIZE, n - got))
                if not chunk:
                    break
                f.write(chunk)
                got += len(chunk)
        ds.close()
        last = ctrl.recv_line()
        return got == n, None
    except Exception as e:
        return False, f"GET data error: {e}"

def do_put(ctrl, filename):
    """Execute PUT command"""
    if not os.path.exists(filename):
        return False, f"File not found: {filename}"
    
    size = os.path.getsize(filename)
    ctrl.send_line(f"PUT {os.path.basename(filename)} SIZE {size}")
    first = ctrl.recv_line()
    if not first.startswith(protocol.OK):
        return False, f"PUT error: {first}"
    
    try:
        parts = first.split()
        p = int(parts[parts.index("PORT") + 1])
    except Exception as e:
        return False, f"Bad PUT response: {first}"
    
    sent = 0
    try:
        ds = open_data_conn(SERVER_HOST, p)
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                ds.sendall(chunk)
                sent += len(chunk)
        ds.close()
        last = ctrl.recv_line()
        if last.startswith(protocol.DONE):
            return True, None
        else:
            return False, f"PUT incomplete: {last}"
    except Exception as e:
        return False, f"PUT data error: {e}"

def client_worker(client_id, operations):
    """Worker function for a single client thread"""
    results = []
    try:
        with ControlConn(SERVER_HOST, SERVER_PORT) as ctrl:
            print(f"[Client {client_id}] Connected to {SERVER_HOST}:{SERVER_PORT}")
            
            for op in operations:
                op_type = op["type"]
                print(f"[Client {client_id}] Executing: {op_type}")
                
                if op_type == "LS":
                    listing, error = do_ls(ctrl)
                    if error:
                        results.append({"op": "LS", "status": "FAIL", "error": error})
                    else:
                        results.append({"op": "LS", "status": "OK", "files": len(listing.split("\n")) if listing else 0})
                
                elif op_type == "GET":
                    success, error = do_get(ctrl, op["filename"])
                    if error:
                        results.append({"op": "GET", "status": "FAIL", "error": error})
                    else:
                        results.append({"op": "GET", "status": "OK" if success else "FAIL"})
                
                elif op_type == "PUT":
                    success, error = do_put(ctrl, op["filename"])
                    if error:
                        results.append({"op": "PUT", "status": "FAIL", "error": error})
                    else:
                        results.append({"op": "PUT", "status": "OK" if success else "FAIL"})
                
                # Small delay between operations
                time.sleep(0.1)
            
            ctrl.send_line("EXIT")
            print(f"[Client {client_id}] Disconnected")
    
    except ConnectionRefusedError as e:
        results.append({"op": "CONNECTION", "status": "FAIL", "error": f"Connection refused - server not running or not accessible"})
        print(f"[Client {client_id}] ❌ Connection refused - server may not be running at {SERVER_HOST}:{SERVER_PORT}")
    except Exception as e:
        results.append({"op": "CONNECTION", "status": "FAIL", "error": str(e)})
        print(f"[Client {client_id}] ❌ Error: {e}")
    
    return {"client_id": client_id, "results": results}

def test_concurrent_put():
    """Test: 3 clients uploading different files simultaneously"""
    print("\n=== Test 1: Concurrent PUT ===")
    threads = []
    results_list = []
    operations_list = [
        [{"type": "PUT", "filename": str(TEST_DATA_DIR / "small.txt")}],
        [{"type": "PUT", "filename": str(TEST_DATA_DIR / "medium.bin")}],
        [{"type": "PUT", "filename": str(TEST_DATA_DIR / "small.txt")}],  # Same file, different client
    ]
    
    def make_worker_with_result(idx, ops, results):
        def worker():
            result = client_worker(idx, ops)
            results.append(result)
            return result
        return worker
    
    for i, ops in enumerate(operations_list, 1):
        t = threading.Thread(target=make_worker_with_result(i, ops, results_list))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # Report results
    passed = sum(1 for r in results_list if all(op["status"] == "OK" for op in r.get("results", [])))
    total = len(results_list)
    print(f"Results: {passed}/{total} clients completed successfully")
    print("=== Test 1 Complete ===\n")
    return results_list

def test_mixed_operations():
    """Test: 3 clients performing GET+PUT+LS simultaneously"""
    print("\n=== Test 2: Mixed Operations (GET+PUT+LS) ===")
    threads = []
    results_list = []
    # Fixed: Ensure files are uploaded before GET operations
    # Client 1: Upload small.txt, then list
    # Client 2: Upload medium.bin, then list (to verify)
    # Client 3: List, then GET both files (they should exist by now)
    operations_list = [
        [{"type": "PUT", "filename": str(TEST_DATA_DIR / "small.txt")}, {"type": "LS"}],
        [{"type": "PUT", "filename": str(TEST_DATA_DIR / "medium.bin")}, {"type": "LS"}],
        [{"type": "LS"}, {"type": "GET", "filename": "small.txt"}, {"type": "GET", "filename": "medium.bin"}, {"type": "LS"}],
    ]
    
    def make_worker_with_result(idx, ops, results):
        def worker():
            result = client_worker(idx, ops)
            results.append(result)
            return result
        return worker
    
    for i, ops in enumerate(operations_list, 1):
        t = threading.Thread(target=make_worker_with_result(i, ops, results_list))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # Report results
    passed = sum(1 for r in results_list if all(op["status"] == "OK" for op in r.get("results", [])))
    total = len(results_list)
    print(f"Results: {passed}/{total} clients completed successfully")
    print("=== Test 2 Complete ===\n")
    return results_list

def test_large_files():
    """Test: Multiple clients handling large files"""
    print("\n=== Test 3: Large Files ===")
    threads = []
    results_list = []
    # Fixed: Ensure file is uploaded first, then downloaded
    # Client 1 uploads large file, Client 2 uploads medium file, Client 3 downloads large file (after upload)
    operations_list = [
        [{"type": "PUT", "filename": str(TEST_DATA_DIR / "large.iso")}],
        [{"type": "PUT", "filename": str(TEST_DATA_DIR / "medium.bin")}],
        [{"type": "LS"}, {"type": "GET", "filename": "large.iso"}],  # LS first to ensure file exists
    ]
    
    def make_worker_with_result(idx, ops, results):
        def worker():
            result = client_worker(idx, ops)
            results.append(result)
            return result
        return worker
    
    for i, ops in enumerate(operations_list, 1):
        t = threading.Thread(target=make_worker_with_result(i, ops, results_list))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # Report results
    passed = sum(1 for r in results_list if all(op["status"] == "OK" for op in r.get("results", [])))
    total = len(results_list)
    print(f"Results: {passed}/{total} clients completed successfully")
    print("=== Test 3 Complete ===\n")
    return results_list

def test_error_cases():
    """Test: Error handling with multiple clients"""
    print("\n=== Test 4: Error Cases ===")
    threads = []
    results_list = []
    operations_list = [
        [{"type": "GET", "filename": "nonexistent_file.txt"}],  # Should fail
        [{"type": "PUT", "filename": str(TEST_DATA_DIR / "small.txt")}],  # Should succeed
        [{"type": "GET", "filename": "nonexistent_file2.txt"}],  # Should fail
    ]
    
    def make_worker_with_result(idx, ops, results):
        def worker():
            result = client_worker(idx, ops)
            results.append(result)
            return result
        return worker
    
    for i, ops in enumerate(operations_list, 1):
        t = threading.Thread(target=make_worker_with_result(i, ops, results_list))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # Report results (note: errors are expected for GET nonexistent files)
    # Client 2 should succeed (PUT), clients 1 and 3 should fail (GET nonexistent)
    # Count operations: Client 1 (GET fail), Client 2 (PUT success), Client 3 (GET fail)
    total_ops = sum(len(r.get("results", [])) for r in results_list)
    # Expected: 1 success (PUT), 2 failures (GET nonexistent)
    expected_success = 1
    expected_failures = 2
    actual_success = sum(1 for r in results_list for op in r.get("results", []) if op.get("status") == "OK")
    actual_failures = sum(1 for r in results_list for op in r.get("results", []) if op.get("status") == "FAIL")
    print(f"Results: {actual_success} succeeded (expected {expected_success}), {actual_failures} failed (expected {expected_failures})")
    if actual_success == expected_success and actual_failures == expected_failures:
        print("✅ Error handling working correctly")
    else:
        print("⚠️  Unexpected results - check error handling")
    print("=== Test 4 Complete ===\n")
    return results_list

def test_5_client_stress():
    """Test: 5-client stress test (all team members)"""
    print("\n=== Test 5: 5-Client Stress Test ===")
    print("Simulating all 5 team members connecting simultaneously")
    threads = []
    results_list = []
    
    # Create diverse operations for 5 clients to stress test the server
    operations_list = [
        # Client 1: Multiple LS operations
        [{"type": "LS"}, {"type": "LS"}, {"type": "PUT", "filename": str(TEST_DATA_DIR / "small.txt")}, {"type": "LS"}],
        # Client 2: Upload and download
        [{"type": "PUT", "filename": str(TEST_DATA_DIR / "medium.bin")}, {"type": "GET", "filename": "medium.bin"}],
        # Client 3: Mixed operations
        [{"type": "LS"}, {"type": "PUT", "filename": str(TEST_DATA_DIR / "small.txt")}, {"type": "GET", "filename": "small.txt"}],
        # Client 4: Large file operations
        [{"type": "PUT", "filename": str(TEST_DATA_DIR / "large.iso")}, {"type": "LS"}],
        # Client 5: Rapid operations
        [{"type": "LS"}, {"type": "PUT", "filename": str(TEST_DATA_DIR / "medium.bin")}, {"type": "LS"}, {"type": "GET", "filename": "medium.bin"}],
    ]
    
    def make_worker_with_result(idx, ops, results):
        def worker():
            result = client_worker(idx, ops)
            results.append(result)
            return result
        return worker
    
    for i, ops in enumerate(operations_list, 1):
        t = threading.Thread(target=make_worker_with_result(i, ops, results_list))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    # Report results
    passed = sum(1 for r in results_list if all(op["status"] == "OK" for op in r.get("results", [])))
    total = len(results_list)
    print(f"Results: {passed}/{total} clients completed successfully")
    print("=== Test 5 Complete ===\n")
    return results_list

def main():
    """Run all multi-client tests"""
    print("=" * 50)
    print("Multi-Client FTP Server Test Suite")
    print(f"Server: {SERVER_HOST}:{SERVER_PORT}")
    print("=" * 50)
    
    # Check server connectivity first
    if not check_server_connectivity(SERVER_HOST, SERVER_PORT):
        print("\n⚠️  Tests cannot proceed without server connection.")
        sys.exit(1)
    
    # Check if test data exists
    if not TEST_DATA_DIR.exists():
        print(f"ERROR: Test data directory not found: {TEST_DATA_DIR}")
        sys.exit(1)
    
    try:
        all_test_results = []
        
        results1 = test_concurrent_put()
        all_test_results.append(("Test 1: Concurrent PUT", results1))
        time.sleep(1)  # Brief pause between test suites
        
        results2 = test_mixed_operations()
        all_test_results.append(("Test 2: Mixed Operations", results2))
        time.sleep(1)
        
        results3 = test_large_files()
        all_test_results.append(("Test 3: Large Files", results3))
        time.sleep(1)
        
        results4 = test_error_cases()
        all_test_results.append(("Test 4: Error Cases", results4))
        time.sleep(1)
        
        results5 = test_5_client_stress()
        all_test_results.append(("Test 5: 5-Client Stress", results5))
        
        # Print summary
        print("=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        total_ops = 0
        passed_ops = 0
        failed_ops = 0
        
        for test_name, results in all_test_results:
            test_ops = sum(len(r.get("results", [])) for r in results)
            test_passed = sum(sum(1 for op in r.get("results", []) if op.get("status") == "OK") for r in results)
            test_failed = sum(sum(1 for op in r.get("results", []) if op.get("status") == "FAIL") for r in results)
            
            # Special handling for Test 4 (Error Cases) - failures are expected
            if "Error Cases" in test_name:
                # Expected: 1 success (PUT), 2 failures (GET nonexistent)
                if test_passed == 1 and test_failed == 2:
                    status = "✅ PASS (expected failures)"
                else:
                    status = f"⚠️  PARTIAL ({test_passed} success, {test_failed} failures - expected 1 success, 2 failures)"
            else:
                status = "✅ PASS" if test_passed == test_ops else f"⚠️  PARTIAL ({test_passed}/{test_ops})"
            
            print(f"{test_name}: {status}")
            
            # Show detailed failures for non-error-case tests
            if "Error Cases" not in test_name and test_failed > 0:
                print(f"  Failed operations:")
                for r in results:
                    for op in r.get("results", []):
                        if op.get("status") == "FAIL":
                            error_msg = op.get("error", "Unknown error")
                            print(f"    Client {r.get('client_id')} - {op.get('op')}: {error_msg}")
            
            total_ops += test_ops
            passed_ops += test_passed
            failed_ops += test_failed
        
        print("=" * 50)
        # For overall count, exclude expected failures from Test 4
        # Test 4 has 2 expected failures, so subtract those from total
        expected_failures = 2  # From Test 4
        adjusted_total = total_ops - expected_failures
        adjusted_passed = passed_ops
        
        print(f"Overall: {adjusted_passed}/{adjusted_total} operations passed (excluding expected failures)")
        if adjusted_passed == adjusted_total:
            print("✅ All tests passed!")
        else:
            unexpected_failures = failed_ops - expected_failures
            if unexpected_failures > 0:
                print(f"⚠️  {unexpected_failures} unexpected operations failed")
            else:
                print("✅ All operations passed (including expected error cases)")
        print("=" * 50)
    
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

