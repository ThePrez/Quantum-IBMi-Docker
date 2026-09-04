# Quantum 3SAT Solver - Jupyter Notebooks

Jupyter notebooks for solving 3SAT problems using Grover's quantum algorithm with IBM i database integration via Mapepire. Runs either on the local Aer simulator or on real IBM Quantum hardware.

---

## Notebooks

| Notebook | Purpose |
|---|---|
| `dbsetup.ipynb` | One-time IBM i database setup - creates the `JESSEG.THREESAT()` function |
| `3sat.ipynb` | Quantum 3SAT solver using the - **local Aer simulator** |
| `3sat-ibm.ipynb` | Quantum 3SAT solver running on a real - **IBM Quantum device** |

### `dbsetup.ipynb`
- Prompts for IBM i connection details
- Creates the `JESSEG` schema and `THREESAT()` table function with embedded sample data
- Verifies the function returns correct clause data

### `3sat.ipynb` - Local Simulator
- Connects to IBM i via Mapepire and fetches 3SAT instances
- Builds a `PhaseOracleGate` oracle from the CNF clauses
- Runs 1 iteration of Grover's algorithm on the local Aer simulator
- Verifies each clause in the returned solution and visualizes results

### `3sat-ibm.ipynb` - IBM Quantum Cloud
- Same workflow as `3sat.ipynb` but submits the circuit to a real IBM Quantum device
- Prompts for the IBM Quantum API key at runtime (masked input - never stored in notebook)
- Uses `SamplerV2` + `generate_preset_pass_manager` for ISA transpilation
- Prints the Job ID and a tracking URL so results can be retrieved if the session disconnects

---

## Running the Notebooks

### Option 1: Docker (Recommended)

```bash
# From inside the 3sat-emulator/ directory:
docker build -t quantum-3sat-jupyter .
docker run -p 8888:8888 quantum-3sat-jupyter
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
2. Run `3sat.ipynb` - solves 3SAT on the local simulator

### IBM Quantum Cloud

1. Run `dbsetup.ipynb` - sets up the IBM i database (one time only)
2. Obtain your IBM Quantum API key (see [IBM Quantum API Key](#ibm-quantum-api-key) below)
3. Run `3sat-ibm.ipynb` - submits the circuit to real quantum hardware

---

## IBM Quantum API Key

The API key (also called *API token*) authenticates your access to [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com). When you run `3sat-ibm.ipynb` you will be prompted:

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
backend = service.backend("ibm_brisbane")
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

After submission the notebook prints:

```
Job ID : abc123xyz
Track  : https://quantum.cloud.ibm.com/jobs/abc123xyz
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

Both solver notebooks connect to IBM i using [Mapepire](https://github.com/Mapepire-IBMi). The Mapepire server must be running on the IBM i before you connect.

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
| `3sat.ipynb` | Quantum 3SAT solver - local Aer simulator |
| `3sat-ibm.ipynb` | Quantum 3SAT solver - IBM Quantum Cloud |
| `dbsetup.ipynb` | IBM i database setup (run once) |
| `Dockerfile` | Container image definition |
| `requirements.txt` | Python dependencies (managed by container build) |
| `jupyter_server_config.py` | Jupyter server configuration |
| `odbc.ini` | ODBC configuration (optional) |
