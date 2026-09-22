# QAOA Batch Job Scheduler - Jupyter Notebooks

Jupyter notebooks for optimizing IBM i batch job scheduling using the **Quantum Approximate Optimization Algorithm (QAOA)**. Job data is fetched from an IBM i database via Mapepire, the scheduling problem is encoded as a Quadratic Unconstrained Binary Optimization (QUBO) and solved with QAOA, and the optimised schedule is written back to IBM i. Runs either on the local Aer simulator or on real IBM Quantum hardware.

---

## Notebooks

| Notebook | Purpose |
|---|---|
| `dbsetup.ipynb` | One-time IBM i database setup - creates `QSCHEDULE.JOBQUEUE()` and `QSCHEDULE.SCHEDULE_RESULTS` |
| `qaoa_scheduler.ipynb` | QAOA batch job scheduler using the **- local Aer simulator** |
| `qaoa_scheduler_ibm.ipynb` | QAOA batch job scheduler running on a real **- IBM Quantum device** |

### `dbsetup.ipynb`
- Prompts for IBM i connection details
- Creates the `QSCHEDULE` schema, `JOBQUEUE()` table function (8 pre-loaded IBM i batch jobs), and `SCHEDULE_RESULTS` results table
- Verifies both objects exist and return data

### `qaoa_scheduler.ipynb` - Local Simulator
- Connects to IBM i via Mapepire and fetches the job queue from `QSCHEDULE.JOBQUEUE()`
- Builds a QUBO cost matrix encoding one-hot, priority, dependency, and memory constraints
- Converts the QUBO to an Ising Hamiltonian as a `SparsePauliOp`
- Builds a parameterized QAOA circuit
- Optimizes circuit parameters with COBYLA on the local Aer simulator
- Decodes the best bitstring into a slot-based job schedule
- Validates dependency constraints and writes the result to `QSCHEDULE.SCHEDULE_RESULTS`
- Visualizes results with a measurement histogram and a Gantt-style schedule chart

### `qaoa_scheduler_ibm.ipynb` - IBM Quantum Cloud
- Same workflow as `qaoa_scheduler.ipynb` but submits circuits to a real IBM Quantum device
- Prompts for the IBM Quantum API key at runtime (masked input - never stored in notebook)
- Uses `SamplerV2` + `generate_preset_pass_manager` (optimization level 3) for ISA transpilation
- Prints the Job ID and a tracking URL for the final sampling job

---

## Running the Notebooks

### Option 1: Docker (Recommended)

```bash
# From inside the qaoa-scheduler/ directory:
docker build -t quantum-qaoa-scheduler .
docker run -p 8888:8888 quantum-qaoa-scheduler
```

Open Jupyter Lab at `http://127.0.0.1:8888/lab` (no token required - configured for development).

### Option 2: Local Installation

```bash
pip install -r requirements.txt
jupyter lab
```

---

## Workflow

### Local simulator

1. Run `dbsetup.ipynb` - sets up the IBM i database (one time only)
2. Run `qaoa_scheduler.ipynb` - solves the scheduling problem on the local simulator

### IBM Quantum Cloud

1. Run `dbsetup.ipynb` - sets up the IBM i database (one time only)
2. Obtain your IBM Quantum API key (see [IBM Quantum API Key](#ibm-quantum-api-key) below)
3. Run `qaoa_scheduler_ibm.ipynb` - submits circuits to real quantum hardware

---

## Problem Description

The scheduler optimises the placement of **8 IBM i batch jobs** into **4 time slots**, minimising total weighted makespan subject to three constraint types:

| Job | Duration (min) | Priority | Memory (MB) | Depends On |
|---|---|---|---|---|
| PAYROLL | 45 | 1 | 512 | - |
| INVUPD | 30 | 2 | 256 | - |
| GLCLOSE | 60 | 1 | 768 | PAYROLL |
| ARAGING | 20 | 3 | 128 | - |
| SALESRPT | 25 | 2 | 192 | INVUPD |
| BACKUPDB | 90 | 1 | 1024 | GLCLOSE |
| TAXCALC | 35 | 1 | 384 | PAYROLL |
| SHIPCONF | 15 | 3 | 96 | ARAGING |

### QUBO Encoding

The binary variable `x_{i,s} = 1` means job `i` is assigned to slot `s`.

| Term | Effect |
|---|---|
| One-hot penalty | Each job assigned to exactly one slot |
| Priority reward | Higher-priority jobs cost more in later slots |
| Dependency penalty | Job A before its dependency → large cost increase |
| Memory penalty | Pairs of jobs in the same slot exceeding 2048 MB → cost increase |

The QUBO is converted to an Ising Hamiltonian via `x_i = (1 − Z_i) / 2` and expressed as a `SparsePauliOp` for Qiskit.

---

## IBM Quantum API Key

The API key (also called *API token*) authenticates your access to [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com). When you run `qaoa_scheduler_ibm.ipynb` you will be prompted:

```
Enter IBM Quantum API key: ········
```

The input is masked like a password and is **never written to disk or stored in the notebook**.

### Getting your key

1. Go to [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com) and sign in (or create a free IBMid account)
2. Click your **account name / avatar** → **Manage account**, or go directly to [quantum.cloud.ibm.com/account](https://quantum.cloud.ibm.com/account)
3. Under **API keys**, click **Create +** or **View** next to an existing key
4. Copy the key - keep it private, never commit it to a repository

> Free accounts include access to real quantum backends at no charge.

### Optional: save credentials locally

To avoid re-entering the key every session:

```python
from qiskit_ibm_runtime import QiskitRuntimeService

QiskitRuntimeService.save_account(
    token="YOUR_API_KEY_HERE",
    overwrite=True,
    set_as_default=True,
)
```

Credentials are stored in `~/.qiskit/qiskit-ibm.json`. Once saved, replace the prompt cell with:

```python
service = QiskitRuntimeService()  # loads saved credentials
```

> ⚠️ Never commit `~/.qiskit/qiskit-ibm.json` or any file containing your key to a repository.

### Selecting a backend

By default the notebook picks the least-busy real device:

```python
backend = service.least_busy(simulator=False, operational=True)
```

To target a specific device:

```python
backend = service.backend("ibm_xyz..")
```

To use the cloud simulator instead of real hardware:

```python
backend = service.least_busy(simulator=True)
```

List all available backends:

```python
for b in service.backends():
    print(b.name, b.num_qubits, "qubits")
```

### Retrieving a job result later

After the final sampling job is submitted the notebook prints:

```
Job ID      : abc123xyz
Tracking URL: https://quantum.cloud.ibm.com/jobs/abc123xyz
```

To retrieve results in a new session without re-running:

```python
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()
job = service.job("abc123xyz")
result = job.result()
counts = result[0].data.c.get_counts()
```

---

## Mapepire - IBM i Connectivity

Both solver notebooks connect to IBM i using [Mapepire]. The Mapepire server must be running on the IBM i before you connect.

### Starting Mapepire (on IBM i)

```bash
# SSH into the IBM i, then:
/QOpenSys/pkgs/bin/sc start mapepire
```

To start Mapepire automatically on every system IPL:

```bash
/QOpenSys/pkgs/bin/sc enable mapepire
```

### Connection details prompted at runtime

```
Enter IBM i hostname/IP:  <hostname or IP>
Enter username:           <your IBM i username>
Enter password:           <masked>
Enter port (default 8076): <press Enter for default>
```

---

## Files

| File | Description |
|---|---|
| `qaoa_scheduler.ipynb` | QAOA batch job scheduler - local Aer simulator |
| `qaoa_scheduler_ibm.ipynb` | QAOA batch job scheduler - IBM Quantum Cloud |
| `dbsetup.ipynb` | IBM i database setup (run once) |
| `Dockerfile` | Container image definition |
| `requirements.txt` | Python dependencies (managed by container build) |
| `jupyter_server_config.py` | Jupyter server configuration |
| `.dockerignore` | Docker build exclusions |
