# FTP Server Test Scenarios

This document outlines the test scenarios for validating the FTP server's multi-client capabilities.

## Test Environment Setup

- **Server**: FTP server running on EC2 instance
- **Control Port**: 2121 (or 21 if root access available)
- **Data Port Range**: 20000-21000
- **Test Files**:
  - `small.txt` (1.4KB) - Small text file
  - `medium.bin` (1MB) - Medium binary file
  - `large.iso` (10MB) - Large binary file

## Test Scenarios

### 1. Concurrent PUT Operations

**Objective**: Verify server can handle multiple simultaneous file uploads

**Steps**:
1. Spawn 3+ clients simultaneously
2. Each client uploads a different file (or same file from different clients)
3. All clients execute PUT command at approximately the same time

**Expected Results**:
- All uploads complete successfully
- No data corruption
- Server responds correctly to all clients
- Files are stored correctly on server

**Test Command**:
```bash
python3 tests/test_multiclient.py
# (Runs test_concurrent_put scenario)
```

---

### 2. Mixed Operations (GET + PUT + LS)

**Objective**: Verify server handles concurrent mixed command types

**Steps**:
1. Spawn 3+ clients simultaneously
2. Client 1: LS → PUT small.txt → LS
3. Client 2: GET small.txt → PUT medium.bin
4. Client 3: LS → GET medium.bin → LS

**Expected Results**:
- All operations complete successfully
- File listings are accurate
- Downloads match uploaded files
- No race conditions or data corruption

**Test Command**:
```bash
python3 tests/test_multiclient.py
# (Runs test_mixed_operations scenario)
```

---

### 3. Large File Transfers

**Objective**: Verify server handles large files with multiple concurrent clients

**Steps**:
1. Spawn 3+ clients simultaneously
2. Client 1: PUT large.iso (10MB)
3. Client 2: GET large.iso (while Client 1 is uploading)
4. Client 3: PUT medium.bin (1MB)

**Expected Results**:
- Large file upload completes successfully
- Large file download completes successfully
- File integrity verified (checksums match)
- Server remains responsive during large transfers
- No timeouts or connection drops

**Test Command**:
```bash
python3 tests/test_multiclient.py
# (Runs test_large_files scenario)
```

---

### 4. Error Cases

**Objective**: Verify proper error handling with concurrent clients

**Steps**:
1. Spawn 3+ clients simultaneously
2. Client 1: GET nonexistent_file.txt (should return 550 error)
3. Client 2: PUT valid_file.txt (should succeed)
4. Client 3: GET another_nonexistent_file.txt (should return 550 error)

**Expected Results**:
- Error responses (550) are returned correctly
- Valid operations are not affected by error cases
- Server continues to handle other clients normally
- Error messages are clear and accurate

**Test Command**:
```bash
python3 tests/test_multiclient.py
# (Runs test_error_cases scenario)
```

---

## Additional Test Scenarios

### 5. 5-Client Stress Test (All Team Members)

**Objective**: Test server with all 5 team members connecting simultaneously

**Steps**:
1. Spawn 5 clients simultaneously (one per team member)
2. Each client performs diverse operations:
   - Client 1: Multiple LS operations, PUT
   - Client 2: PUT and GET operations
   - Client 3: Mixed LS, PUT, GET operations
   - Client 4: Large file PUT operations
   - Client 5: Rapid LS, PUT, GET operations
3. Monitor server performance and resource usage

**Expected Results**:
- Server handles all 5 clients without crashing
- All operations complete successfully
- Response times remain reasonable
- No memory leaks or resource exhaustion
- File integrity maintained across all operations

**Test Command**:
```bash
python3 tests/test_multiclient.py
# (Runs test_5_client_stress scenario)
```

---

### 6. Stress Test: Maximum Concurrent Clients

**Objective**: Test server limits with maximum number of concurrent clients

**Steps**:
1. Spawn 5-10 clients simultaneously
2. Each client performs multiple operations (LS, PUT, GET)
3. Monitor server performance and resource usage

**Expected Results**:
- Server handles all clients without crashing
- Response times remain reasonable
- No memory leaks or resource exhaustion

---

### 7. Rapid Connect/Disconnect

**Objective**: Test server stability with rapid client connections

**Steps**:
1. Spawn multiple clients that connect, perform one operation, then disconnect
2. Repeat rapidly (10+ times)
3. Monitor for connection issues or resource leaks

**Expected Results**:
- All connections handled correctly
- No orphaned processes or sockets
- Server remains stable

---

### 8. Concurrent LS Operations

**Objective**: Verify directory listing accuracy with concurrent clients

**Steps**:
1. Spawn 3+ clients simultaneously
2. All clients execute LS at the same time
3. Some clients upload files while others list

**Expected Results**:
- All LS commands return consistent results
- Newly uploaded files appear in subsequent listings
- No race conditions in file listing

---

## Running All Tests

To run the automated multi-client test suite:

```bash
# Set server host/port if not using defaults
export FTP_HOST=your-ec2-ip
export FTP_PORT=2121

# Run all test scenarios
python3 tests/test_multiclient.py
```

## Manual Testing

For manual testing, you can use multiple terminal windows:

**Terminal 1**:
```bash
python3 client/ftp_client.py <server-ip> 2121
> PUT tests/test_data/small.txt
> LS
> EXIT
```

**Terminal 2** (start simultaneously):
```bash
python3 client/ftp_client.py <server-ip> 2121
> GET small.txt
> PUT tests/test_data/medium.bin
> EXIT
```

**Terminal 3** (start simultaneously):
```bash
python3 client/ftp_client.py <server-ip> 2121
> LS
> GET medium.bin
> EXIT
```

## Success Criteria

All test scenarios should pass with:
- ✅ No server crashes or hangs
- ✅ All operations complete successfully (except expected errors)
- ✅ File integrity maintained (checksums match)
- ✅ Proper error handling and error codes
- ✅ Server remains responsive under load
- ✅ No data corruption or race conditions

