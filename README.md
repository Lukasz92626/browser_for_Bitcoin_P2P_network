# BitLab: a browser for the Bitcoin P2P network and its blockchain

BitLab is a tool for interacting with the Bitcoin peer-to-peer network and its blockchain.

## Command list

**help** - Displays a list of all functions.

**quit** - Quits BitLab.

**connect <host> <port>** - Connects to a Bitcoin peer at the address and port.

**peers** - Displays a list of current peers.

**version** - Sends a version message for peers to use.

**getaddr [seed]** - Discovers new peers in the Bitcoin network via DNS seed or the specified host.

**ping** - Sends a ping to all connected peers.

**alert <text>** - Sends an alert to peers (historical protocol function).

**message <text>** - Sends a simple diagnostic message to peers.

**reject <command> <reason>** - Sends a reject message, reporting a client error for the given command.

**inv <tx|block> <hash>** - Announces to peers that you have a block or transaction with the specified hash.

**getdata <tx|block> <hash>** - Requests a specific block or transaction from peers by hash.

**getblocks <hash1> [hash2 …]** - Requests a list of blocks from peers starting with the given hash.

**getheaders <hash1> [hash2 …]** - Downloads block headers from the Bitcoin network starting with the given hash.

**tx <hex>** - Sends the raw transaction in hex format to peers.

**block <hex>** - Sends the raw block in hex format to peers.
