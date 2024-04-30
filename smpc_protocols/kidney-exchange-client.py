#!/usr/bin/python3

import sys

sys.path.append('.')

from client import *
from domains import *

client_id = int(sys.argv[1])
n_computing_peers = int(sys.argv[2])
n_input_peers = int(sys.argv[3])
finish = int(sys.argv[4])


client = Client(['localhost'] * n_computing_peers, 14000, client_id)

type = client.specification.get_int(4)

if type == ord('R'):
    domain = Z2(client.specification.get_int(4))
elif type == ord('p'):
    domain = Fp(client.specification.get_bigint())
else:
    raise Exception('invalid type')

for socket in client.sockets:
    os = octetStream()
    os.store(finish)
    os.Send(socket)

input_data = []
with open("ExternalIO/Inputs/input_"+str(client_id)+".txt") as f:
    for l in f:
        input_data.append(l.split(" "))

# compatibility check input
donor_blood = []
patient_blood = []
donor_antigens_a = []
donor_antigens_b = []
donor_antigens_c = []
donor_antigens_dr = []
donor_antigens_dq = []
donor_antigens_dp = []
patient_antibodies_a = []
patient_antibodies_b = []
patient_antibodies_c = []
patient_antibodies_dr = []
patient_antibodies_dq = []
patient_antibodies_dp = []
altruist_bit = []
# prioritization input
prescores = []
patient_antigens_a = []
patient_antigens_b = []
patient_antigens_dr = []
patient_center = []
donor_center = []

for i in range(len(input_data)):
    for j in range(len(input_data[i])):
        if i == 0:
            donor_blood.append(domain(int(input_data[i][j].rstrip())))
        elif i == 1:
            donor_antigens_a.append(domain(int(input_data[i][j].rstrip())))
        elif i == 2:
            donor_antigens_b.append(domain(int(input_data[i][j].rstrip())))
        elif i == 3:
            donor_antigens_c.append(domain(int(input_data[i][j].rstrip())))
        elif i == 4:
            donor_antigens_dr.append(domain(int(input_data[i][j].rstrip())))
        elif i == 5:
            donor_antigens_dq.append(domain(int(input_data[i][j].rstrip())))
        elif i == 6:
            donor_antigens_dp.append(domain(int(input_data[i][j].rstrip())))
        elif i == 7:
            patient_blood.append(domain(int(input_data[i][j].rstrip())))
        elif i == 8:
            patient_antibodies_a.append(domain(int(input_data[i][j].rstrip())))
        elif i == 9:
            patient_antibodies_b.append(domain(int(input_data[i][j].rstrip())))
        elif i == 10:
            patient_antibodies_c.append(domain(int(input_data[i][j].rstrip())))
        elif i == 11:
            patient_antibodies_dr.append(domain(int(input_data[i][j].rstrip())))
        elif i == 12:
            patient_antibodies_dq.append(domain(int(input_data[i][j].rstrip())))
        elif i == 13:
            patient_antibodies_dp.append(domain(int(input_data[i][j].rstrip())))
        elif i == 14:
            altruist_bit.append(domain((int(input_data[i][j].rstrip()))))
        elif i == 15:
            prescores.append(domain(int(input_data[i][j].rstrip())))
        elif i == 16:
            patient_antigens_a.append(domain(int(input_data[i][j].rstrip())))
        elif i == 17:
            patient_antigens_b.append(domain(int(input_data[i][j].rstrip())))
        elif i == 18:
            patient_antigens_dr.append(domain(int(input_data[i][j].rstrip())))
        elif i == 19:
            patient_center.append(domain(int(input_data[i][j].rstrip())))
        elif i == 20:
            donor_center.append(domain(int(input_data[i][j].rstrip())))

# send input for compatibility check
client.send_private_inputs(donor_blood)
client.send_private_inputs(patient_blood)
client.send_private_inputs(donor_antigens_a)
client.send_private_inputs(patient_antibodies_a)
client.send_private_inputs(donor_antigens_b)
client.send_private_inputs(patient_antibodies_b)
client.send_private_inputs(donor_antigens_c)
client.send_private_inputs(patient_antibodies_c)
client.send_private_inputs(donor_antigens_dr)
client.send_private_inputs(patient_antibodies_dr)
client.send_private_inputs(donor_antigens_dq)
client.send_private_inputs(patient_antibodies_dq)
client.send_private_inputs(donor_antigens_dp)
client.send_private_inputs(patient_antibodies_dp)
client.send_private_inputs(altruist_bit)

# send input for prioritization
client.send_private_inputs(prescores)
client.send_private_inputs(patient_antigens_a)
client.send_private_inputs(patient_antigens_b)
client.send_private_inputs(patient_antigens_dr)
client.send_private_inputs(donor_antigens_a)
client.send_private_inputs(donor_antigens_b)
client.send_private_inputs(donor_antigens_dr)
client.send_private_inputs(patient_center)
client.send_private_inputs(donor_center)

donor = client.receive_outputs(domain, 1)[0].v % 2 ** 64
print("Client"+str(client_id+1)+": The donor for your patient is: "+str(donor))

patient = client.receive_outputs(domain, 1)[0].v % 2 ** 64
print("Client"+str(client_id+1)+": The recipient for your donor is: "+str(patient))
print("NOTE: The donor for the patient of an altruistic donor and the recipient for the last donor in a chain are always set to '0'.")
