# README

## Introduction

This project implements a Markov Decision Process (MDP) in Python. It allows for the simulation and analysis of MDPs based on user-specified input files. The project also includes functionalities for statistical model checking (SMC) and reinforcement learning (RL).

## Installation

Before starting, ensure you have installed the necessary libraries. You can install them via pip:

```sh
pip install antlr4-python3-runtime numpy networkx matplotlib click
```

## Usage

### File Structure

Input files must be in the `.mdp` format and define the states, actions, and transitions of the MDP. Here is an example structure of an `.mdp` file:

```
States S0 : 1, S1 : 2, S2 : 3;
Actions a,b,c;
S0 -> 5:S1 + 5:S2;
S1[b] -> 2: S1 + 8:S0;
S1[a] -> 1:S2+3:S0+6:S1;
S2[c] -> 5:S0 + 5:S1;
```

### Running the Script

To run the script, execute the following command in the terminal:

```sh
python mdp.py
```

The script will prompt you for the name of the input file. Provide the name of the `.mdp` file you want to use.

### Main Functions

The script includes several main functions:

- `presentation_suite(mode_auto)`: Presents the next possible actions in the MDP.
- `algo_it_valeurs()`: Implements the value iteration algorithm for reinforcement learning.
- `s_proba(a)`: Calculates the probabilities of transitions.
- `prochain_etat(somme_proba)`: Determines the next state based on calculated probabilities.
- `avance(a, model_checked)`: Advances the simulation by one step.
- `initialisation()`: Initializes the simulation parameters by interacting with the user.
- `model_checking(nbr_tour)`: Performs statistical model checking.
- `plot_graph()`: Generates a graphical visualization of the MDP.

### Model Verification

Before starting the simulation, the model is verified to ensure that all actions and states are correctly defined, and there is no mixing between MDP and Markov Chain (MC).

### Simulation

The simulation can be run in manual or automatic mode. In automatic mode, the user can choose to use reinforcement learning to optimize the decisions made.

### Statistical Model Checking (SMC)

Quantitative and qualitative SMC is performed to verify the properties of the model. The results of the checks are displayed after execution.

## Example Output

After running the script, the following results will be displayed:

- The states, actions, and transitions of the model.
- The results of the statistical model checking.
- The optimized state values if reinforcement learning is used.
- A graphical visualization of the MDP.
- The history of visited states and the accumulated reward.

## Conclusion

This project offers a robust platform for the simulation and analysis of MDPs, with advanced features such as statistical model checking and reinforcement learning. Users can easily define their own MDPs through `.mdp` input files and use the provided tools to explore and optimize these models.

Thank you for using this project, and feel free to suggest improvements or report bugs.