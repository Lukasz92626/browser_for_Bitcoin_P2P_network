Browser for Bitcoin P2P Network
A simple Python client for the Bitcoin P2P network. This tool connects to Bitcoin nodes, performs the handshake, and exchanges basic protocol messages.

Description
This application acts as a lightweight node or "browser" that connects to peers in the Bitcoin network. It allows you to observe network communication, request block headers, and discover other node addresses.

Features
The project supports the following Bitcoin protocol messages:

Version / Verack: Connection initialization (handshake).

GetHeaders / Headers: Retrieving block headers.

GetBlocks: Requesting block inventory.

Addr: Handling and exchanging known peer addresses.

Inv: Processing inventory messages.

Project Structure

main.py: The main entry point of the application.

node.py: Contains the logic for a single network node.

communication.py: Handles socket connections and network transmission.

commands/: Directory containing specific command implementations.

addresses.json: Stores IP addresses of known peers.

bitcoin.log: Records network activity and logs.

Requirements
Python 3.13 or higher.

Standard Python libraries (socket, struct, json).

How to Run
Clone the repository or extract the files.

(Optional) Update addresses.json with known Bitcoin node IP addresses.

Run the application:

Bash
python main.py

Logs
All sent and received messages are saved to bitcoin.log. You can check this file to analyze network traffic.