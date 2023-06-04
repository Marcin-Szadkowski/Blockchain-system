import time

import typer

from blockchain_system.blockchain import Record
from blockchain_system.publisher import Publisher
from blockchain_system.subscriber import CliSubscriber

app = typer.Typer()


@app.command()
def listen_events():
    subscriber = CliSubscriber()
    subscriber.start_consuming()


@app.command()
def add_record(content: str):
    record = Record(index=0, timestamp=int(time.time()), content=content)
    publisher = Publisher()
    publisher.notify_add_record(record=record)


@app.command()
def show_chain():
    publisher = Publisher()
    publisher.notify_show_chain()


if __name__ == "__main__":
    app()
