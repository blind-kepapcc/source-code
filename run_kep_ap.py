import os
import subprocess
import shutil
import re
import random
import sys

WARNING_COLOR = "\033[92m"
END_COLOR = "\033[0m"
OUTPUT_COLORS = ["\033[94m", "\033[95m", "\033[96m", "\033[91m"]


def execute(cmd, currwd, prnt):
    """
    Helper method. Wraps around subprocess Popen.
    Executes one command after printing a descriptor, then continually prints that commands output/err.
    """

    print(prnt)

    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=currwd, universal_newlines=True)

    for line in popen.stdout:
        print(line, end='')

    popen.stdout.close()
    return_code = popen.wait()

    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def generate_random_input(input_peers):
    """
    Create random example inputs for those input peers for which no input data is specified under 'protocols/Inputs'.
    """

    for i in range(input_peers):
        f_name = f"smpc_protocols/Inputs/input_{i}.txt"
        if os.path.isfile(f_name):
            continue
        print("Generating random input for client " + str(i))

        altruist = False
        if random.random() < 0.1:
            altruist = True

        with open(f_name, "w") as file:
            # meaning: Bloodtype indicator, HLA-A, -B, -C, -DR, -DQ, -DP
            input_lengths = [4, 59, 132, 48, 61, 26, 22]
            donor_blood_type = random.randint(0, 3)
            patient_blood_type = random.randint(0, 3)
            for k in input_lengths:
                if k == 4:
                    if donor_blood_type == 0:
                        donor_bloodtype_indicator = "1 1 1 1\n"
                    elif donor_blood_type == 1:
                        donor_bloodtype_indicator = "0 1 0 1\n"
                    elif donor_blood_type == 2:
                        donor_bloodtype_indicator = "0 0 1 1\n"
                    else:
                        donor_bloodtype_indicator = "0 0 0 1\n"
                    file.write(donor_bloodtype_indicator)
                else:
                    for j in range(k - 1):
                        file.write("0 ")
                    file.write("0\n")

            for k in input_lengths:
                if k == 4:
                    if altruist:
                        file.write("0 0 0 0\n")
                    else:
                        if patient_blood_type == 0:
                            patient_bloodtype_indicator = "1 0 0 0\n"
                        elif patient_blood_type == 1:
                            patient_bloodtype_indicator = "0 1 0 1\n"
                        elif patient_blood_type == 2:
                            patient_bloodtype_indicator = "0 0 1 1\n"
                        else:
                            patient_bloodtype_indicator = "1 1 1 1\n"
                        file.write(patient_bloodtype_indicator)
                else:
                    if altruist:
                        for j in range(k - 1):
                            file.write("0 ")
                        file.write("0\n")
                    else:
                        for j in range(k - 1):
                            file.write("0 ")
                        file.write("0\n")

            # add altruist bit
            if altruist:
                file.write("1\n")
            else:
                file.write("0\n")

            # add random pre-score
            file.write(str(random.randint(0, 200)) + "\n")
            prio_input_lengths = [59, 132, 61]
            for k in prio_input_lengths:
                for j in range(k - 1):
                    file.write("0 ")
                file.write("0\n")
            # add random patient and donor center
            center = random.randint(0, 30)
            file.write(str(center) + "\n")
            file.write(str(center) + "\n")


def compile_code(clients, smpc_primitive, computing_peers, ke_protocol):
    # modify the mpc files for the current number of clients
    with open("smpc_protocols/Programs/Source/"+ke_protocol+".mpc", "r") as file:
        text = file.read()

    text = re.sub(r"NUM_NODES = \d+", f"NUM_NODES = {clients}", text)
    s_len_two = int(clients * (clients - 1) / 2)
    s_len_three = int(clients * (clients - 1) * (clients - 2) / 6)
    s_len_four = int(clients * (clients - 1) * (clients - 2) * (clients - 3) / 24)
    if ke_protocol == "KEP_AP_CC_4":
        text = re.sub(r"S_LENGTH = \d+", f"S_LENGTH = {s_len_two + s_len_three+s_len_four}", text)
    else:
        text = re.sub(r"S_LENGTH = \d+", f"S_LENGTH = {s_len_two + s_len_three}", text)
    text = re.sub(r"S_LENGTH_TWO = \d+", f"S_LENGTH_TWO = {s_len_two}", text)
    text = re.sub(r"S_LENGTH_THREE = \d+", f"S_LENGTH_THREE = {s_len_three}", text)
    if ke_protocol == "KEP_AP_CC_4":
        text = re.sub(r"S_LENGTH_FOUR = \d*", f"S_LENGTH_FOUR = {s_len_four}", text)

    if computing_peers == 2:
        text = re.sub(r"program.use_split\(3\)", r"program.use_split(2)", text)
    elif computing_peers == 3:
        text = re.sub(r"program.use_split\(2\)", r"program.use_split(3)", text)

    with open("smpc_protocols/Programs/Source/" + ke_protocol + ".mpc", "w+") as file:
        file.write(text)

    # copy the inputs of the patient-donor pairs to the MP-SPDZ directory
    try:
        execute(["rm", "-r", "./ExternalIO/Inputs/"], "./MPSPDZ/", "\n\nRemoving old Input Data")
    except subprocess.CalledProcessError:
        line = "No old Input Data available.\n\n"
        print(f"{WARNING_COLOR}{line}{END_COLOR}", end='')

    execute(["cp", "-r", "../smpc_protocols/Inputs/", "./ExternalIO/"], "./MPSPDZ/", "\n\nCopying Input Data")
    execute(["cp", "Programs/Source/" + ke_protocol + ".mpc", "../MPSPDZ/Programs/Source/"], "./smpc_protocols",
            "\n\nCopying MPC file")

    # copy the custom code to the MP-SPDZ directory
    with open("smpc_protocols/deltas.txt", "r") as deltas:
        for line in deltas:
            target = line.split(">")
            target = [elem.strip() for elem in target]
            try:
                if os.path.exists(target[1]):
                    shutil.rmtree(target[1])
                shutil.copytree(target[0], target[1])
            except NotADirectoryError:
                shutil.copy(target[0], target[1])

    # Cleanup the old player data
    try:
        execute(["rm", "-r", "./Player-Data/", "../smpc_protocols/Player-Data/"], "./MPSPDZ/",
                "\n\nRemoving old Player Data")
    except subprocess.CalledProcessError:
        line = "No old Player Data available.\n\n"
        print(f"{WARNING_COLOR}{line}{END_COLOR}", end='')

    # run the setup scripts for the computing peers and the patient-donor pairs
    try:
        execute(["./Scripts/tldr.sh"], "./MPSPDZ/", "\n\nExecuting 'tldr.sh'")
        execute(["./Scripts/setup-ssl.sh", str(computing_peers)], "./MPSPDZ/", "\n\nExecuting 'setup-ssl.sh'")
        execute(["./Scripts/setup-clients.sh", str(clients)], "./MPSPDZ/", "\n\nExecuting 'setup-clients.sh'")

    except subprocess.CalledProcessError:
        line = "MPSPDZ setup scripts returned exit status 1. If this is your first compilation run please abort and fix here.\n\n"
        print(f"{WARNING_COLOR}{line}{END_COLOR}", end='')

    if smpc_primitive == "semi2k-party.x" or smpc_primitive == "ps-rep-ring-party.x" or smpc_primitive == "replicated-ring-party.x":
        # compile the MP-SPDZ program
        execute(["./compile.py", "-R", "64", ke_protocol], "./MPSPDZ", "\n\nExecuting /MPSPDZ/compile.py "+ke_protocol)


def run(clients, smpc_primitive, computing_peers, ke_protocol):
    # start all computing peers
    popen_first = subprocess.Popen(
        ["./" + str(smpc_primitive), "-h",
         "localhost", "0", ke_protocol],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="./MPSPDZ", universal_newlines=True)

    for i in range(1, computing_peers):
        subprocess.Popen(
            ["./" + str(smpc_primitive), "-h",
             "localhost", str(i),
             ke_protocol], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd="./MPSPDZ", universal_newlines=True)

    # start sending the input of the patient-donor pairs
    popen_clients = []

    for i in range(int(clients)):
        if i == (int(clients) - 1):
            popen_clients.append(
                subprocess.Popen(
                    ["python", "ExternalIO/kidney-exchange-client.py", str(i), str(computing_peers), str(clients), "1"],
                    stdout=subprocess.PIPE, cwd="./MPSPDZ", universal_newlines=True))
        else:
            popen_clients.append(
                subprocess.Popen(
                    ["python", "ExternalIO/kidney-exchange-client.py", str(i), str(computing_peers), str(clients), "0"],
                    stdout=subprocess.PIPE, cwd="./MPSPDZ", universal_newlines=True))

    for line in popen_first.stdout:
        print(f"{WARNING_COLOR}{line}{END_COLOR}", end='')

    for i in range(len(popen_clients)):
        for line in popen_clients[i].stdout:
            print(f"{OUTPUT_COLORS[i % 4]}{line}{END_COLOR}", end='')


def main():
    if len(sys.argv) > 3:
        clients = int(sys.argv[1])
        chain_length = int(sys.argv[2])
        smpc_primitive = sys.argv[3]
    elif len(sys.argv) > 2:
        clients = int(sys.argv[1])
        chain_length = int(sys.argv[2])
        smpc_primitive = "ps-rep-ring"
    elif len(sys.argv) > 1:
        clients = int(sys.argv[1])
        chain_length = 3
        smpc_primitive = "ps-rep-ring"
    else:
        clients = 3
        chain_length = 3
        smpc_primitive = "ps-rep-ring"

    if chain_length == 3:
        ke_protocol = "KEP_AP_CC_3"
    elif chain_length == 4:
        ke_protocol = "KEP_AP_CC_4"
    else:
        print("Unsupported chain length: " + str(chain_length))
        return

    computing_peers = 3
    if smpc_primitive == "rep-ring":
        smpc_primitive = "replicated-ring-party.x"
    elif smpc_primitive == "ps-rep-ring":
        smpc_primitive = "ps-rep-ring-party.x"
    elif smpc_primitive == "semi2k":
        smpc_primitive = "semi2k-party.x"
        computing_peers = 2
    else:
        print("Unsupported SMPC primitive: " + smpc_primitive)
        return

    generate_random_input(clients)
    compile_code(clients, smpc_primitive, computing_peers, ke_protocol)
    run(clients, smpc_primitive, computing_peers, ke_protocol)


if __name__ == "__main__":
    main()
