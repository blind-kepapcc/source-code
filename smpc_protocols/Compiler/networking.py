# The Software is copyright (c) 2023, Commonwealth Scientific and Industrial Research Organisation (CSIRO) ABN 41 687 119 230.
#
# CSIRO grants you a licence to the Software on the terms of the BSD 3-Clause Licence.
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#    Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Computing peer side of the infrastructure for handling External IO in MP-SPDZ adapted to our use case. See
smpc_protocols/kidney-exchange-client.py for the client (input peer) side.
The original source code can be found in:
https://github.com/data61/MP-SPDZ/blob/v0.3.5/Programs/Source/bankers_bonus.mpc
"""

from Compiler.types import sint, regint, Array, MemValue
from Compiler.library import  accept_client_connection, for_range
from Compiler.instructions import closeclientconnection
from Compiler.library import print_ln, do_while, if_, crash
from Compiler.library import listen_for_clients

PORTNUM = 14000


def accept_client():
    client_socket_id = accept_client_connection(PORTNUM)
    last = regint.read_from_socket(client_socket_id)
    return client_socket_id, last


def close_connections(number_clients):
    @for_range(number_clients)
    def _(i):
        closeclientconnection(i)


def client_input(client_socket_id, length):
    """
    Send share of random value, receive input and deduce share.
    """

    return sint.receive_from_client(length, client_socket_id)


def setup_client_connections(port_num, num_clients):
    # start listening for client socket connections
    listen_for_clients(port_num)
    print_ln('Listening for client connections on base port %s', port_num)

    # clients socket id (integer)
    client_sockets = Array(num_clients, regint)
    # number of clients
    number_clients = MemValue(regint(0))
    # client ids to identity client
    client_ids = Array(num_clients, sint)
    # keep track of received inputs
    seen = Array(num_clients, regint)
    seen.assign_all(0)

    # loop waiting for each client to connect
    @do_while
    def client_connection():
        client_id, last = accept_client()

        @if_(client_id >= num_clients)
        def _():
            print_ln('client id is too high')
            crash()

        client_sockets[client_id] = client_id
        client_ids[client_id] = client_id
        seen[client_id] = 1

        @if_(last == 1)
        def _():
            number_clients.write(client_id + 1)

        return (sum(seen) < number_clients) + (number_clients == 0)

    return number_clients, client_sockets

def write_output_to_clients(sockets, number_clients, output):
    @for_range(number_clients)
    def loop_body(i):
        r = sint.get_random()
        to_send = [output[i], r, output[i] * r]
        sint.write_shares_to_socket(sockets[i], to_send)


def write_output_to_client(socket, recipient, donor):
    rnd_from_triple = sint.get_random_triple()[0]
    auth_result = recipient * rnd_from_triple
    sint.write_shares_to_socket(socket, [recipient, rnd_from_triple, auth_result])

    rnd_from_triple = sint.get_random_triple()[0]
    auth_result = donor * rnd_from_triple
    sint.write_shares_to_socket(socket, [donor, rnd_from_triple, auth_result])
