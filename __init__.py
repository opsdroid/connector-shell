import logging
import os
import pwd
import datetime
import sys
import asyncio
from asyncio.streams import StreamWriter, FlowControlMixin

from opsdroid.connector import Connector
from opsdroid.message import Message

reader, writer = None, None

async def stdio(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    reader = asyncio.StreamReader()
    reader_protocol = asyncio.StreamReaderProtocol(reader)

    writer_transport, writer_protocol = await loop.connect_write_pipe(FlowControlMixin, os.fdopen(0, 'wb'))
    writer = StreamWriter(writer_transport, writer_protocol, None, loop)

    await loop.connect_read_pipe(lambda: reader_protocol, sys.stdin)

    return reader, writer

async def async_input(message, loop=None):
    if isinstance(message, str):
        message = message.encode('utf8')

    global reader, writer
    if (reader, writer) == (None, None):
        reader, writer = await stdio(loop)

    writer.write(message)
    await writer.drain()

    line = await reader.readline()
    return line.decode('utf8').replace('\r', '').replace('\n', '')

class ConnectorShell(Connector):

    def __init__(self, config):
        """Setup the connector."""
        logging.debug("Loaded shell connector")
        super().__init__(config)
        self.name = "shell"
        self.config = config
        self.bot_name = config.get("bot-name", "opsdroid")
        self.prompt_length = None

    async def connect(self, opsdroid):
        """Connect to the shell."""
        pass # Nothing to do here as stdin is already available

    async def listen(self, opsdroid):
        """Listen for new user input."""
        logging.debug("Connecting to shell")
        while True:
            user = pwd.getpwuid(os.getuid())[0]
            self.draw_prompt()
            user_input = await async_input('', opsdroid.eventloop)
            message = Message(user_input, user, None, self)
            await opsdroid.parse(message)

    async def respond(self, message, room=None):
        """Respond with a message."""
        logging.debug("Responding with: " + message.text)
        self.clear_prompt()
        print(message.text)
        self.draw_prompt()

    def draw_prompt(self):
        """Draw the user input prompt."""
        prompt = self.bot_name + '> '
        self.prompt_length = len(prompt)
        print(prompt, end="", flush=True)

    def clear_prompt(self):
        """Clear the prompt."""
        print("\r" + (" " * self.prompt_length) + "\r", end="", flush=True)
