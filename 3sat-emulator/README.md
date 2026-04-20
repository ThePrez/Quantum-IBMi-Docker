# Quantum 3SAT Solver - Jupyter Notebooks

This directory contains Jupyter notebooks for solving 3SAT problems using Grover's quantum algorithm with IBM i database integration via Mapepire.

## Notebooks

1. **`dbsetup.ipynb`** - Database setup and connection testing
   - Tests Mapepire connection to IBM i
   - Sets current schema to JESSEG
   - Creates JESSEG schema
   - Creates THREESAT() function with embedded sample data
   - Verifies THREESAT function returns correct data

2. **`3sat.ipynb`** - Quantum 3SAT solver
   - Connects to IBM i and fetches 3SAT instances
   - Creates quantum oracle from clauses
   - Runs Grover's algorithm
   - Visualizes results

## Running the Notebooks

### Option 1: Using Docker (Recommended)

```bash
# Build the Docker image
docker build -t quantum-3sat-jupyter .

# Run the container
docker run -p 8888:8888 quantum-3sat-jupyter
```

Access Jupyter Lab at the URL shown in the terminal output (typically `http://127.0.0.1:8888/lab?token=...`).

### Option 2: Local Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Start Jupyter Lab
jupyter lab
```

## Requirements

- Python 3.11+
- Qiskit 1.0.0+
- Mapepire Python 0.1.0+
- JupyterLab 4.0.0+
- Access to IBM i system with Mapepire configured

## Usage

1. First, run `dbsetup.ipynb` to set up the database and test connectivity
2. Then, run `3sat.ipynb` to solve 3SAT problems using quantum algorithms

## Files

- `3sat.ipynb` - Main quantum solver notebook
- `dbsetup.ipynb` - Database setup notebook (includes all database setup logic)
- `Dockerfile` - Container configuration for Jupyter Lab
- `requirements.txt` - Python dependencies
- `jupyter_server_config.py` - Jupyter server configuration