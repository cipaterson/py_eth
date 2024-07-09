#!/usr/bin/env python3
import asyncio
import json
from web3 import Web3
from websockets import connect
import os
import sys
import copy
from datetime import datetime
import time

from dotenv import load_dotenv
load_dotenv()

InfuraApiKey = os.environ.get("INFURA_API_KEY")
network = os.environ.get("ETHEREUM_NETWORK")

infura_ws_url = f'wss://{network}.infura.io/ws/v3/{InfuraApiKey}'
print(infura_ws_url)

contract_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT Tether token
topic_transfer = Web3.keccak(text='Transfer(address,address,uint256)').hex()
method_transfer = Web3.keccak(text='transfer(address,uint256)').hex()[:10]


async def get_event():
    async with connect(infura_ws_url) as ws:    ### , ping_interval=None
        request = ('{{"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe",'
                   '"params": ["logs",'
                   '{{"address": "{}"'
                   # ',"topics": ["{}"]'   ## adding this stops subscription messages?  The filter somehow does not match.
                   '}}]'
                   '}}').format(contract_address, topic_transfer)
        await ws.send(request)
        subscription_response = await ws.recv()
        if "result" not in subscription_response:
            print("Error: result not in ",subscription_response)
        logs_subscription = json.loads(subscription_response)["result"]

        request = '{"jsonrpc":"2.0", "id": 2, "method": "eth_subscribe", "params": ["newHeads"]}'
        await ws.send(request)
        subscription_response = await ws.recv()
        if "result" not in subscription_response:
            print("Error: result not in ",subscription_response)
        newHeads_subscription = json.loads(subscription_response)["result"]

        tx_hashes = {}
        tx_hash_value = {"onchain": {}, "receipt": {}, "events": []}
        re_org = False

        while True:
            try:
                # print(f"waiting for event.....")
                message = await asyncio.wait_for(ws.recv(), timeout=150)
                response = json.loads(message)
                if "id" in response:
                    if response["id"] == 3:   # eth_getBlockByHash response
                        result = response["result"]
                        for t in result["transactions"]:
                            if method_transfer == t["input"][:10] and t["to"] == contract_address.lower():
                                # time.sleep(1)#xxxxx
                                hash = t["hash"]
                                request = '{{"jsonrpc":"2.0","method":"eth_getTransactionReceipt","params": ["{}"],"id":4}}'.format(
                                    hash)
                                # print(f'{request=}')
                                await ws.send(request)

                                # Decoding the input data by hand...
                                # transfer(address,uint256)
                                # 0xa9059cbb 00000000000000000000000070b964b3e119fc0a027f08996bbb98606add6ad1 0000000000000000000000000000000000000000000000000000000005f5e100
                                # to_adr = "0x" + t["input"][34:74]
                                # value = int(t["input"][75:], 16)
                                # print("From: {} To: {} Value={}".format(t["from"], to_adr, value))
                                # Add the onchain tx to the hash
                                if hash in tx_hashes:
                                    if tx_hashes[hash]["onchain"] != {}:
                                        print(f"Replacement tx!", file=sys.stderr)
                                        print("this one: blockhash: {}, blocknum: {}".format(t["blockHash"], t["blockNumber"]), file=sys.stderr)
                                        print("prev one: blockhash: {}, blocknum: {}".format(tx_hashes[hash]["onchain"]["blockHash"], tx_hashes[hash]["onchain"]["blockNumber"]), file=sys.stderr)
                                    tx_hashes[hash]["onchain"] = t
                                else:
                                    tx_hashes[hash] = copy.deepcopy(
                                        tx_hash_value)
                                    tx_hashes[hash]["onchain"] = t

                        # The end of processing the latest block is a good time to print a summary of the collected txs and events
                        print(datetime.now(), "count tx hashes:", len(tx_hashes))
                        if re_org:
                            print("========================== Blockchain re-org!")
                            re_org = False
                        failed_txs = 0
                        for t in iter(tx_hashes):
                            # We only care about entries that were found in a block
                            # There are some tx's that cause Transfer events as a result of calls from other contracts
                            # i.e. internal txs.  Comment this out to print them as well.
                            if tx_hashes[t]["onchain"] == {}:
                                continue
                            # We are interested in txs for which there are no events  ##, or txs that have too many.
                            if len(tx_hashes[t]["events"]) < 1:
                                # If the tx receipt hasn't turned up yet, don't summarize
                                if tx_hashes[t]["receipt"] == {}:
                                    continue
                                # Just count the failed txs, don't print them
                                if tx_hashes[t]["receipt"]["status"]=="0x0":
                                    failed_txs += 1
                                    continue
                                print(t, end=" ")
                                # print(json.dumps(tx_hashes[t], indent=4))
                                print("onchain: {}, events: {}, status: {}".format(
                                    "YES" if tx_hashes[t]["onchain"] != {} else "NO!", len(tx_hashes[t]["events"]), "N/Y" if tx_hashes[t]["receipt"] == {} else tx_hashes[t]["receipt"]["status"]))
                                # Print the from and to addresses for any events
                                for e in tx_hashes[t]["events"]:
                                    # print(" "*20, e["topics"][1]
                                    #       [-32:], e["topics"][2][-32:])
                                    print(e)
                        print(f'Failed tx count= {failed_txs}')

                    elif response["id"] == 4:   # eth_getTransactionReceipt response
                        if "result" not in response:
                            print("Error: result not in ",response)
                            continue#xxx
                        result = response["result"]
                        hash = result["transactionHash"]
                        # print(f'{hash}, {result["status"]=}')
                        # Add the receipt to the hash entry (no need to test if tx hash already seen, it must have been)
                        tx_hashes[hash]["receipt"] = result

                    else:
                        print("Invalid RPC response id: ", id)

                else:   # This must be a subscription event rather than a response to a request
                    if response["params"]["subscription"] == logs_subscription:
                        result = response["params"]["result"]
                        if result["topics"][0] == topic_transfer:
                            hash = result["transactionHash"]
                            if result["removed"]==True:
                                print(f"Re-sent event! Possible re-org.  {hash=}", file=sys.stderr)
                                print(f'{result=}', file=sys.stderr)
                                re_org = True
                            # Add this event (there could be several) to the hash entry for this tx hash
                            if hash in tx_hashes:
                                tx_hashes[hash]["events"].append(result)
                            else:
                                tx_hashes[hash] = copy.deepcopy(tx_hash_value)
                                tx_hashes[hash]["events"].append(result)

                    elif response["params"]["subscription"] == newHeads_subscription:
                        block_hash = response["params"]["result"]["hash"]
                        # We have a newHead subscription response but we want the block including the txs
                        request = '{{"jsonrpc":"2.0","method":"eth_getBlockByHash","params": ["{}",true],"id":3}}'.format(
                            block_hash)
                        await ws.send(request)

                    else:
                        print("Invalid case")
                        exit(1)
            except () as e:
                print("exception ", e)
                print(f'{result=}')

if __name__ == "__main__":
    asyncio.run(get_event())
