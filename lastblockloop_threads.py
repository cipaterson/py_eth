#!/usr/bin/env python3
import json
from web3 import Web3
import logging
import sys
import os
import threading

InfuraApiKey = os.environ.get("INFURA_API_KEY")

logger = logging.getLogger("web3")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/' + InfuraApiKey))

def thread_fn(id):
  while True:
    logging.info("Thread(%d): ping", id)
    print("Thread",id,": ", w3.eth.get_block_number())

# for i in range(1):
#   logging.info("Main    : create and start thread %d.", i)
#   x = threading.Thread(target=thread_fn, args=(i,))
#   x.start()

thread_fn(42)
