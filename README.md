# opsdroid connector shell

A connector for [opsdroid](https://github.com/opsdroid/opsdroid) to send messages using the command line.

## Requirements

The shell connector requires access to user input, this means you should probably set the logging not to go to the console. 

## Configuration

```yaml
connectors:
  - name: shell
    # optional
    bot-name: "mybot" # default "opsdroid"
```
