FTP Server Project - Part 2 Submission
======================================

## EC2 Instance Information
---------------------------
EC2 Instance IP: [INSERT_EC2_IP_HERE]
EC2 Instance Type: t2.micro
Control Port: 2121
Data Port Range: 20000-21000

## Deployment Information
-------------------------
Deployment Date: [INSERT_DATE_HERE]
Deployed By: [INSERT_NAME_HERE]
Git Commit: [INSERT_COMMIT_HASH_HERE]

## Server Access
---------------
SSH Command:
  ssh -i [YOUR_KEY.pem] ec2-user@[INSERT_EC2_IP_HERE]

Server Start Command:
  cd /path/to/project
  ./deployment/manual_deploy.sh

Server Stop Command:
  ./deployment/stop_server.sh

## Execution Instructions
------------------------

### Prerequisites
1. Python 3.x installed
2. Server running on EC2 instance
3. Test data files in tests/test_data/ directory

### Running Tests

#### Single Test Suite (All Tests)
```bash
# Set server host/port if not using defaults
export FTP_HOST=[EC2_IP]
export FTP_PORT=2121

# Run all test scenarios
python3 tests/test_multiclient.py
```

#### Individual Test Scenarios
The test suite includes:
1. Test 1: Concurrent PUT (3 clients uploading simultaneously)
2. Test 2: Mixed Operations (GET+PUT+LS with 3 clients)
3. Test 3: Large File Transfers (multiple clients with large files)
4. Test 4: Error Cases (error handling with concurrent clients)
5. Test 5: 5-Client Stress Test (all team members)

### Manual Testing
For manual testing, use multiple terminal windows:

**Terminal 1:**
```bash
python3 client/ftp_client.py [EC2_IP] 2121
> PUT tests/test_data/small.txt
> LS
> EXIT
```

**Terminal 2:**
```bash
python3 client/ftp_client.py [EC2_IP] 2121
> GET small.txt
> PUT tests/test_data/medium.bin
> EXIT
```

**Terminal 3:**
```bash
python3 client/ftp_client.py [EC2_IP] 2121
> LS
> GET medium.bin
> EXIT
```

## Test Results
--------------

### Test 1: Concurrent PUT Operations
Status: [PASS/FAIL]
Description: 3+ clients uploading files simultaneously
Results:
  - Client 1: [PASS/FAIL] - [Details]
  - Client 2: [PASS/FAIL] - [Details]
  - Client 3: [PASS/FAIL] - [Details]
Notes: [Any observations or issues]

### Test 2: Mixed Operations (GET + PUT + LS)
Status: [PASS/FAIL]
Description: 3+ clients performing different operations simultaneously
Results:
  - Client 1 (LS → PUT → LS): [PASS/FAIL] - [Details]
  - Client 2 (GET → PUT): [PASS/FAIL] - [Details]
  - Client 3 (LS → GET → LS): [PASS/FAIL] - [Details]
Notes: [Any observations or issues]

### Test 3: Large File Transfers
Status: [PASS/FAIL]
Description: Multiple clients handling large files (10MB+)
Results:
  - Large file upload: [PASS/FAIL] - [Time taken, file size]
  - Large file download: [PASS/FAIL] - [Time taken, file size]
  - File integrity check: [PASS/FAIL] - [Checksum verification]
Notes: [Any observations or issues]

### Test 4: Error Cases
Status: [PASS/FAIL]
Description: Error handling with concurrent clients
Results:
  - GET nonexistent file: [PASS/FAIL] - [Error code received]
  - Valid operations during errors: [PASS/FAIL] - [Details]
Notes: [Any observations or issues]

### Test 5: 5-Client Stress Test
Status: [PASS/FAIL]
Description: All 5 team members connecting simultaneously
Results:
  - Maximum clients tested: 5
  - Server stability: [STABLE/UNSTABLE]
  - Response times: [Average response time]
  - All operations completed: [YES/NO]
Notes: [Any observations or issues]

## Performance Metrics
---------------------
Average Response Time (LS): [INSERT_TIME]ms
Average Upload Speed (1MB): [INSERT_SPEED] MB/s
Average Download Speed (1MB): [INSERT_SPEED] MB/s
Maximum Concurrent Clients: 5
Server Uptime: [INSERT_TIME]

## Issues Encountered
-------------------
[LIST ANY ISSUES, BUGS, OR LIMITATIONS DISCOVERED DURING TESTING]

See tests/BUGS.md for detailed bug reports with reproduction steps.

## Test Execution Log
--------------------
Date: [INSERT_DATE]
Tester: [INSERT_NAME]
Command Used: python3 tests/test_multiclient.py
Output: [PASTE_RELEVANT_OUTPUT_HERE]

## Additional Notes
------------------
[ANY ADDITIONAL OBSERVATIONS, RECOMMENDATIONS, OR COMMENTS]

