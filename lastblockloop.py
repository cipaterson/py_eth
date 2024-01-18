#!/usr/bin/env python3
import json
from web3 import Web3
import logging
import sys
import os

logger = logging.getLogger("web3")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

InfuraApiKey = os.environ.get("INFURA_API_KEY")

w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/' + InfuraApiKey))

prev = 0
while True:
  last_block_number = w3.eth.get_block_number()
  print("last block number: ", last_block_number)
  if last_block_number < prev :
    print("block ", last_block_number," out of order by ", prev-last_block_number)
  prev = last_block_number

