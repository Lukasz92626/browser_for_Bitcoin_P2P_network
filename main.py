import asyncio
from cli import BitLabCLI

def main():
    cli = BitLabCLI()
    cli.run()

if __name__ == "__main__":
    shell = BitLabCLI()
    shell.run()
    main()