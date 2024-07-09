#!/usr/bin/env python3
import asyncio
import json
from web3 import Web3
from websockets import connect
import os
import copy

from dotenv import load_dotenv
load_dotenv()

InfuraApiKey = os.environ.get("INFURA_API_KEY")
network = "mainnet"   ##os.environ.get("ETHEREUM_NETWORK")

infura_ws_url = f'wss://{network}.infura.io/ws/v3/' + InfuraApiKey

contract_address = "0xb373d8a5e11BB9337e9cB9707eD35f62F5282176"  # Sepolia USDT Tether token
##contract_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT Tether token
topic_transfer = Web3.keccak(text='Transfer(address,address,uint256)').hex()
method_transfer = Web3.keccak(text='transfer(address,uint256)').hex()[:10]


async def get_event():
    async with connect(infura_ws_url) as ws:
        request = ('{{"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe",'
                   '"params": ["logs",'
                   '{{"address": "{}"'
                   # ',"topics": ["{}"]'   ## adding this stops subscription messages?  The filter somehow does not match.
                   '}}]'
                   '}}').format(contract_address, topic_transfer)
        await ws.send(request)
        subscription_response = await ws.recv()
        if "result" not in subscription_response:
            print("Error: result not in ", subscription_response)
        logs_subscription = json.loads(subscription_response)["result"]

        while True:
            try:
                print(f"waiting for event..... ")
                message = await asyncio.wait_for(ws.recv(), timeout=1500)
                print(message)
                # response = json.loads(message)
            except () as e:
                print("exception ", e)

if __name__ == "__main__":
    asyncio.run(get_event())
