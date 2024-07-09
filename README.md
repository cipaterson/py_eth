# Python Ethereum scripts

## Description

Just some random scripts in Python for interacting with an Ethereum node.

## subscribe_logs.py
This script uses a websocket to subscribe to USDT Transfer events and compare them with Transfer transactions added
to the blockchain looking for missing events.

## eip1559_tx.py
This script sends a simple zero value ETH transfer to be added to the chain.  It uses the Infura Gas estimation API
to determine the gas price to use.  By default it tries to use a very cheap price to explore what happens when
a transaction is pending for longer than expected.  It retries the tx send after bumping up the gas price if it times
out.  I hope UniSwap has a better algorithm, but it's an example of how to handle failure for a tx to be mined
and re-try with a higher gas price.

## Getting Started
Most scripts use argparse so try --help for help.

### Dependencies

```
pip web3
```
There may be others.

### Installing

Most get the Infura API KEY from an environment variable or from a .env file, or on the command line.

Example .env file:
```
ETHEREUM_NETWORK="sepolia"
# INFURA project: Infura account / project_name
INFURA_API_KEY="cfc1xxxxxxxxxxxxxx0dd1bf3d"
INFURA_SECRET=3dxxxxxxxxxxxxxx7a4e5dd3af7
# TEST ETH account
SIGNER_ACCOUNT="0x8893eaxxxxxxxxxxxxxxxxxxx9a54B111a12"
SIGNER_PRIVATE_KEY="460xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx197"
RECIPIENT-PUBLIC-KEY=""
```

### Executing program


