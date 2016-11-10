import logging
import os
import pwd
import datetime
import asyncio
from asyncio.streams import StreamWriter, FlowControlMixin
import sys

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
        """ Setup the connector """
        logging.debug("Loaded shell connector")
        self.name = "shell"
        self.config = config
        self.bot_name = config["bot-name"]

    async def connect(self, opsdroid):
        """ Connect to the chat service """
        logging.debug("Connecting to shell")
        user = pwd.getpwuid(os.getuid())[0]
        message = Message("", "", None, self)
        while message.text != "exit":
            user_input = await async_input(self.bot_name + '> ', opsdroid.eventloop)
            message = Message(user_input, user, None, self)
            await opsdroid.parse(message)

    def respond(self, message):
        """ Respond with a message """
        logging.debug("Responding with: " + message.text)
        print(message.text)
