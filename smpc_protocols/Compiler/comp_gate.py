# coding: latin-1
"""

"""

from Compiler.types import sint, regint, Array, MemValue, Matrix, MultiArray
from Compiler.library import print_ln, do_while, for_range, print_str, if_, for_range_parallel
from Compiler.unos import BLOOD_TYPES, UNOS_ANTIGEN_TYPES, UNOS_ANTIGEN_TYPES_A, UNOS_ANTIGEN_TYPES_B, \
    UNOS_ANTIGEN_TYPES_C, UNOS_ANTIGEN_TYPES_DR, UNOS_ANTIGEN_TYPES_DQ, UNOS_ANTIGEN_TYPES_DP, \
    UNOS_PRIO_VALUE_0_ABDR_MISMATCH, UNOS_PRIO_VALUE_REGION
from Compiler.networking import write_output_to_clients, client_input, accept_client


def compute_prioritization_weight(prescore, patient_abdr, donor_abdr, num_donor_abdr, patient_center, donor_center):
    w_region = Array(1, sint)
    w_region[0] = patient_center[0] == donor_center[0]

    # calculate 0-ABDR mismatch
    w_abdr = Array(1, sint)
    w_abdr[0] = sint.dot_product(patient_abdr, donor_abdr) == num_donor_abdr

    return prescore[0] + UNOS_PRIO_VALUE_REGION * w_region[0] + UNOS_PRIO_VALUE_0_ABDR_MISMATCH * w_abdr[0]


def compute_prio_matrix(prescores, patient_antigens, donor_antigens, patient_center, donor_center, num_nodes):
    prio_matrix = sint.Matrix(num_nodes, num_nodes)
    prio_matrix.assign_all(sint(0))

    num_donor_abdr = sint.Array(num_nodes)
    num_donor_abdr.assign_all(sint(0))

    @for_range(UNOS_ANTIGEN_TYPES_A + UNOS_ANTIGEN_TYPES_B + UNOS_ANTIGEN_TYPES_DR)
    def _(i):
        @for_range_parallel(num_nodes, num_nodes)
        def _(j):
            num_donor_abdr[j] = num_donor_abdr[j] + donor_antigens[j][i]

    @for_range_parallel(num_nodes, num_nodes)
    def _(i):
        @for_range_parallel(num_nodes, num_nodes)
        def _(j):
            prio_matrix[i][j] = compute_prioritization_weight(prescores[j], patient_antigens[j], donor_antigens[i],
                                                              num_donor_abdr[i], patient_center[j], donor_center[i])

    return prio_matrix


def compute_compatibility(blood_donor, antigen_donor, blood_patient, antigen_patient):
    sumb = Array(1, sint)
    sumb[0] = sint(0)

    suma = Array(1, sint)
    suma[0] = sint(0)

    sumb[0] = sint.dot_product(blood_patient, blood_donor)

    suma[0] = sint.dot_product(antigen_patient, antigen_donor)

    ohb = sint(0) < sumb[0]
    oha = suma[0] < sint(1)
    return ohb * oha


def compute_comp_matrix(blood_donor, blood_patient, antigen_donor, antigen_patient, num_nodes):
    adjacency_matrix = sint.Matrix(num_nodes, num_nodes)
    adjacency_matrix.assign_all(sint(0))

    @for_range_parallel(num_nodes, num_nodes)
    def _(client_i):
        @for_range_parallel(num_nodes, num_nodes)
        def _(client_j):
            adjacency_matrix[client_i][client_j] = compute_compatibility(blood_donor[client_i],
                                                                         antigen_donor[client_i],
                                                                         blood_patient[client_j],
                                                                         antigen_patient[client_j])

    return adjacency_matrix


def read_input(num_clients):
    blood_donor = sint.Matrix(num_clients, BLOOD_TYPES)
    blood_patient = sint.Matrix(num_clients, BLOOD_TYPES)
    antigen_donor = sint.Matrix(num_clients, UNOS_ANTIGEN_TYPES)
    antibodies_patient = sint.Matrix(num_clients, UNOS_ANTIGEN_TYPES)

    @for_range(num_clients)
    def _(client_id):
        blood_donor[client_id] = client_input(client_id, BLOOD_TYPES)
        blood_patient[client_id] = client_input(client_id, BLOOD_TYPES)

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_A)
        for i in range(UNOS_ANTIGEN_TYPES_A):
            antigen_donor[client_id][i] = tmp[i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_A)

        for i in range(UNOS_ANTIGEN_TYPES_A):
            antibodies_patient[client_id][i] = tmp[i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_B)

        for i in range(UNOS_ANTIGEN_TYPES_B):
            antigen_donor[client_id][UNOS_ANTIGEN_TYPES_A + i] = tmp[i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_B)

        for i in range(UNOS_ANTIGEN_TYPES_B):
            antibodies_patient[client_id][UNOS_ANTIGEN_TYPES_A + i] = tmp[i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_C)

        for i in range(UNOS_ANTIGEN_TYPES_C):
            antigen_donor[client_id][UNOS_ANTIGEN_TYPES_A + UNOS_ANTIGEN_TYPES_B + i] = tmp[i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_C)

        for i in range(UNOS_ANTIGEN_TYPES_C):
            antibodies_patient[client_id][UNOS_ANTIGEN_TYPES_A + UNOS_ANTIGEN_TYPES_B + i] = tmp[i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_DR)

        for i in range(UNOS_ANTIGEN_TYPES_DR):
            antigen_donor[client_id][UNOS_ANTIGEN_TYPES_A + UNOS_ANTIGEN_TYPES_B + UNOS_ANTIGEN_TYPES_C + i] = \
                tmp[
                    i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_DR)

        for i in range(UNOS_ANTIGEN_TYPES_DR):
            antibodies_patient[client_id][UNOS_ANTIGEN_TYPES_A + UNOS_ANTIGEN_TYPES_B + UNOS_ANTIGEN_TYPES_C + i] = \
                tmp[i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_DQ)

        for i in range(UNOS_ANTIGEN_TYPES_DQ):
            antigen_donor[client_id][
                UNOS_ANTIGEN_TYPES_A + UNOS_ANTIGEN_TYPES_B + UNOS_ANTIGEN_TYPES_C + UNOS_ANTIGEN_TYPES_DR + i] = \
                tmp[
                    i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_DQ)

        for i in range(UNOS_ANTIGEN_TYPES_DQ):
            antibodies_patient[client_id][
                UNOS_ANTIGEN_TYPES_A + UNOS_ANTIGEN_TYPES_B + UNOS_ANTIGEN_TYPES_C + UNOS_ANTIGEN_TYPES_DR + i] = \
                tmp[i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_DP)

        for i in range(UNOS_ANTIGEN_TYPES_DP):
            antigen_donor[client_id][
                UNOS_ANTIGEN_TYPES_A + UNOS_ANTIGEN_TYPES_B + UNOS_ANTIGEN_TYPES_C + UNOS_ANTIGEN_TYPES_DR + UNOS_ANTIGEN_TYPES_DQ + i] = \
                tmp[i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_DP)

        for i in range(UNOS_ANTIGEN_TYPES_DP):
            antibodies_patient[client_id][
                UNOS_ANTIGEN_TYPES_A + UNOS_ANTIGEN_TYPES_B + UNOS_ANTIGEN_TYPES_C + UNOS_ANTIGEN_TYPES_DR + UNOS_ANTIGEN_TYPES_DQ + i] = \
                tmp[i]

    return blood_donor, blood_patient, antigen_donor, antibodies_patient


def read_prio_input(num_clients):
    prescores = Matrix(num_clients, 1, sint)
    patient_antigens = Matrix(num_clients, UNOS_ANTIGEN_TYPES_A + UNOS_ANTIGEN_TYPES_B + UNOS_ANTIGEN_TYPES_DR, sint)
    donor_antigens = Matrix(num_clients, UNOS_ANTIGEN_TYPES_A + UNOS_ANTIGEN_TYPES_B + UNOS_ANTIGEN_TYPES_DR, sint)
    patient_center = Matrix(num_clients, 1, sint)
    donor_center = Matrix(num_clients, 1, sint)

    @for_range(num_clients)
    def _(client_id):
        prescores[client_id] = client_input(client_id, 1)

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_A)
        for i in range(UNOS_ANTIGEN_TYPES_A):
            patient_antigens[client_id][i] = tmp[i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_B)

        for i in range(UNOS_ANTIGEN_TYPES_B):
            patient_antigens[client_id][UNOS_ANTIGEN_TYPES_A + i] = tmp[i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_DR)

        for i in range(UNOS_ANTIGEN_TYPES_DR):
            patient_antigens[client_id][UNOS_ANTIGEN_TYPES_A + UNOS_ANTIGEN_TYPES_B + i] = tmp[i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_A)
        for i in range(UNOS_ANTIGEN_TYPES_A):
            donor_antigens[client_id][i] = tmp[i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_B)

        for i in range(UNOS_ANTIGEN_TYPES_B):
            donor_antigens[client_id][UNOS_ANTIGEN_TYPES_A + i] = tmp[i]

    @for_range(num_clients)
    def _(client_id):
        tmp = client_input(client_id, UNOS_ANTIGEN_TYPES_DR)

        for i in range(UNOS_ANTIGEN_TYPES_DR):
            donor_antigens[client_id][UNOS_ANTIGEN_TYPES_A + UNOS_ANTIGEN_TYPES_B + i] = tmp[i]

    @for_range(num_clients)
    def _(client_id):
        patient_center[client_id] = client_input(client_id, 1)
        donor_center[client_id] = client_input(client_id, 1)

    return prescores, patient_antigens, donor_antigens, patient_center, donor_center


def read_altruist_bits(num_nodes):
    # stores for each client a bit indicating whether the client is altruistic (1 = altruistic, 0 otherwise)
    altruist_bits = Array(num_nodes, sint)

    @for_range(num_nodes)
    def _(client_id):
        altruist_bits[client_id] = client_input(client_id, 1)[0]

    return altruist_bits