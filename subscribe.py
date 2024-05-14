#!/usr/bin/env python3
import asyncio
import json
from dotenv import load_dotenv

from web3 import Web3
from websockets import connect
import os

load_dotenv()

InfuraApiKey = os.environ.get("INFURA_API_KEY")
SignerAccount = os.environ.get("SIGNER_ACCOUNT")
network = "mainnet"  # os.environ.get("ETHEREUM_NETWORK")

# eth_subscribe = "newHeads"
# eth_subscribe = "newPendingTransactions"
eth_subscribe = "newPendingTransactions"

infura_ws_url = f'wss://{network}.infura.io/ws/v3/' + InfuraApiKey
infura_http_url = f'https://{network}.infura.io/v3/' + InfuraApiKey
# print(infura_ws_url)
web3 = Web3(Web3.HTTPProvider(infura_http_url))

# Used if you want to monitor ETH transactions to a specific address
account = SignerAccount

async def get_event():
    async with connect(infura_ws_url) as ws:
        await ws.send('{"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["'+eth_subscribe+'"]}')
        subscription_response = await ws.recv()
        print(subscription_response)

        while True:
            try:
                print("waiting for event.....")
                message = await asyncio.wait_for(ws.recv(), timeout=15)
                print(message)
                response = json.loads(message)
                if eth_subscribe == "newPendingTransactions":
                  txHash = response['params']['result']
                  print(txHash)
                  tx=None
                  for i in range(5):
                    try:
                      tx = web3.eth.get_transaction(txHash)
                      break
                    except:
                      pass
                  print(f'{tx=}')
                elif eth_subscribe == "newHeads":
                  blk_number = response['params']['result']['number']
                  print(blk_number)
            except () as e:
                print("exception ", e)

if __name__ == "__main__":
    asyncio.run(get_event())
