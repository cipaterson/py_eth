import json
from web3 import Web3
import logging
import sys
import os

InfuraApiKey = os.environ.get("INFURA_API_KEY")

logger = logging.getLogger("web3")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

w3a = Web3(Web3.HTTPProvider('https://mainnet.aurora.dev'))
w3i = Web3(Web3.HTTPProvider('https://aurora-mainnet.infura.io/v3/' + InfuraApiKey))

for w3 in (w3a, w3i):
    print(f"======{w3.provider.endpoint_uri}======")
    assert w3.isConnected()

    contract = w3.eth.contract(
        address = Web3.toChecksumAddress('0x918dbe087040a41b786f0da83190c293dae24749'),
        abi = json.load(open('./abi/erc20.json'))
        )

    fr = 69117400 #(contract.web3.eth.block_number - 10)
    to = 69117404 #contract.web3.eth.block_number

    events = contract.events.Transfer.getLogs(fromBlock=fr, toBlock=to)

    for e in events:
        print(e["args"]["from"],
            e["args"]["to"],
            e["args"]["value"])
