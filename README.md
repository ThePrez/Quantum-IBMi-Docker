# Quantum-IBMi-Docker

Docker images that integrate Quantum computing technologies with IBM i systems, enabling quantum algorithm execution with IBM i database connectivity.

## Overview

This repository provides containerized quantum computing solutions that interact with IBM i systems through the Mapepire Python library. It demonstrates practical applications of quantum algorithms for solving computational problems stored in IBM i databases.

## Project Structure

```
Quantum-IBMi-Docker/
├── 3sat-emulator/          # Quantum 3SAT solver with IBM i integration
│   ├── Dockerfile          # Container configuration
│   ├── grover_3sat_solver.py  # Grover's algorithm implementation
│   ├── Db2.sql            # IBM i database setup scripts
│   ├── test_mapepire.py   # Mapepire connectivity tests
├── requirements.txt        # Python dependencies
└── LICENSE                # Apache 2.0 License
```

## Features

- **Quantum 3SAT Solver**: Implementation of Grover's algorithm to solve Boolean satisfiability problems
- **IBM i Integration**: Direct connectivity to IBM i databases using Mapepire
- **Containerized Deployment**: Docker-based deployment for consistent execution environments
- **Qiskit Framework**: Built on IBM's Qiskit quantum computing framework
- **Aer Simulator**: Local quantum circuit simulation using Qiskit Aer

## Technologies

- **Quantum Computing**: Qiskit (≥1.0.0), Qiskit Aer (≥0.13.0)
- **IBM i Connectivity**: Mapepire Python (≥0.1.0)
- **Python**: 3.11+
- **Container**: Docker

## Dependencies

```
qiskit>=1.0.0
qiskit-aer>=0.13.0
mapepire-python>=0.1.0
python-dotenv>=1.0.0
numpy>=1.24.0
```

## Getting Started

### Prerequisites

- Docker installed on your system
- Access to an IBM i system with Mapepire configured
- IBM i database with 3SAT problem instances

### Quick Start

For the fastest path to building and running:
```bash
cd 3sat-emulator
cp ../requirements.txt .
docker build -t quantum-3sat-solver:latest .
docker run -it quantum-3sat-solver:latest
```

See [QUICK_START.md](QUICK_START.md) for detailed quick start instructions.

### Comprehensive Build Guide

For detailed build instructions, verification methods, and troubleshooting:
- **[BUILD_AND_VERIFY.md](BUILD_AND_VERIFY.md)** - Complete build and verification guide
- **[QUICK_START.md](QUICK_START.md)** - Fast-track build instructions

### Verification Without Docker

If Docker is not available, you can verify the project structure:
```bash
cd 3sat-emulator
chmod +x verify_without_docker.sh
./verify_without_docker.sh
```

The solver will prompt for IBM i credentials and connect to retrieve 3SAT problem instances.

## 3SAT Solver

The 3SAT solver uses Grover's quantum algorithm to find satisfying assignments for Boolean formulas in Conjunctive Normal Form (CNF). The solver:

1. Connects to IBM i via Mapepire
2. Retrieves 3SAT problem instances from the database
3. Constructs quantum circuits using Grover's algorithm
4. Simulates quantum execution using Qiskit Aer
5. Returns satisfying variable assignments

### Database Schema

The IBM i database should provide a function `THREESAT()` that returns CNF formulas in DIMACS format:

```sql
CREATE OR REPLACE FUNCTION THREESAT()
RETURNS TABLE (CNF_FORMULA VARCHAR(32000))
```

## Use Cases

- **Quantum Algorithm Research**: Explore quantum computing applications on real-world data
- **IBM i Modernization**: Integrate quantum computing capabilities with legacy systems
- **Educational Demonstrations**: Learn quantum computing with practical examples
- **Proof of Concept**: Validate quantum-classical hybrid architectures

## License

This project is licensed under the Apache License 2.0 - see the [`LICENSE`](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
