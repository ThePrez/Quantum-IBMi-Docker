# Quantum-IBMi-Docker

Docker-based Jupyter Lab environment integrating Quantum computing technologies with IBM i systems, enabling quantum algorithm execution with IBM i database connectivity through interactive notebooks.

## Overview

This repository provides a containerized Jupyter Lab environment for quantum computing solutions that interact with IBM i systems through the Mapepire Python library. It demonstrates practical applications of Grover's quantum algorithm for solving 3SAT (Boolean satisfiability) problems with data stored in IBM i databases.

## Project Structure

```
Quantum-IBMi-Docker/
├── 3sat-emulator/                    # Quantum 3SAT solver with IBM i integration
│   ├── Dockerfile                    # Jupyter Lab container configuration
│   ├── 3sat.ipynb                    # Main quantum 3SAT solver notebook
│   ├── dbsetup.ipynb                 # Database setup and connection testing notebook
│   ├── jupyter_server_config.py      # Jupyter server configuration
│   ├── Db2.sql                       # IBM i database setup SQL script
│   ├── requirements.txt              # Python dependencies
│   ├── odbc.ini                      # ODBC configuration (optional)
│   ├── .dockerignore                 # Docker ignore patterns
│   └── README.md                     # 3SAT emulator documentation
├── .gitignore                        # Git ignore patterns
├── LICENSE                           # Apache 2.0 License
└── README.md                         # This file
```

## Features

- **Interactive Jupyter Notebooks**: User-friendly interface for quantum computing experimentation
- **Quantum 3SAT Solver**: Implementation of Grover's algorithm to solve Boolean satisfiability problems
- **IBM i Integration**: Direct connectivity to IBM i databases using Mapepire Python library
- **Database Setup Tools**: Automated notebook for schema creation and data insertion
- **Containerized Deployment**: Docker-based Jupyter Lab for consistent execution environments
- **Qiskit Framework**: Built on IBM's latest Qiskit quantum computing framework (≥1.0.0)
- **Aer Simulator**: Local quantum circuit simulation using Qiskit Aer
- **Visualization**: Interactive plotting of quantum measurement results

## Technologies

- **Quantum Computing**: Qiskit (≥1.0.0), Qiskit Aer (≥0.13.0)
- **IBM i Connectivity**: Mapepire Python (≥0.1.0)
- **Interactive Environment**: JupyterLab (≥4.0.0), IPython Kernel (≥6.25.0)
- **Visualization**: Matplotlib (≥3.7.0)
- **Python**: 3.11+
- **Container**: Docker

## Dependencies

```
qiskit>=1.0.0
qiskit-aer>=0.13.0
mapepire-python>=0.1.0
python-dotenv>=1.0.0
numpy>=1.24.0
jupyterlab>=4.0.0
ipykernel>=6.25.0
matplotlib>=3.7.0
```

## Getting Started

### Prerequisites

- Docker installed on your system
- Access to an IBM i system with Mapepire configured
- IBM i credentials (hostname, username, password, port)

### Quick Start

Build and run the Jupyter Lab container:

```bash
cd 3sat-emulator
docker build -t quantum-3sat-jupyter .
docker run -p 8888:8888 quantum-3sat-jupyter
```

Access Jupyter Lab at `http://127.0.0.1:8888/lab` (no token required - configured for development use).

### Using the Notebooks

1. **Database Setup** ([`dbsetup.ipynb`](3sat-emulator/dbsetup.ipynb)):
   - Connect to IBM i via Mapepire
   - Create the `DIMACS` schema
   - Create the `SAT3_1` table
   - Insert sample 3SAT problem data
   - Verify database connectivity

2. **Quantum 3SAT Solver** ([`3sat.ipynb`](3sat-emulator/3sat.ipynb)):
   - Connect to IBM i database
   - Fetch 3SAT problem instances
   - Build quantum oracle from CNF clauses
   - Execute Grover's algorithm
   - Measure and visualize results
   - Verify satisfying assignments

### Local Installation (Without Docker)

If you prefer to run locally without Docker:

```bash
cd 3sat-emulator
pip install -r requirements.txt
jupyter lab
```

## How It Works

### Grover's Algorithm for 3SAT

The 3SAT solver uses Grover's quantum search algorithm to find satisfying assignments for Boolean formulas in Conjunctive Normal Form (CNF):

1. **Database Connection**: Connects to IBM i via Mapepire to retrieve 3SAT problem instances
2. **Quantum Oracle Construction**: Builds a quantum oracle that marks satisfying assignments
3. **Grover Iteration**: Applies amplitude amplification to increase probability of measuring correct solutions
4. **Measurement**: Simulates quantum circuit execution using Qiskit Aer
5. **Verification**: Validates results against the original CNF formula

### Database Schema

The IBM i database uses the `THREESAT()` function that returns 3SAT clauses:

```sql
CREATE OR REPLACE FUNCTION JESSEG.THREESAT()
  RETURNS TABLE (c1 INT, c2 INT, c3 INT, c4 INT)
  LANGUAGE SQL
  RETURN
    VALUES (-1, -2, -3, 0),
           ( 1, -2,  3, 0),
           ( 1,  2, -3, 0),
           ( 1, -2, -3, 0),
           (-1,  2,  3, 0);
```

**Format**: Each row represents a clause with three literals (c1, c2, c3). Negative values represent negated variables. The fourth column (c4) is reserved for future use.

**Alternative Schema**: The notebooks also support the `DIMACS.SAT3_1` table format:

```sql
CREATE TABLE DIMACS.SAT3_1 (
    A INTEGER,
    B INTEGER,
    C INTEGER
)
```

## Use Cases

- **Quantum Algorithm Education**: Learn quantum computing with practical, interactive examples
- **IBM i Modernization**: Demonstrate quantum computing integration with legacy systems
- **Research & Development**: Explore quantum-classical hybrid architectures
- **Proof of Concept**: Validate quantum solutions for combinatorial optimization problems
- **Interactive Experimentation**: Modify and test quantum algorithms in real-time

## Configuration

### Jupyter Server Configuration

The [`jupyter_server_config.py`](3sat-emulator/jupyter_server_config.py) file disables authentication for development:

```python
c.ServerApp.token = ''
c.ServerApp.password = ''
c.IdentityProvider.token = ''
```

**⚠️ Security Note**: This configuration is for development/demonstration purposes. For production use, enable proper authentication.

### Docker Configuration

- **Exposed Port**: 8888 (Jupyter Lab)
- **Base Image**: `python:3.11-slim`
- **Non-root User**: Runs as user `quantum` (UID 1000)
- **Working Directory**: `/app`

## Acknowledgments

**Based on:** Jack Woehr's COMMON 2021 Presentation on Quantum Computing with IBM i

## License

This project is licensed under the Apache License 2.0 - see the [`LICENSE`](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For questions or issues:
- Open an issue in this repository
- Consult the [3SAT Emulator README](3sat-emulator/README.md) for detailed notebook documentation
