# Quantum-IBMi-Docker

Docker-based Jupyter Lab environment integrating quantum computing with IBM i systems. Each module demonstrates a practical quantum algorithm running against live IBM i databases via Mapepire, and can target either the local Aer simulator or real IBM Quantum hardware.

## Overview

This repository provides containerised Jupyter Lab environments for quantum computing solutions that interact with IBM i systems through the Mapepire Python library. Modules implement quantum algorithms from the iQuantum ideas catalogue, covering combinatorial optimisation and satisfiability problems with data stored in IBM i databases.

## Project Structure

```
Quantum-IBMi-Docker/
├── 3sat-emulator/
│   ├── 3sat.ipynb                      # Quantum 3SAT solver - local Aer simulator
│   ├── 3sat-ibm.ipynb                  # Quantum 3SAT solver - IBM Quantum Cloud
│   ├── dbsetup.ipynb                   # IBM i database setup (run once)
│   ├── Dockerfile                      # Container image definition
│   ├── requirements.txt                # Python dependencies
│   ├── jupyter_server_config.py        # Jupyter server configuration
│   ├── odbc.ini                        # ODBC configuration (optional)
│   └── README.md                       # Detailed notebook documentation
├── qaoa-scheduler/
│   ├── qaoa_scheduler.ipynb            # QAOA batch job scheduler - local Aer simulator
│   ├── qaoa_scheduler_ibm.ipynb        # QAOA batch job scheduler - IBM Quantum Cloud
│   ├── dbsetup.ipynb                   # IBM i database setup (run once)
│   ├── Dockerfile                      # Container image definition
│   ├── requirements.txt                # Python dependencies
│   ├── jupyter_server_config.py        # Jupyter server configuration
│   ├── odbc.ini                        # ODBC configuration (optional)
│   └── README.md                       # Detailed notebook documentation
├── .gitignore
├── LICENSE                             # Apache 2.0
└── README.md                           # This file
```

## Modules

### `3sat-emulator/` — Quantum 3SAT Solver

Solves a 3SAT Boolean satisfiability problem using **Grover's algorithm**. The CNF clause data is stored in an IBM i database and fetched via Mapepire. Results are verified clause-by-clause and visualised as a measurement histogram.

```bash
cd 3sat-emulator
docker build -t quantum-3sat-jupyter .
docker run -p 8888:8888 quantum-3sat-jupyter
```

See [`3sat-emulator/README.md`](3sat-emulator/README.md) for full documentation.

---

### `qaoa-scheduler/` — QAOA Batch Job Scheduler

Optimises the scheduling of **8 IBM i batch jobs** across 4 time slots using the **Quantum Approximate Optimisation Algorithm (QAOA)**. The job queue (with priority, duration, memory, and dependency attributes) is stored in IBM i and fetched via Mapepire. The scheduling problem is encoded as a QUBO, converted to an Ising Hamiltonian, and solved with COBYLA-optimised QAOA. The resulting schedule is written back to IBM i.

```bash
cd qaoa-scheduler
docker build -t quantum-qaoa-scheduler .
docker run -p 8888:8888 quantum-qaoa-scheduler
```

See [`qaoa-scheduler/README.md`](qaoa-scheduler/README.md) for full documentation.

---

## Common Prerequisites

| Requirement | Details |
|---|---|
| Docker | For the containerised workflow |
| IBM i system | With Mapepire installed and running (`sc start mapepire`) |
| IBM i credentials | Hostname, username, password, port (default 8076) |
| IBM Quantum account | Required for IBM Cloud notebooks only — free account at [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com) |

## Technologies

| Layer | Package |
|---|---|
| Quantum (simulator) | `qiskit`, `qiskit-aer` |
| Quantum (cloud) | `qiskit-ibm-runtime` |
| IBM i connectivity | `mapepire-python`, `gssapi` |
| Notebooks | `jupyterlab`, `ipykernel` |
| Visualisation | `matplotlib` |
| Container base | `python:3.11-slim` + `libkrb5-dev` |

## Acknowledgements

Based on Jack Woehr's COMMON 2021 presentation on Quantum Computing with IBM i, and the iQuantum ideas catalogue for practical quantum + IBM i applications.

## License

Apache License 2.0 — see [`LICENSE`](LICENSE).
