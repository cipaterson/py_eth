#!/usr/bin/env python3
import requests
import os
import time
import json

def new_filter(network, InfuraApiKey, level):
  response = requests.post(
    f'https://eth-mainnet.g.alchemy.com/v2/CSV4moPMCLzK-1vt_Z5vLtsLT5ZwVHZZ',
    data='{"id": 1, "jsonrpc": "2.0", "method": "eth_newFilter", "params": [{"topics": [], "fromBlock": "'+level+'", "toBlock": "'+level+'"}]}'
  )
  return json.loads(response.text)["result"]

def get_filter_logs(network, InfuraApiKey, filter_id):
  response = requests.post(
    f'https://eth-mainnet.g.alchemy.com/v2/CSV4moPMCLzK-1vt_Z5vLtsLT5ZwVHZZ',
    data='{"id": 1, "jsonrpc": "2.0", "method": "eth_getFilterLogs", "params": ["'+filter_id+'"]}'
  )
  # print(response.status_code)
  # print(response.text[0:400])
  results=(json.loads(response.text)["result"])
  for e in results:
    #  print(e)
    blknum = int(e["blockNumber"], 16)
    print(filter_id, "   ", e["blockNumber"], blknum)
    break
  return blknum


def get_filter_changes(network, InfuraApiKey, filter_id):
  response = requests.post(
    f'https://eth-mainnet.g.alchemy.com/v2/CSV4moPMCLzK-1vt_Z5vLtsLT5ZwVHZZ',
    data='{"id": 1, "jsonrpc": "2.0", "method": "eth_getFilterChanges", "params": ["'+filter_id+'"]}'
  )
  # print(response.status_code)
  # print(response.text[0:400])
  results=(json.loads(response.text)["result"])
  print(len(results))
  for e in results:
    #  print(e)
    blknum = int(e["blockNumber"], 16)
    print(filter_id, "   ", e["blockNumber"], blknum)
    break
  return blknum

def main():
    InfuraApiKey = os.environ.get("INFURA_API_KEY")
    network = "mainnet"   # os.environ.get("ETHEREUM_NETWORK")

    filter_id_latest = new_filter(network, InfuraApiKey, "latest")
    filter_id_finalized = new_filter(network, InfuraApiKey, "finalized")

    print("Using filter with latest block")
    blknum_l = get_filter_logs(network, InfuraApiKey, filter_id_latest)
    print("Using filter with finalized block")
    blknum_f = get_filter_logs(network, InfuraApiKey, filter_id_finalized)
    print("difference= ", blknum_l - blknum_f)

    time.sleep(60) # wait a minute to expect a new block

    print("Getting changes using filter with latest block")
    blknum_l = get_filter_changes(network, InfuraApiKey, filter_id_latest)
    print("Getting changes using filter with finalized block")
    blknum_f = get_filter_changes(network, InfuraApiKey, filter_id_finalized)
    print("difference= ", blknum_l - blknum_f)

if __name__ == "__main__":
  main()
