import socket
import threading

import constants
from commands.addr import Addr
from communication import Communication
from mode import Mode
from node import Node

def print_options():
    print(f"0. exit")
    print(f"1. connect to server")
    print(f"2. do the handshake")
    print(f"3. do the manual handshake")
    print(f"4. read in loop")
    print(f"5. enter different modes for reading loop")

def print_manual_hanshake_options():
    print(f"1. send version")
    print(f"2. read version")
    print(f"3. read verack")
    print(f"4. send verack")
    print(f"5. disconnect")
    print(f"6. back")

def print_mode_options():
    print(f"1. set IDLE mode (default)")
    print(f"2. set GETADDR mode")
    print(f"3. set GETDATA_TX mode")
    print(f"4. set GETDATA_BLOCK mode")
    print(f"5. set GETHEADERS mode")
    print(f"6. set GETBLOCKS mode")
    print(f"7. set EXIT mode")
    print(f"8. back")

def handle_menu():
    is_cached = False
    a = Addr()
    c = Communication(Node.from_dict(constants.node))
    client: socket.socket | None = None
    while True:
        print_options()
        choice = input()
        match choice:
            case '0':
                if client is not None:
                    client.close()
                print("closing...")
                break
            case '1':
                if is_cached:
                    client = c.connect_until_success()
                else:
                    client = c.connect()
            case '2':
                if client is None:
                    print("socket is closed ")
                    continue
                c.send_version(client)
                c.read_version(client)
                c.read_verack(client)
                c.send_verack(client)
            case '3':
                if client is None:
                    print("socket is closed")
                    continue
                manual_handshake(client, c)
            case '4':
                if client is None:
                    print("socket is closed ")
                    continue
                reading_thread = threading.Thread(target=c.read_in_loop, args=(client,), daemon=True)
                reading_thread.start()
            case '5':
                if client is None:
                    print("socket is closed ")
                    continue
                mode_options(c)

def mode_options(c):
    print_mode_options()
    choice = input()
    match choice:
        case '1':
            c.set_mode(Mode.IDLE)
        case '2':
            c.set_mode(Mode.GETADDR)
        case '3':
            c.set_mode(Mode.GETDATA_TX)
        case '4':
            c.set_mode(Mode.GETDATA_BLOCK)
        case '5':
            c.set_mode(Mode.GETHEADERS)
        case '6':
            c.set_mode(Mode.GETBLOCKS)
        case '7':
            c.set_mode(Mode.EXIT)
        case '8':
            return

def manual_handshake(client, c):
    counter = 0
    while True:
        print_manual_hanshake_options()
        choice = input()
        match choice:
            case '1':
                c.send_version(client)
            case '2':
                c.read_version(client)
            case '3':
                c.read_verack(client)
            case '4':
                c.send_verack(client)
            case '5':
                c.disconnect(client)
            case '6':
                break
        counter += 1
        if counter == 4:
            break

if __name__ == '__main__':
    handle_menu()
