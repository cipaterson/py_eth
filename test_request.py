#!/usr/bin/env python3
import requests
import os
import sys
import json
import argparse

parser = argparse.ArgumentParser(
    description='Test support exists for every eth_method for every network')
parser.add_argument('-m', '--methods', nargs='+',
                    help='Method name(s) to test, e.g. eth_getBalance (all methods by default).')
parser.add_argument('-n', '--networks', nargs='+',
                    help='Network subdomain to test (all test networks by default).')
parser.add_argument('-k', '--api_key', metavar='INFURA_API_KEY', default=None,
                    help='Infura API Key to use (INFURA_API_KEY env var used by default).')

args = parser.parse_args()

InfuraApiKey = args.api_key or os.environ.get("INFURA_API_KEY") or os.environ.get("ETH")
if InfuraApiKey == None:
   print('Error: Use --api_key to provide a valid Infura API key', file=sys.stderr)
   parser.print_help()
   exit(1)

defaultNetworks = [
    "sepolia",
    "goerli",
    "arbitrum-goerli",
    "aurora-testnet",
    "avalanche-fuji",
    "base-goerli",
    "celo-alfajores",
    # "bnbsmartchain-testnet",  # project ID does not have access to binance
    "linea-goerli",
    "near-testnet",
    "optimism-goerli",
    "palm-testnet",
    "polygon-mumbai",
    "starknet-goerli"
]
theNetworks = args.networks or defaultNetworks

defaultMethods = [
    {'method': 'eth_accounts', 'params': []},
    {'method': 'eth_blockNumber', 'params': []},
    {'method': 'eth_call', 'params': [{"from": "0xb60e8dd61c5d32be8058bb8eb970870f07233155", "to": "0xd46e8dd67c5d32be8058bb8eb970870f07244567", "gas": "0x76c0",
        "gasPrice": "0x9184e72a000", "value": "0x9184e72a", "data": "0xd46e8dd67c5d32be8d46e8dd67c5d32be8058bb8eb970870f072445675058bb8eb970870f072445675"}, "latest"]},
    # eth_call err: insufficient funds for gas * price + value
    {'method': 'eth_chainId', 'params': []},
    # {'method': 'eth_coinbase', 'params': []},   # Not supported on any endpoint
    {"method": "eth_createAccessList", "params": [
        {"from": "0xaeA8F8f781326bfE6A7683C2BD48Dd6AA4d3Ba63", "data": "0x608060806080608155"}, "pending"]},
    # many errors
    {"method": "eth_estimateGas", "params": [{"from": "0xb60e8dd61c5d32be8058bb8eb970870f07233155", "to": "0xd46e8dd67c5d32be8058bb8eb970870f07244567", "gas": "0x76c0",
        "gasPrice": "0x9184e72a000", "value": "0x9184e72a", "data": "0xd46e8dd67c5d32be8d46e8dd67c5d32be8058bb8eb970870f072445675058bb8eb970870f072445675"}]},
    # insufficient funds
    {"method": "eth_feeHistory", "params": ["0x5", "latest", [20, 30]]},
    {"method": "eth_gasPrice", "params": []},
    {"method": "eth_getBalance", "params": [
        "0xc94770007dda54cF92009BFF0dE90c06F603a09f", "latest"]},
    {'method': 'eth_getBlockByHash', 'params': [
        "0xb3b20624f8f0f86eb50dd04688409e5cea4bd02d700bf6e79e9384d47d6a5a35", False]},
    {'method': 'eth_getBlockByNumber', 'params': ["latest", False]},
    {"method": "eth_getBlockTransactionCountByHash", "params": [
        "0xb3b20624f8f0f86eb50dd04688409e5cea4bd02d700bf6e79e9384d47d6a5a35"]},
    {"method": "eth_getBlockTransactionCountByNumber", "params": ["latest"]},
    # "latest" is more resilient across chains
    {"method": "eth_getCode", "params": [
        "0x06012c8cf97bead5deae237070f9587f8e7a266d", "latest"]},
    {"method": "eth_getLogs", "params": [{"topics": [
        "0x241ea03ca20251805084d27d4440371c34a0b85ff108f6bb5611248f73818b80"]}]},
    {"method": "eth_getProof", "id": 1, "params": ["0x7F0d15C7FAae65896648C8273B6d7E43f58Fa842", [
        "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"], "latest"]},
    {"method": "eth_getStorageAt", "params": ["0x295a70b2de5e3953354a6a8344e616ed314d7251",
        "0x6661e9d6d8b923d5bbaab1b96e1dd51ff6ea2a93520fdc9eb75d059238b8c5e9", "latest"]},  # "latest" is more resilient across chains
    {"method": "eth_getTransactionByBlockHashAndIndex", "params": [
        "0xb3b20624f8f0f86eb50dd04688409e5cea4bd02d700bf6e79e9384d47d6a5a35", "0x0"]},
    {"method": "eth_getTransactionByBlockNumberAndIndex",
        "params": ["0x5BAD55", "0x0"]},
    {"method": "eth_getTransactionByHash", "params": [
        "0xbb3a336e3f823ec18197f1e13ee875700f08f03e2cab75f0d0b118dabb44cba0"]},
    {"method": "eth_getTransactionCount", "params": [
        "0xc94770007dda54cF92009BFF0dE90c06F603a09f", "latest"]},  # "latest" is more resilient across chains
    {"method": "eth_getTransactionReceipt", "params": [
        "0xbb3a336e3f823ec18197f1e13ee875700f08f03e2cab75f0d0b118dabb44cba0"]},
    {"method": "eth_getUncleByBlockHashAndIndex", "params": [
        "0xb3b20624f8f0f86eb50dd04688409e5cea4bd02d700bf6e79e9384d47d6a5a35", "0x0"]},
    {"method": "eth_getUncleByBlockNumberAndIndex",
        "params": ["0x29c", "0x0"]},
    {"method": "eth_getUncleCountByBlockHash", "params": [
        "0xb3b20624f8f0f86eb50dd04688409e5cea4bd02d700bf6e79e9384d47d6a5a35"]},
    {"method": "eth_getUncleCountByBlockNumber", "params": ["0x5bad55"]},
    {"method": "eth_getWork", "params": []},
    {"method": "eth_hashrate", "params": []},
    {"method": "eth_maxPriorityFeePerGas", "params": []},
    {"method": "eth_mining", "params": []},
    {"method": "eth_protocolVersion", "params": []},
    {"method": "eth_sendRawTransaction", "params": [
        "0xf869018203e882520894f17f52151ebef6c7334fad080c5704d77216b732881bc16d674ec80000801ba02da1c48b670996dcb1f447ef9ef00b33033c48a4fe938f420bec3e56bfd24071a062e0aa78a81bf0290afbc3a9d8e9a068e6d74caa66c5e0fa8a46deaae96b0833"]},
    # eth_sendRawTransaction nonce too low: next nonce 17260, tx nonce 1
    # aurora-testnet: {'code': -32602, 'message': 'rejected: unknown chainid'}
    # avalanche-fuji, base-goerli, polygon-mumbai: {'code': -32000, 'message': 'only replay-protected (EIP-155) transactions allowed over RPC'}
    # near-testnet, starknet-goerli: not found
    #
    # eth_sendTransaction not supported by Infura
    # eth_sign not supported by Infura
    {"method": "eth_submitWork", "params": ["0x0000000000000001", "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "0xD1FE5700000000000000000000000000D1FE5700000000000000000000000000"]},
    {"method": "eth_syncing", "params": []},
    {'method': 'eth_newFilter', 'params': [{"topics": [
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]}]},
        # Other Filter methods - need to save this returned filter ID for them to use
    {"method": "net_listening", "params": []},
    {"method": "net_peerCount", "params": []},
    {"method": "net_version", "params": []},
    # Subcription methods?
    # Trace methods?
    {"method": "web3_clientVersion", "params": []},
]

# These methods need eth in the source account to work properly, or nonce has to be correct, etc.
# So they are hard to test generically
problemMethods = [
   'eth_call', 'eth_createAccessList', 'eth_estimateGas', 'eth_sendRawTransaction',
]

# If any methods are provided on command line, then use them, otherwise use sanitized default list
theMethods = []
methods_on_cli = False
if args.methods:
    # copy {method, params} across from the defaultMethods list
    for m in args.methods:
        try:
          theMethods.append(
              next(item for item in defaultMethods if item['method'] == m))
        except:
          print(f'Error: method "{m}" is not known', file=sys.stderr)
          exit(1)
    methods_on_cli = True  # maybe print extra output about the specific method calls
else:
    # copy all {method, params} across from the defaultMethod list, strip out problematic ones
    for item in defaultMethods:
      if not item['method'] in problemMethods:
         theMethods.append(item)

# Print summary header row
print("method,", ', '.join(theNetworks))

for m in theMethods:
    m['jsonrpc'] = '2.0'
    m['id'] = '1'
    summary = m['method']
    for n in theNetworks:
        url = f'https://{n}.infura.io/v3/{InfuraApiKey}'
        try:
          response = requests.post(url, data=json.dumps(m))
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
          print(f'Error: {n}, {m}, Status code: {response.status_code}, URL: {url}', file=sys.stderr)
          exit(1)

        jResponse = json.loads(response.text)

        # Print more detailed info if methods are specified on command line with '-m'
        if methods_on_cli:
          if jResponse.get('error') == None:
            print(f'{n}: {jResponse["result"]}')
          else:
            print(f'{n}: {jResponse["error"]}')


        if jResponse.get('error') == None:
            summary += ', Y'
        else:
            error_code = jResponse['error']['code']
            if n == 'palm-testnet' and m['method'] == 'eth_getBlockByHash' and error_code == -32600:
               # Palm is unique and returns an error instead of success and 'None' if the block hash is not found
               summary += ', Y'
            elif n == 'celo-alfajores' and error_code == -32000:
               # celo uses this generic error code for "Not implemented"
              summary += ', N(-32000)'
            elif n == 'base-goerli' and error_code == -32602:
               # base uses 32602 for "Not found" (and 32601 for eth_protocolVersion does not exist?!)
              summary += ', N(-32602)'
            elif error_code == -32004:
               # This non-standard error code returned by our proxy for "method not supported"
               summary += ', N(-32004)'
            elif error_code == -32601:
               # This is the common (correct?) error code for "Method not found" from the node
               summary += ', N'
            else:
              summary += f', {error_code}'

    print(summary)
