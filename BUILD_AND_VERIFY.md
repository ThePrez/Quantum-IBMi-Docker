# Build and Verify Guide for Quantum-IBMi-Docker

This guide provides comprehensive instructions for building and verifying the Quantum 3SAT Solver Docker container image.

## Prerequisites

### Required Software
- **Docker Desktop** (or Docker Engine)
  - macOS: [Download Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
  - Linux: Install via package manager (`apt-get install docker.io` or `yum install docker`)
  - Windows: [Download Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- **IBM i System Access** with Mapepire configured
- **Network connectivity** to IBM i system

### Verify Docker Installation
```bash
docker --version
docker info
```

## Project Structure

```
Quantum-IBMi-Docker/
├── 3sat-emulator/
│   ├── Dockerfile              # Container configuration
│   ├── grover_3sat_solver.py   # Main solver application
│   ├── test_mapepire.py        # Connection test script
│   ├── requirements.txt        # Python dependencies
│   ├── .dockerignore          # Files to exclude from build
│   ├── Db2.sql                # Database setup scripts
│   └── odbc.ini               # ODBC configuration
├── requirements.txt            # Root-level dependencies
├── README.md                   # Project documentation
└── LICENSE                     # Apache 2.0 License
```

## Build Instructions

### Step 1: Prepare the Build Context

Ensure `requirements.txt` is in the `3sat-emulator` directory:

```bash
cd Quantum-IBMi-Docker
cp requirements.txt 3sat-emulator/requirements.txt
```

### Step 2: Build the Docker Image

Navigate to the `3sat-emulator` directory and build:

```bash
cd 3sat-emulator
docker build -t quantum-3sat-solver:latest .
```

**Build Options:**
- `-t quantum-3sat-solver:latest` - Tags the image with name and version
- `.` - Specifies current directory as build context

**Expected Build Time:** 3-5 minutes (depending on network speed)

### Step 3: Verify Build Success

Check if the image was created:

```bash
docker images | grep quantum-3sat-solver
```

Expected output:
```
quantum-3sat-solver   latest    <image-id>   <time>   <size>
```

Inspect the image details:

```bash
docker inspect quantum-3sat-solver:latest
```

## Verification Methods

### Method 1: Interactive Container Test

Run the container interactively to test the solver:

```bash
docker run -it quantum-3sat-solver:latest
```

The solver will prompt for:
- IBM i hostname/IP
- Username
- Password
- Port (default: 8076)

**Expected Behavior:**
1. Connection prompt appears
2. Credentials are accepted
3. Solver connects to IBM i
4. Retrieves 3SAT instance
5. Executes Grover's algorithm
6. Displays results

### Method 2: Container Shell Access

Access the container shell to inspect the environment:

```bash
docker run -it --entrypoint /bin/bash quantum-3sat-solver:latest
```

Inside the container, verify:

```bash
# Check Python version
python --version

# Verify installed packages
pip list

# Check application files
ls -la /app

# Test imports
python -c "import qiskit; print(qiskit.__version__)"
python -c "import qiskit_aer; print('Aer OK')"
python -c "from mapepire_python.client.sql_job import SQLJob; print('Mapepire OK')"
```

### Method 3: Automated Verification Script

Create a verification script to test the container:

```bash
#!/bin/bash
# verify_container.sh

echo "=== Quantum 3SAT Solver Container Verification ==="

# Check if image exists
if docker images | grep -q quantum-3sat-solver; then
    echo "✓ Image found: quantum-3sat-solver:latest"
else
    echo "✗ Image not found"
    exit 1
fi

# Check image size
SIZE=$(docker images quantum-3sat-solver:latest --format "{{.Size}}")
echo "✓ Image size: $SIZE"

# Verify Python version in container
PYTHON_VERSION=$(docker run --rm quantum-3sat-solver:latest python --version 2>&1)
echo "✓ Python version: $PYTHON_VERSION"

# Verify Qiskit installation
docker run --rm quantum-3sat-solver:latest python -c "import qiskit; print('✓ Qiskit version:', qiskit.__version__)"

# Verify Qiskit Aer installation
docker run --rm quantum-3sat-solver:latest python -c "import qiskit_aer; print('✓ Qiskit Aer installed')"

# Verify Mapepire installation
docker run --rm quantum-3sat-solver:latest python -c "from mapepire_python.client.sql_job import SQLJob; print('✓ Mapepire installed')"

# Check file structure
echo "✓ Container file structure:"
docker run --rm quantum-3sat-solver:latest ls -la /app

echo ""
echo "=== Verification Complete ==="
```

Make it executable and run:

```bash
chmod +x verify_container.sh
./verify_container.sh
```

### Method 4: Test with Mock Data (No IBM i Required)

Modify the solver to test with hardcoded data:

```bash
docker run -it --entrypoint python quantum-3sat-solver:latest -c "
from grover_3sat_solver import ThreeSATSolver

solver = ThreeSATSolver(verbose=True)

# Test CNF parsing
test_cnf = '''c Example 3SAT problem
p cnf 3 3
1 2 -3 0
-1 2 3 0
1 -2 3 0
'''

num_vars, clauses = solver.parse_dimacs_cnf(test_cnf)
print(f'Parsed {len(clauses)} clauses with {num_vars} variables')

# Test oracle creation
oracle = solver.create_oracle_from_clauses(num_vars, clauses)
print(f'Oracle created with {oracle.num_qubits} qubits')

# Test Grover's algorithm
result = solver.solve_with_grover(oracle)
solver.display_results(result, num_vars)
"
```

## Troubleshooting

### Build Failures

**Issue:** `requirements.txt not found`
```bash
# Solution: Copy requirements.txt to build directory
cp ../requirements.txt .
```

**Issue:** `gcc not found` during build
```bash
# Solution: Dockerfile already includes gcc installation
# Verify Dockerfile line 14-17 is present
```

**Issue:** Network timeout during pip install
```bash
# Solution: Build with increased timeout
docker build --network=host -t quantum-3sat-solver:latest .
```

### Runtime Issues

**Issue:** Connection refused to IBM i
- Verify IBM i hostname/IP is correct
- Check port 8076 is open
- Ensure Mapepire daemon is running on IBM i

**Issue:** Authentication failed
- Verify username and password
- Check user has necessary permissions on IBM i

**Issue:** THREESAT() function not found
```sql
-- Run on IBM i to create the function
-- See Db2.sql for complete setup
```

## Performance Optimization

### Build Cache Optimization

Use multi-stage builds for faster rebuilds:

```dockerfile
# Add to Dockerfile for caching
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY grover_3sat_solver.py .
ENV PATH=/root/.local/bin:$PATH
```

### Runtime Optimization

Run with resource limits:

```bash
docker run -it \
  --memory="2g" \
  --cpus="2" \
  quantum-3sat-solver:latest
```

## Container Registry

### Tag for Registry

```bash
docker tag quantum-3sat-solver:latest your-registry/quantum-3sat-solver:latest
```

### Push to Registry

```bash
docker push your-registry/quantum-3sat-solver:latest
```

### Pull from Registry

```bash
docker pull your-registry/quantum-3sat-solver:latest
```

## Alternative: Build Without Docker

If Docker is not available, you can run the solver directly with Python:

### Prerequisites
- Python 3.11+
- pip package manager

### Setup

```bash
cd Quantum-IBMi-Docker/3sat-emulator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the solver
python grover_3sat_solver.py
```

### Test Connection

```bash
python test_mapepire.py
```

## Security Considerations

1. **Credentials Management**
   - Never hardcode credentials in the image
   - Use environment variables or secrets management
   - Consider using Docker secrets for production

2. **Non-root User**
   - Container runs as non-root user `quantum` (UID 1000)
   - Enhances security by limiting privileges

3. **Network Security**
   - Use encrypted connections to IBM i
   - Consider VPN or SSH tunneling for production

## Continuous Integration

### GitHub Actions Example

```yaml
name: Build and Test Docker Image

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: |
          cd Quantum-IBMi-Docker/3sat-emulator
          docker build -t quantum-3sat-solver:test .
      
      - name: Verify image
        run: |
          docker run --rm quantum-3sat-solver:test python --version
          docker run --rm quantum-3sat-solver:test python -c "import qiskit; print(qiskit.__version__)"
```

## Support

For issues or questions:
- Check the [README.md](../README.md) for project overview
- Review [Db2.sql](Db2.sql) for database setup
- Examine [grover_3sat_solver.py](grover_3sat_solver.py) for implementation details

## License

This project is licensed under the Apache License 2.0 - see [LICENSE](../LICENSE) for details.