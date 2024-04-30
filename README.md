# Source Code for Protocol KEP-AP-CC

This repository contains the source code for the privacy-preserving protocol KEP-AP-CC presented in the paper:
Efficient Integration of Exchange Chains in Privacy-Preserving Kidney Exchange.

The source code of the protocol KEP_AP_CC for chains of maximum length 3 and 4 is available in the files `smpc_protocols/Programs/Source/KEP_AP_CC_3.mpc` and `smpc_protocols/Programs/Source/KEP_AP_CC_4.mpc`, respectively. Note that due to the inner workings of MP-SPDZ, we provide two different files for chain length 3 and 4. One reason is that MP-SPDZ does not allow for any other control structures than `for_range_parallel` inside a parallelized loop. Hence, case distinctions based on the maximum chain length would be difficult to handle in parallelized loops if we used the same file for both values of the maximum chain length.

The two scripts `setup_mpspdz.py` and `run_kep_ap_cc.py` can be used to setup MP-SPDZ and run an example execution of the protocol.

## Setup

### Python Requirements
- Tested for Python 3.11
- Packages listed in requirements.txt: `pip install -r requirements.txt`

The assumption in this file is that python is installed as `python` and pip as `pip`.

### Setup of MP-SPDZ
Our protocol is implemented using the secure multi-party computation benchmarking framework [MP-SPDZ](https://github.com/data61/MP-SPDZ). 
The requirements for MP-SPDZ are stated in the corresponding README file of MP-SPDZ: https://github.com/data61/MP-SPDZ/blob/v0.3.5/README.md.

After installing these requirements, execute: `python setup_mpspdz.py`

This downloads the correct version of MP-SPDZ and sets up all remaining files for running the protocols.

## Protocol Execution

Execute the following command to run the protocol KEP-AP-CC:

`python run_kep_ap_cc.py <number of patient-donor pairs and altruistic donors> <maximum chain length> <SMPC primitive>`

If you do not explicitly specify a number of patient-donor pairs and altruistic donors, the protocol is executed for three patient-donor pairs and if you do not explicitly specify a maximum chain length, the protocol is executed for maximum chain length 3. Note that compilation times and RAM consumption can grow large for large numbers of patient-donor pairs and altruistic donors. For further details on the protocol specification we refer to the source code itself or to our paper.

If you do not explicitly specify an SMPC primitive, the primitive `ps-rep-ring` is chosen. This is also the SMPC primitive that is used in our evaluation in Section V of the paper. The other two available options for the SMPC primitive are `rep-ring`, which is a semi-honest version of `ps-rep-ring`, and `semi2k`, which is a primitive with security in the semi-honest model for a dishonest majority. For further details on the differences among these SMPC primitives, we refer the documentation of MP-SPDZ: https://mp-spdz.readthedocs.io/en/latest/readme.html#protocols

The protocol output is printed to the command line and it indicates the exchange partner for patient and donor of each patient-donor pair and altruistic donor. If the pair or altruistic donor is not part of an exchange, this is indicated by the value 0 in the output. Also the donor for the patient of an altruistic donor and the recipient for the last donor in a chain are always indicated by the value 0.

Note that the output can differ for the same inputs due to the random shuffling of the adjacency matrix at the beginning of the protocol execution.

### Input encoding 
There are four example input files in the directory `smpc_protocols/Inputs/`. The rows of each input file contain:
- row 1: donor bloodtype indicator vector
- rows 2-7: donor HLA indicator vectors for A, B, C, DR, DQ, and DP loci
- row 8: patient bloodtype indicator vector
- rows 9-14: patient antibody indicator vectors for HLA-A, -B, -C, -DR, -DQ, and -DP loci
- row 15: altruist bit
- row 16: pre-score
- rows 17-19: patient HLA indicator vectors for A, B, and DR loci
- rows 20-21: transplant center of patient and donor

If the protocol is run for more than three input peers, additional input files are created. These contain random values for the blood types and the prioritization input, and all values of the HLA indicator vectors are set to 0. 
Note that the inputs do not contain real-world data for kidney exchange. Especially, the generated compatibility graphs are much denser than in a real-world setting since using "all zero" HLA indicator vectors reduces the compatibility check to blood type compatibility only.


## Licenses
This repository contains licensed code, here is a comprehensive list of all third party code used:

#### MP-SPDZ
Our protocol is implemented using the secure multi-party computation benchmarking framework MP-SPDZ :

- MP-SPDZ: copyright (c) 2023, Commonwealth Scientific and Industrial Research Organisation (CSIRO) ABN 41 687 119 230. See https://github.com/data61/MP-SPDZ/blob/v0.3.5/License.txt for details.


Besides using MP-SPDZ as the underlying framework for our protocol, we adapted the client-server infrastructure that MP-SPDZ (https://github.com/data61/MP-SPDZ) uses for External IO to our use case. 
In particular, the file `smpc_protocols/Programs/Compiler/networking.py` for client communication is adapted from the bankers bonus example for external IO provided by MP-SPDZ (https://github.com/data61/MP-SPDZ/blob/v0.3.5/Programs/Source/bankers_bonus.mpc). 
The code was modified in some places such that it can handle the specific inputs and outputs of our kidney exchange protocol. 
The license for MP-SPDZ can be found in the file itself as well as in the linked repository (https://github.com/data61/MP-SPDZ/blob/v0.3.5/License.txt).
