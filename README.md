# Quantum-IBMi-Docker

Docker-based Jupyter Lab environment integrating Quantum computing technologies with IBM i systems, enabling quantum algorithm execution with IBM i database connectivity through interactive notebooks.

## Overview

This repository provides a containerized Jupyter Lab environment for quantum computing solutions that interact with IBM i systems through the Mapepire Python library. It demonstrates practical applications of Grover's quantum algorithm for solving 3SAT (Boolean satisfiability) problems with data stored in IBM i databases.

## Project Structure

```
Quantum-IBMi-Docker/
├── 3sat-emulator/
│   ├── 3sat.ipynb                 # Quantum 3SAT solver — local Aer simulator
│   ├── 3sat-ibm.ipynb             # Quantum 3SAT solver — IBM Quantum Cloud
│   ├── dbsetup.ipynb              # IBM i database setup (run once)
│   ├── Dockerfile                 # Container image definition
│   ├── requirements.txt           # Python dependencies
│   ├── jupyter_server_config.py   # Jupyter server configuration
│   ├── odbc.ini                   # ODBC configuration (optional)
│   └── README.md                  # Detailed notebook documentation
├── .gitignore
├── LICENSE                        # Apache 2.0
└── README.md                      # This file
```

## Quick Start

```bash
cd 3sat-emulator
docker build -t quantum-3sat-jupyter .
docker run -p 8888:8888 quantum-3sat-jupyter
```

Open Jupyter Lab at `http://127.0.0.1:8888/lab` (no token required — development configuration).

## How It Works

### 1. Database setup (once)

Run `dbsetup.ipynb` to create the `JESSEG.THREESAT()` table function on IBM i:

```sql
SELECT * FROM TABLE(JESSEG.THREESAT()) AS t
-- Returns 5 clauses: (-1,-2,-3), (1,-2,3), (1,2,-3), (1,-2,-3), (-1,2,3)
```

### 2. Solve with Grover's algorithm

Both solver notebooks share the same pipeline:

1. Connect to IBM i via Mapepire and fetch the 3SAT instance
2. Convert DIMACS CNF clauses to a boolean expression
3. Build a `PhaseOracleGate` oracle from that expression
4. Run **1 iteration** of Grover's algorithm (optimal for N=8 states, multiple solutions)
5. Measure, verify each clause, and plot the histogram

**`3sat.ipynb`** runs step 4 on the local Aer simulator — fast, noise-free, no extra credentials.

**`3sat-ibm.ipynb`** transpiles the circuit to a real IBM Quantum device's native gate set and submits it via `SamplerV2`. The IBM Quantum API key is prompted securely at runtime (masked input, never stored). A Job ID and tracking URL are printed so results can be retrieved if the session disconnects.

## Prerequisites

| Requirement | Details |
|---|---|
| Docker | For the containerised workflow |
| IBM i system | With Mapepire installed and running (`sc start mapepire`) |
| IBM i credentials | Hostname, username, password, port (default 8076) |
| IBM Quantum account | Required for `3sat-ibm.ipynb` only — free account at [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com) |

## Technologies

| Layer | Package |
|---|---|
| Quantum (simulator) | `qiskit`, `qiskit-aer` |
| Quantum (cloud) | `qiskit-ibm-runtime` |
| IBM i connectivity | `mapepire-python`, `gssapi` |
| Notebooks | `jupyterlab`, `ipykernel` |
| Visualisation | `matplotlib` |
| Container base | `python:3.11-slim` + `libkrb5-dev` |

See [`3sat-emulator/README.md`](3sat-emulator/README.md) for full notebook documentation including IBM Quantum API key setup, Mapepire startup, and backend selection.

## Acknowledgements

Based on Jack Woehr's COMMON 2021 presentation on Quantum Computing with IBM i.

## License

Apache License 2.0 — see [`LICENSE`](LICENSE).
