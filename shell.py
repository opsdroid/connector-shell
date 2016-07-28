import logging
import os
import pwd
import datetime
from opsdroid.message import Message

class ConnectorShell:

    def __init__(self, config):
        """ Setup the connector """
        logging.debug("Loaded shell connector")
        self.name = "shell"

    def connect(self, opsdroid):
        """ Connect to the chat service """
        logging.debug("Connecting to shell")
        user = pwd.getpwuid(os.getuid())[0]
        message = ""
        try:
            while message != "exit":
                print('shell> ', end="")
                user_input = input()
                message = Message(user_input, user, None, self)
                opsdroid.parse(message)
        except (KeyboardInterrupt, EOFError):
            print('') # Prints a character return to prepare for return to shell
            logging.info("Keyboard interrupt, exiting shell connector")

    def respond(self, message):
        """ Respond with a message """
        logging.debug("Responding with: " + message.text)
        print(message.text)
