# QAOA Scheduler — Run Results Analysis

**Date:** September 2026  
**Author:** Het Patel  
**Notebooks analysed:** `qaoa_scheduler.ipynb` (local Aer) · `qaoa_scheduler_ibm.ipynb` (IBM Quantum Cloud)

---

## 1. What Ran and What Succeeded

Both notebooks executed end-to-end without crashing. The full pipeline — IBM i connection → QUBO build → Ising conversion → circuit construction → optimisation → decode → write-back — completed in both variants.

| Step | Local (Aer MPS) | IBM Quantum (ibm_fez) |
|---|---|---|
| IBM i connect (Mapepire) | ✅ | ✅ |
| JOBQUEUE() fetch (8 jobs) | ✅ | ✅ |
| QUBO build (32 variables) | ✅ | ✅ |
| Ising Hamiltonian (80 Pauli terms) | ✅ | ✅ |
| QAOA circuit build (32 qubits, depth 20) | ✅ | ✅ |
| ISA transpilation | n/a (MPS, no transpile) | ✅ depth 78, 156 qubits |
| COBYLA optimisation | ✅ 30 iterations | ✅ 10 iterations |
| Schedule decoded | ✅ | ✅ |
| Write-back to QSCHEDULE.SCHEDULE_RESULTS | ✅ | ✅ |
| Gantt chart rendered | ✅ | ✅ |

---

## 2. Actual Results

### 2a. Local Aer Simulator (`qaoa_scheduler.ipynb`)

| Metric | Value |
|---|---|
| Backend | AerSimulator — `matrix_product_state` |
| QAOA layers (p) | 1 |
| Optimal γ | 0.3022 |
| Optimal β | −0.0768 |
| Final QUBO cost | 102.27 |
| COBYLA iterations | 30 |
| Top bitstring | `10110001010010111010101001010100` |
| Top bitstring frequency | 1 / 1024 shots (0.1%) |
| Estimated makespan | 185 minutes |

**Decoded schedule:**

| Slot | Jobs | Memory |
|---|---|---|
| 1 | INVUPD, SALESRPT, TAXCALC, SHIPCONF | 1024 MB |
| 2 | GLCLOSE, ARAGING | 1024 MB |
| 3 | PAYROLL, BACKUPDB | 640 MB |
| 4 | *(empty)* | 0 MB |

**Dependency violations (2 of 4 dependent jobs):**
- `GLCLOSE` must run **after** PAYROLL — placed in Slot 2, PAYROLL in Slot 3 ✗
- `TAXCALC` must run **after** PAYROLL — placed in Slot 1, PAYROLL in Slot 3 ✗

---

### 2b. IBM Quantum Cloud (`qaoa_scheduler_ibm.ipynb`)

| Metric | Value |
|---|---|
| Backend | ibm_fez (initially connected to ibm_marrakesh) |
| QAOA layers (p) | 1 |
| Optimal γ | 0.0438 |
| Optimal β | 0.3688 |
| Final QUBO cost | 336.57 |
| COBYLA iterations | **10** (maxiter was reduced to 10) |
| Job ID | `daodavdr85ps73ff4d60` |
| Tracking URL | https://quantum.cloud.ibm.com/jobs/daodavdr85ps73ff4d60 |
| Top bitstring | `00110110101101011101101110111011` |
| Top bitstring frequency | 1 / 1024 shots (0.1%) |
| Estimated makespan | 125 minutes |

**Decoded schedule:**

| Slot | Jobs | Memory |
|---|---|---|
| 1 | PAYROLL, INVUPD, GLCLOSE, ARAGING, SALESRPT, BACKUPDB, SHIPCONF | **2176 MB** ⚠️ |
| 2 | TAXCALC | 512 MB |
| 3 | *(empty)* | 0 MB |
| 4 | *(empty)* | 0 MB |

**Dependency violations (3 of 4 dependent jobs):**
- `GLCLOSE` must run after PAYROLL — both in Slot 1 ✗
- `ARAGING` must run after INVUPD — both in Slot 1 ✗
- `BACKUPDB` must run after GLCLOSE — both in Slot 1 ✗
- `TAXCALC` must run after PAYROLL — Slot 1 → Slot 2 ✓

**Additional issue:** Slot 1 uses 2176 MB, exceeding the 2048 MB memory pool constraint.

---

## 3. What Went Wrong / Gaps

### 3a. Optimisation quality is poor — both runs

The top bitstring appeared only **1 time in 1024 shots** in both variants. In a well-optimised QAOA run, the target solution(s) should concentrate probability mass and appear far more frequently. A frequency of 1/1024 is indistinguishable from random noise over 2³² possible bitstrings.

**Root causes:**

| Issue | Detail |
|---|---|
| **p=1 is insufficient** | With only 1 QAOA layer, the cost landscape has very little expressibility for a 32-qubit problem with 80 Pauli terms. Standard QAOA theory shows that p needs to scale with problem hardness. A 32-variable QUBO with dependencies typically needs p ≥ 3–5 to show useful bias. |
| **COBYLA maxiter too low (IBM run)** | The IBM Cloud run used `maxiter=10` (changed from the designed 100). COBYLA stopped after just 10 function evaluations — barely enough to leave the initial point. The local run used 30 iterations and got a meaningfully lower cost (102 vs 337). |
| **Shot noise dominates at p=1** | With 1024 shots spread over 2³² states, each evaluation is extremely noisy. COBYLA is a deterministic optimiser not designed for stochastic objectives — it interprets shot noise as signal, degrading convergence. |
| **No warm-start or parameter initialisation strategy** | Both runs start from (γ=0.5, β=0.5). There is no grid pre-search or analytical warm-start. For p=1, the optimal γ is known to correlate with the problem's spectral gap; a smarter initialisation would help. |

### 3b. Dependency constraints violated in both runs

QAOA violated 2/4 dependency constraints (local) and 3/4 (IBM hardware). This is directly caused by the weak optimisation — the algorithm has not converged anywhere near the feasible region of the QUBO.

The dependency penalty weight (`penalty_dependency=20.0`) should in theory dominate, but:
- The one-hot reward (`-10` on diagonal) partially cancels it for certain assignments.
- With p=1, the cost unitary doesn't have enough layers to "route" probability away from violating states.

### 3c. Memory constraint violated (IBM hardware run)

Slot 1 in the IBM hardware result contains 7 jobs using 2176 MB, exceeding the 2048 MB pool. The memory penalty (`penalty_memory=5.0`) is the weakest penalty weight and is clearly not strong enough relative to the one-hot reward to prevent over-packing at this optimisation depth.

### 3d. Transpilation inflates the IBM circuit significantly

The 32-qubit, depth-20 abstract circuit becomes a **156-qubit, depth-78** ISA circuit after transpilation to ibm_fez. This is a 3.9× depth increase from routing/SWAP insertion alone. At depth 78 on a real device, gate error accumulation is significant — the hardware results are substantially noisier than the simulator results, compounding the already-weak optimisation.

### 3e. No benchmark comparison

There is no classical baseline (e.g. greedy priority-first schedule) to compare the QAOA result against. Without knowing what a good makespan looks like, it is impossible to say how far the current result is from optimal. A trivial greedy scheduler would likely outperform both QAOA runs.

### 3f. Histogram visualisation empty in local run

Cell 12 in `qaoa_scheduler.ipynb` rendered an empty figure (`Figure size 640x480 with 0 Axes`). The `plot_histogram` call returned a figure that was not captured by `plt.show()` correctly — this is a Qiskit visualisation/display integration issue specific to the `matrix_product_state` path where counts have a different format.

---

## 4. What Could Be Improved

### Priority 1 — Fix optimisation convergence

```python
# Increase QAOA layers
QAOA_LAYERS = 3  # minimum meaningful for this problem size

# Restore full COBYLA budget on IBM hardware
options={"maxiter": 100, "rhobeg": 0.5}

# Increase shots to reduce gradient noise
SHOTS = 2048
```

Alternatively, switch from COBYLA to a gradient-based optimiser using the **parameter-shift rule** via Qiskit's `EstimatorV2`, which is designed for noisy quantum objectives.

### Priority 2 — Rebalance QUBO penalty weights

The dependency and memory penalties need to dominate the one-hot cost more strongly. Suggested starting point:

```python
penalty_one_hot=5.0,        # reduced from 10
penalty_dependency=50.0,    # raised from 20
penalty_memory=15.0,        # raised from 5
```

### Priority 3 — Add a classical baseline

Add one cell computing a greedy schedule (sort by priority, respect dependencies) for comparison. This gives the QAOA result context and makes the notebook a proper demonstration.

### Priority 4 — Fix the histogram display (local run)

Replace `plot_histogram` → `plt.show()` with an explicit figure assignment:

```python
fig = plot_histogram(top_counts, title="...", figsize=(12, 5))
plt.tight_layout()
display(fig)
plt.close()
```

### Priority 5 — IBM hardware: use the cloud simulator for development

During development and debugging, use:
```python
backend = service.least_busy(simulator=True)
```
This avoids queue time and hardware noise while retaining the full Qiskit Runtime API path. Only switch to real hardware once the optimisation is producing feasible schedules on the simulator.

### Priority 6 — Reduce circuit width for real hardware

32 qubits × 4 slots is too large for current NISQ devices with p ≥ 2. Consider:
- Reducing to 4 jobs × 3 slots = 12 qubits for hardware demonstration runs
- Keeping the full 8-job version for the Aer simulator only

### Priority 7 — Makespan calculation includes empty slots

The current `compute_makespan` sums `max(duration)` per slot including slots with no jobs, inflating the number. An empty slot contributes 0 but slots should only count if occupied:

```python
return sum(v for v in slot_durations.values() if v > 0)
```

---

## 5. PR Readiness Assessment

### ❌ Not ready for PR in current state

The module is **architecturally complete and runs end-to-end**, but the quantum results are not meaningful. Merging now would document an algorithm that produces constraint-violating, near-random schedules. A reviewer would correctly flag this as a proof-of-infrastructure rather than a proof-of-concept.

**Minimum bar before PR:**
1. Fix the COBYLA iteration count on the IBM hardware notebook (restore `maxiter=100`)
2. Increase `QAOA_LAYERS` to at least 2–3 in both notebooks
3. Fix the histogram display bug in the local notebook
4. Add a classical greedy baseline cell for comparison
5. Run both notebooks again and verify at least 6/8 dependency constraints are satisfied in the Aer result

**What is already PR-ready:**
- All infrastructure: Docker, `requirements.txt`, Dockerfile, `odbc.ini`, `jupyter_server_config.py`
- `dbsetup.ipynb` — correct and complete
- The QUBO construction logic — mathematically sound
- The Ising conversion (`qubo_to_ising`) — correct
- The circuit builder (`build_qaoa_circuit`) — correct
- IBM i write-back pipeline — working
- Mapepire connection pattern — consistent with `3sat-emulator`
- Security model (masked `getpass`, no stored credentials)
- README documentation

---

## 6. Summary

| Dimension | Status |
|---|---|
| End-to-end pipeline | ✅ Complete and working |
| IBM i integration (Mapepire) | ✅ Solid |
| QUBO formulation | ✅ Mathematically correct |
| Ising / circuit construction | ✅ Correct |
| Optimisation convergence | ❌ Not converged (p=1, maxiter too low) |
| Constraint satisfaction | ❌ 2–3 dependency violations per run |
| Hardware noise handling | ❌ 32-qubit circuit too wide for NISQ at p>1 |
| Visualisation | ⚠️ Histogram broken in local run |
| Classical benchmark | ❌ Missing |
| Documentation | ✅ Good |
| Security (credentials) | ✅ Correct (getpass, never stored) |
| PR readiness | ❌ Needs 3–4 targeted fixes first |
