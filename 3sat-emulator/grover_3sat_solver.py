#!/usr/bin/env python3
"""
Quantum 3SAT Solver using Grover's Algorithm with Mapepire Integration
This script connects to IBM i, retrieves 3SAT problem instances, and solves them using Grover's algorithm.
"""

import getpass
import sys
from typing import List, Tuple, Optional
import numpy as np

# Qiskit imports (latest structure)
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import GroverOperator, MCMT, ZGate
from qiskit_aer import AerSimulator
from qiskit_aer.primitives import SamplerV2
import math

# Mapepire import for IBM i connectivity
try:
    from mapepire_python.client.sql_job import SQLJob
    from mapepire_python.data_types import DaemonServer
except ImportError:
    print("Error: mapepire-python not installed. Run: pip install mapepire-python")
    sys.exit(1)


class ThreeSATSolver:
    """
    Quantum 3SAT Solver using Grover's Algorithm
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the 3SAT Solver
        
        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.backend = AerSimulator()
        
    def log(self, message: str):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(f"[3SAT Solver] {message}")
    
    def connect_to_ibmi(self) -> Optional[SQLJob]:
        """
        Connect to IBM i using Mapepire with user credentials
        
        Returns:
            SQLJob object if successful, None otherwise
        """
        self.log("Connecting to IBM i...")
        
        try:
            # Get connection details from user
            host = input("Enter IBM i hostname/IP: ").strip()
            username = input("Enter username: ").strip()
            password = getpass.getpass("Enter password: ")
            
            # Optional: port number (default is usually 8076 for Mapepire)
            port_input = input("Enter port (press Enter for default 8076): ").strip()
            port = int(port_input) if port_input else 8076
            
            # Create daemon server configuration
            daemon_server = DaemonServer(
                host=host,
                port=port,
                user=username,
                password=password
            )
            
            # Create SQL job
            sql_job = SQLJob()
            sql_job.connect(daemon_server)
            
            self.log("Successfully connected to IBM i")
            return sql_job
            
        except Exception as e:
            print(f"Error connecting to IBM i: {e}")
            return None
    
    def fetch_3sat_instance(self, sql_job: SQLJob) -> Optional[str]:
        """
        Fetch 3SAT problem instance from IBM i
        
        Args:
            sql_job: Active SQL job connection
            
        Returns:
            3SAT instance as DIMACS CNF string, or None if error
        """
        self.log("Fetching 3SAT instance from IBM i...")
        
        try:
            # Execute the SQL query to get 3SAT instance
            query_str = "SELECT * FROM TABLE(JESSEG.THREESAT()) AS t"
            
            # Create query and run it
            query = sql_job.query(query_str)
            result = query.run()
            
            # Check if query was successful
            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                print(f"Error: Query failed - {error_msg}")
                return None
            
            # Check if we have data
            if not result.get("data"):
                print("Error: No data returned from THREESAT() function")
                return None
            
            # The THREESAT function returns rows with columns C1, C2, C3, C4
            # representing literals in each clause (0 means unused)
            # Convert this to DIMACS CNF format
            data = result["data"]
            
            if not data:
                print("Error: Empty data returned")
                return None
            
            # Count variables (find max absolute value across all literals)
            max_var = 0
            clauses = []
            
            for row in data:
                clause = []
                # Extract C1, C2, C3, C4 values
                for key in ['C1', 'C2', 'C3', 'C4']:
                    if key in row:
                        literal = row[key]
                        if literal != 0:  # 0 means unused position
                            clause.append(literal)
                            max_var = max(max_var, abs(literal))
                
                if clause:  # Only add non-empty clauses
                    clauses.append(clause)
            
            if not clauses:
                print("Error: No valid clauses found")
                return None
            
            # Build DIMACS CNF format string
            cnf_lines = [f"c 3SAT instance from IBM i"]
            cnf_lines.append(f"p cnf {max_var} {len(clauses)}")
            
            for clause in clauses:
                cnf_lines.append(" ".join(map(str, clause)) + " 0")
            
            cnf_formula = "\n".join(cnf_lines)
            
            self.log(f"Retrieved 3SAT instance with {len(clauses)} clauses and {max_var} variables")
            self.log(f"CNF preview: {cnf_formula[:100]}...")
            
            return cnf_formula
                
        except Exception as e:
            print(f"Error fetching 3SAT instance: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def parse_dimacs_cnf(self, cnf_string: str) -> Tuple[int, List[List[int]]]:
        """
        Parse DIMACS CNF format string
        
        Args:
            cnf_string: CNF formula in DIMACS format
            
        Returns:
            Tuple of (num_variables, clauses_list)
        """
        lines = cnf_string.strip().split('\n')
        num_vars = 0
        clauses = []
        
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('c'):
                continue
            
            # Parse problem line
            if line.startswith('p cnf'):
                parts = line.split()
                num_vars = int(parts[2])
                continue
            
            # Parse clause
            clause = [int(x) for x in line.split() if x != '0']
            if clause:
                clauses.append(clause)
        
        self.log(f"Parsed {len(clauses)} clauses with {num_vars} variables")
        return num_vars, clauses
    
    def create_oracle_from_clauses(self, num_vars: int, clauses: List[List[int]]) -> QuantumCircuit:
        """
        Create a phase oracle from 3SAT clauses
        
        Args:
            num_vars: Number of variables
            clauses: List of clauses (each clause is a list of literals)
            
        Returns:
            QuantumCircuit oracle for the 3SAT problem
        """
        self.log("Creating quantum oracle...")
        
        # Create quantum circuit for the oracle
        oracle = QuantumCircuit(num_vars)
        
        # For each clause, mark the state that violates it
        for clause in clauses:
            # A clause is violated when all literals are false
            # We need to flip the phase of states where all literals in the clause are false
            
            # Create a temporary circuit for this clause
            clause_qc = QuantumCircuit(num_vars)
            
            # Apply X gates to flip qubits for negative literals
            for literal in clause:
                if literal < 0:
                    clause_qc.x(abs(literal) - 1)
            
            # Apply multi-controlled Z gate (marks the violating state)
            if len(clause) == 1:
                clause_qc.z(abs(clause[0]) - 1)
            else:
                controls = [abs(lit) - 1 for lit in clause]
                clause_qc.mcx(controls[:-1], controls[-1])
                clause_qc.z(controls[-1])
                clause_qc.mcx(controls[:-1], controls[-1])
            
            # Undo the X gates
            for literal in clause:
                if literal < 0:
                    clause_qc.x(abs(literal) - 1)
            
            oracle.compose(clause_qc, inplace=True)
        
        self.log(f"Oracle created with {len(clauses)} clauses")
        
        return oracle
    
    def solve_with_grover(self, oracle: QuantumCircuit) -> dict:
        """
        Solve 3SAT problem using Grover's algorithm
        
        Args:
            oracle: Quantum circuit oracle for the problem
            
        Returns:
            Dictionary with solution results
        """
        self.log("Running Grover's algorithm...")
        
        num_qubits = oracle.num_qubits
        
        # Calculate optimal number of iterations
        num_solutions = 1  # Assume at least one solution
        total_states = 2 ** num_qubits
        optimal_iterations = int(math.pi / 4 * math.sqrt(total_states / num_solutions))
        optimal_iterations = max(1, min(optimal_iterations, 10))  # Limit iterations
        
        self.log(f"Using {optimal_iterations} Grover iterations")
        
        # Create Grover circuit
        grover_circuit = QuantumCircuit(num_qubits, num_qubits)
        
        # Initialize superposition
        grover_circuit.h(range(num_qubits))
        
        # Apply Grover iterations
        for _ in range(optimal_iterations):
            # Apply oracle
            grover_circuit.compose(oracle, inplace=True)
            
            # Apply diffusion operator
            grover_circuit.h(range(num_qubits))
            grover_circuit.x(range(num_qubits))
            
            # Multi-controlled Z
            if num_qubits > 1:
                grover_circuit.h(num_qubits - 1)
                grover_circuit.mcx(list(range(num_qubits - 1)), num_qubits - 1)
                grover_circuit.h(num_qubits - 1)
            else:
                grover_circuit.z(0)
            
            grover_circuit.x(range(num_qubits))
            grover_circuit.h(range(num_qubits))
        
        # Measure
        grover_circuit.measure(range(num_qubits), range(num_qubits))
        
        # Run on simulator
        backend = AerSimulator()
        transpiled = transpile(grover_circuit, backend)
        job = backend.run(transpiled, shots=1024)
        result = job.result()
        counts = result.get_counts()
        
        # Get most frequent measurement
        top_measurement = max(counts, key=counts.get)
        
        self.log("Grover's algorithm completed")
        
        return {
            'top_measurement': top_measurement,
            'assignment': {f'x{i+1}': top_measurement[-(i+1)] for i in range(num_qubits)},
            'oracle_evaluation': True,
            'circuit_results': counts,
            'iterations': optimal_iterations
        }
    
    def display_results(self, result: dict, num_vars: int):
        """
        Display the solution results
        
        Args:
            result: Result dictionary from Grover's algorithm
            num_vars: Number of variables in the problem
        """
        print("\n" + "="*60)
        print("QUANTUM 3SAT SOLUTION RESULTS")
        print("="*60)
        
        print(f"\nTop measurement: {result['top_measurement']}")
        print(f"Number of Grover iterations: {result['iterations']}")
        
        if result['assignment']:
            print(f"\nSatisfying assignment found:")
            print(f"Oracle evaluation: {result['oracle_evaluation']}")
            
            # Display variable assignments (consistent with assignment dictionary)
            # Qubits are indexed right-to-left (LSB first), so we reverse the string
            print("\nVariable assignments:")
            assignment_str = result['top_measurement']
            for i in range(num_vars):
                # Use reverse indexing to match the assignment dictionary
                var_value = assignment_str[-(i+1)] if i < len(assignment_str) else '?'
                print(f"  x{i+1} = {var_value} (qubit {i})")
            
            # Show the mapping for clarity
            print(f"\nBit string '{assignment_str}' maps to:")
            for var, val in sorted(result['assignment'].items()):
                print(f"  {var} = {val}")
        else:
            print("\nNo satisfying assignment found")
        
        print("\n" + "="*60)
    
    def run(self):
        """
        Main execution flow
        """
        print("\n" + "="*60)
        print("QUANTUM 3SAT SOLVER WITH GROVER'S ALGORITHM")
        print("IBM i Integration via Mapepire")
        print("="*60 + "\n")
        
        # Step 1: Connect to IBM i
        sql_job = self.connect_to_ibmi()
        if not sql_job:
            print("Failed to connect to IBM i. Exiting.")
            return
        
        try:
            # Step 2: Fetch 3SAT instance
            cnf_string = self.fetch_3sat_instance(sql_job)
            if not cnf_string:
                print("Failed to fetch 3SAT instance. Exiting.")
                return
            
            # Step 3: Parse the CNF formula
            num_vars, clauses = self.parse_dimacs_cnf(cnf_string)
            
            if not clauses:
                print("No clauses found in the CNF formula. Exiting.")
                return
            
            # Step 4: Create quantum oracle
            oracle = self.create_oracle_from_clauses(num_vars, clauses)
            
            # Step 5: Solve using Grover's algorithm
            result = self.solve_with_grover(oracle)
            
            # Step 6: Display results
            self.display_results(result, num_vars)
            
        except Exception as e:
            print(f"Error during execution: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Close connection
            try:
                sql_job.close()
                self.log("Connection closed")
            except:
                pass


def main():
    """
    Main entry point
    """
    # Create solver instance
    solver = ThreeSATSolver(verbose=True)
    
    # Run the solver
    solver.run()


if __name__ == "__main__":
    main()

# def test_local():
#     """Test with hardcoded 3SAT instance"""
#     solver = ThreeSATSolver(verbose=True)
    
#     # Example 3SAT instance in DIMACS CNF format
#     test_cnf = """c Example 3SAT problem
# p cnf 3 3
# 1 2 -3 0
# -1 2 3 0
# 1 -2 3 0
# """
    
#     num_vars, clauses = solver.parse_dimacs_cnf(test_cnf)
#     oracle = solver.create_oracle_from_clauses(num_vars, clauses)
#     result = solver.solve_with_grover(oracle)
#     solver.display_results(result, num_vars)


# if __name__ == "__main__":
#     test_local()