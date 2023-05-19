import services
import typer
from blockchain import Blockchain

blockchain = Blockchain()
app = typer.Typer()


@app.command()
def mine_block():
    response = services.mine_block(blockchain)
    print(response)


@app.command()
def display_chain():
    response = {"chain": blockchain.chain, "length": len(blockchain.chain)}
    return print(response)


@app.command()
def valid():
    valid = blockchain.chain_valid(blockchain.chain)

    if valid:
        response = {"message": "The Blockchain is valid."}
    else:
        response = {"message": "The Blockchain is not valid."}
    print(response)


if __name__ == "__main__":
    app()
