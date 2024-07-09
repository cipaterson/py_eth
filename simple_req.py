#!/usr/bin/env python3
import requests
import os
import sys
import json
import argparse
from datetime import datetime
import time

parser = argparse.ArgumentParser(
    description='Send eth_method to network and return result')
parser.add_argument('-k', '--api_key', metavar='INFURA_API_KEY', default=None,
                    help='Infura API Key to use (INFURA_API_KEY env var used by default).')
parser.add_argument('-v', '--verbose', action='store_true', default=False,
                    help='Make output more verbose.')
parser.add_argument("network", help="network to request on")

args = parser.parse_args()
# print(args)
# exit()

InfuraApiKey = args.api_key or os.environ.get("INFURA_API_KEY") or os.environ.get("ETH")
if InfuraApiKey == None:
   print('Error: Use --api_key to provide a valid Infura API key', file=sys.stderr)
   parser.print_help()
   exit(1)

network = args.network
verbose = args.verbose


# data='{"jsonrpc": "2.0", "method": "debug_traceBlockByNumber", "params": ["latest", {"tracer": "callTracer", "timeout": "120s"}], "id": 3095109}'
# eth_blockNumber, eth_chainId, net_version, web3_clientVersion
data='{"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}'
if verbose:
  print(data)

url = f'https://{network}.infura.io/v3/{InfuraApiKey}'

i=0
while True:
  i += 1
  t = time.time()
  try:
    response = requests.post(url, data=data)
    # print(f'Requests.post time={time.time()-t:7.3f}')
  except:
    print(f"Error: Can't connect: {url}", file=sys.stderr)
    exit(1)

  if response.status_code == 401:
    print(
        'Error: Status code 401, use --api_key to provide a valid Infura API key', file=sys.stderr)
    exit(1)

  # Ignore 400 because many networks return it together with a valid error response we can interpret later
  # Networks that do this: near, starknet, avalanche, base.
  if response.status_code != 200 and response.status_code != 400:
    print(f'Error: Status code: {response.status_code}, URL: {url}', file=sys.stderr)
    print(response.text[:250])
    exit(1)

  if verbose:
    print(datetime.now(), i, f'{time.time()-t:10.3f}', response.text[:120])

  jResponse = json.loads(response.text)

  if jResponse.get('error') == None:
    pass ## print(f'{jResponse["result"]}')
  else:
    print(f'{jResponse["error"]}')
    ##exit(1)
