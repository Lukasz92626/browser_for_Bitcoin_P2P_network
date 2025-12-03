from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
import asyncio
from p2p import P2PManager
from peer_discovery import discover_peers, peer_db

class BitLabCLI:
    def __init__(self):
        self.session = PromptSession()
        self.p2p = P2PManager()
        self.commands = {
            'connect': self.cmd_connect,
            'peers': self.cmd_peers,
            'version': self.cmd_version,
            'getaddr': self.cmd_getaddr,
            'inv': self.cmd_inv,
            'getdata': self.cmd_getdata,
            'quit': self.cmd_quit,
            'help': self.cmd_help,
            'ping': self.cmd_ping,
            'alert': self.cmd_alert,
            'message': self.cmd_message,
            'reject': self.cmd_reject,
            'tx': self.cmd_tx,
            'block': self.cmd_block,
            'getblocks': self.cmd_getblocks,
            'getheaders': self.cmd_getheaders
        }
        self.completer = WordCompleter(list(self.commands.keys()), ignore_case=True)

    def run(self):
        print("BitLab — prosty P2P shell. Wpisz 'help' aby zobaczyć komendy.")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            while True:
                text = self.session.prompt('bitlab> ', completer=self.completer)
                if not text.strip():
                    continue
                parts = text.strip().split()
                cmd = parts[0].lower()
                args = parts[1:]
                func = self.commands.get(cmd)
                if func:
                    result = func(args)
                    if asyncio.iscoroutine(result):
                        loop.run_until_complete(result)
                else:
                    print(f"Nieznana komenda: {cmd}")
        except (EOFError, KeyboardInterrupt):
            print("\nKończę...")

    # Komendy
    def cmd_help(self, args):
        print("Dostępne komendy:")
        for k in sorted(self.commands.keys()):
            print("  ", k)

    def cmd_quit(self, args):
        print("Wyjście.")
        raise EOFError

    def cmd_connect(self, args):
        """connect <host> <port>"""
        if len(args) < 2:
            print("Użycie: connect <host> <port>")
            return
        host, port = args[0], int(args[1])
        return self.p2p.connect(host, port)

    def cmd_peers(self, args):
        self.p2p.print_peers()

    def cmd_version(self, args):
        """Wysyła (symulowany) version do połączonych peerów."""
        return self.p2p.send_version()

    def cmd_getaddr(self, args):
        """Odkrywa peerów z DNS seed"""
        return self.do_getaddr(args)

    def cmd_inv(self, args):
        if len(args) < 2:
            print("Użycie: inv <tx|block> <hash>")
            return
        typ, h = args[0], args[1]
        return self.p2p.send_inv(typ, h)

    def cmd_getdata(self, args):
        if len(args) < 2:
            print("Użycie: getdata <tx|block> <hash>")
            return
        typ, h = args[0], args[1]
        return self.p2p.send_getdata(typ, h)

    def cmd_ping(self, args):
        """Wyślij ping do wszystkich połączonych peerów"""
        return self.p2p.send_ping()

    def cmd_alert(self, args):
        """
        alert <tekst>
        """
        if not args:
            print("Użycie: alert <tekst>")
            return
        return self.p2p.send_alert(" ".join(args))

    def cmd_message(self, args):
        """
        message <tekst>
        """
        if not args:
            print("Użycie: message <tekst>")
            return
        return self.p2p.send_message(" ".join(args))

    def cmd_reject(self, args):
        """
        reject <cmd> <powód>
        """
        if len(args) < 2:
            print("Użycie: reject <cmd> <powód>")
            return
        cmd, reason = args[0], " ".join(args[1:])
        return self.p2p.send_reject(cmd, reason)

    def cmd_tx(self, args):
        """
        tx <hex>
        wysyła transakcję
        """
        if not args:
            print("Użycie: tx <raw_transaction_hex>")
            return
        return self.p2p.send_tx(args[0])

    def cmd_block(self, args):
        """
        block <hex>
        wysyła blok
        """
        if not args:
            print("Użycie: block <raw_block_hex>")
            return
        return self.p2p.send_block(args[0])

    def cmd_getblocks(self, args):
        """
        getblocks <hash1> [hash2 ...]
        """
        if not args:
            print("Użycie: getblocks <locator_hash1> ...")
            return
        return self.p2p.send_getblocks(args)

    def cmd_getheaders(self, args):
        """
        getheaders <hash1> [hash2 ...]
        """
        if not args:
            print("Użycie: getheaders <locator_hash1> ...")
            return
        return self.p2p.send_getheaders(args)

    # ----------------------
    # Async getaddr
    # ----------------------
    async def do_getaddr(self, args):
        seed = args[0] if args else "seed.bitcoin.sipa.be"
        await discover_peers(seed)
        print("Aktualna lista peerów:", peer_db.list_peers())


