#! /usr/bin/python3

import sys
import pennylane as qml
import numpy as np


def variational_ansatz(params, wires):
    """The variational ansatz circuit.

    Fill in the details of your ansatz between the # QHACK # comment markers. Your
    ansatz should produce an n-qubit state of the form

        a_0 |10...0> + a_1 |01..0> + ... + a_{n-2} |00...10> + a_{n-1} |00...01>

    where {a_i} are real-valued coefficients.

    Args:
         params (np.array): The variational parameters.
         wires (qml.Wires): The device wires that this circuit will run on.
    """

    # QHACK #
    n = len(wires)

    dev = qml.device('default.qubit', wires = n)
   


    def F_gate(i,j,n,k,theta) :
        #theta = np.arccos(np.sqrt(1/(n-k+1)))
        qml.RY(-theta,wires=[j])       
        qml.CZ(wires=[i, j])
        qml.RY(theta,wires =[j])
        #circ.barrier(q[i])
        

    
    qml.PauliX(n-1) #start is |10000>

    for i in range(1,n):
        F_gate(n-i,n-i-1,n,i,params[i-1]) # Applying F12

    for j in range(1,n):
        qml.CNOT(wires=[n-j-1,n-j])


    #return qml.state()
    #return qml.probs(wires=[0, 1,2])



# QHACK #


def run_vqe(H):
    """Runs the variational quantum eigensolver on the problem Hamiltonian using the
    variational ansatz specified above.

    Fill in the missing parts between the # QHACK # markers below to run the VQE.

    Args:
        H (qml.Hamiltonian): The input Hamiltonian

    Returns:
        The ground state energy of the Hamiltonian.
    """
    energy = 0

    # QHACK #

    # Initialize the quantum device
    n = len(H.wires)
    dev = qml.device('default.qubit', wires = n)
    
  
    # Randomly choose initial parameters (how many do you need?)
    params = np.random.uniform(low=-np.pi / 2, high=np.pi / 2, size=(n-1,))
    

    # Set up a cost function
    opt = qml.AdamOptimizer(stepsize=0.2, beta1=0.9, beta2=0.99, eps=1e-08)
    
    #opt = qml.MomentumOptimizer(stepsize=0.01, momentum=0.99)

    steps = 600

    cost_fn = qml.ExpvalCost(variational_ansatz, H, dev)
    
    

    for i in range(steps):
        
        params, prev_energy= opt.step_and_cost(cost_fn, params)
        energy = cost_fn(params)
        conv = np.abs(energy - prev_energy)
       
        #if i % 4 == 0:
            #print("Iteration = {:},  E = {:.8f} Ha".format(i, energy))

        if conv <= 1e-06:
            break


    # QHACK #

    # Return the ground state energy
    return energy


def pauli_token_to_operator(token):
    """
    DO NOT MODIFY anything in this function! It is used to judge your solution.

    Helper function to turn strings into qml operators.

    Args:
        token (str): A Pauli operator input in string form.

    Returns:
        A qml.Operator instance of the Pauli.
    """
    qubit_terms = []

    for term in token:
        # Special case of identity
        if term == "I":
            qubit_terms.append(qml.Identity(0))
        else:
            pauli, qubit_idx = term[0], term[1:]
            if pauli == "X":
                qubit_terms.append(qml.PauliX(int(qubit_idx)))
            elif pauli == "Y":
                qubit_terms.append(qml.PauliY(int(qubit_idx)))
            elif pauli == "Z":
                qubit_terms.append(qml.PauliZ(int(qubit_idx)))
            else:
                print("Invalid input.")

    full_term = qubit_terms[0]
    for term in qubit_terms[1:]:
        full_term = full_term @ term

    return full_term


def parse_hamiltonian_input(input_data):
    """
    DO NOT MODIFY anything in this function! It is used to judge your solution.

    Turns the contents of the input file into a Hamiltonian.

    Args:
        filename(str): Name of the input file that contains the Hamiltonian.

    Returns:
        qml.Hamiltonian object of the Hamiltonian specified in the file.
    """
    # Get the input
    coeffs = []
    pauli_terms = []

    # Go through line by line and build up the Hamiltonian
    for line in input_data.split("S"):
        line = line.strip()
        tokens = line.split(" ")

        # Parse coefficients
        sign, value = tokens[0], tokens[1]

        coeff = float(value)
        if sign == "-":
            coeff *= -1
        coeffs.append(coeff)

        # Parse Pauli component
        pauli = tokens[2:]
        pauli_terms.append(pauli_token_to_operator(pauli))

    return qml.Hamiltonian(coeffs, pauli_terms)


if __name__ == "__main__":
    # DO NOT MODIFY anything in this code block

    # Turn input to Hamiltonian
    H = parse_hamiltonian_input(sys.stdin.read())

    # Send Hamiltonian through VQE routine and output the solution
    ground_state_energy = run_vqe(H)
    print(f"{ground_state_energy:.6f}")
