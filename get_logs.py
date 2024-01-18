#!/usr/bin/env python3
import json
from web3 import Web3
import logging
import sys
import os

InfuraApiKey = os.environ.get("ETH")


logger = logging.getLogger("web3")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/' + InfuraApiKey))

while True:
  last_block_number = w3.eth.block_number
  print(last_block_number)
