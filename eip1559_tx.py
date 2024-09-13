#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from web3 import Web3, exceptions
from web3.datastructures import AttributeDict
import requests
import json
import time
import sys
import argparse
from chainids import theChainIds

parser = argparse.ArgumentParser(
    description='Send, zero value, Type 2 transaction to network and retry if gas is too low.')
parser.add_argument('-k', '--api_key', metavar='INFURA_API_KEY', default=None,
                    help='Infura API Key to use (INFURA_API_KEY env var used by default).')
parser.add_argument('-v', '--verbose', action='store_true', default=False,
                    help='Make output more verbose.')
parser.add_argument('-g', '--gas', type=str, choices=["low", "medium", "high", "cheap", "vcheap"], default="cheap",
                    help='Choose gas price level, default is very cheap.')
parser.add_argument(
    "-n", "--network", help="network to request on (default: use ETHEREUM_NETWORK env var)")

args = parser.parse_args()

load_dotenv()
if os.environ.get("SIGNER_PRIVATE_KEY") is None:
    print("ERROR: These environment vars need to exist: SIGNER_PRIVATE_KEY, SIGNER_ACCOUNT, INFURA_API_KEY, ETHEREUM_NETWORK", file=sys.stderr)
    parser.print_help()
    exit(1)

network = args.network or os.getenv("ETHEREUM_NETWORK")
InfuraApiKey = args.api_key or os.getenv("INFURA_API_KEY")

infura_url = f'https://{network}.infura.io/v3/{InfuraApiKey}'
print(f'{infura_url=}')

private_key = os.getenv('SIGNER_PRIVATE_KEY')
from_account = os.getenv('SIGNER_ACCOUNT')
# NOTE! same address as the source! (why not?)
to_account = os.getenv('SIGNER_ACCOUNT')

web3 = Web3(Web3.HTTPProvider(infura_url))

from_account = web3.to_checksum_address(from_account)
to_account = web3.to_checksum_address(to_account)

# Get the current gas price from our Gas API
gas_url = f'https://gas.api.infura.io/v3/{InfuraApiKey}/networks/{theChainIds[network]}/suggestedGasFees'
print(f'{gas_url=}')
try:
    response = requests.get(gas_url)
except:
    print(f"Error: Can't connect: {url}", file=sys.stderr)
    exit(1)

if response.status_code == 401:
    print(
        'Error: Status code 401, use --api_key to provide a valid Infura API key', file=sys.stderr)
    exit(1)

jResponse = response.json()
estimatedBaseFee = jResponse["estimatedBaseFee"]
print(f'{estimatedBaseFee=}')
print(f'{jResponse["priorityFeeTrend"]=}')
print(f'{jResponse["baseFeeTrend"]=}')
if args.verbose:
    print(f'{json.dumps(jResponse, indent=4)}')

# Use the low option if cheap, then make cheaper later
gas_level = args.gas if args.gas != "cheap" and args.gas != "vcheap" else "low"

suggestedMaxFeePerGas = jResponse[gas_level]["suggestedMaxFeePerGas"]
suggestedMaxPriorityFeePerGas = jResponse[gas_level]["suggestedMaxPriorityFeePerGas"]

maxFeePerGas = suggestedMaxFeePerGas
maxPriorityFeePerGas = suggestedMaxPriorityFeePerGas
# change the gas price estimates to make the tx as cheap as possible:
if args.gas == "cheap":
    # reduce fee per gas by a bit (the low estimate is usually 1Gwei above the base fee)
    maxFeePerGas = float(suggestedMaxFeePerGas) - 0.5
    # zero tip or:-  ## int(suggestedMaxPriorityFeePerGas)/2  # Half the suggested tip?
    maxPriorityFeePerGas = 0
elif args.gas == "vcheap":
    # reduce fee per gas by a LOT!
    maxFeePerGas = float(estimatedBaseFee) + 0.1
    # zero tip
    maxPriorityFeePerGas = 0

print(f'{maxFeePerGas=}')
print(f'{maxPriorityFeePerGas=}')

nonce = web3.eth.get_transaction_count(from_account)
tx = {
    'type': '0x2',
    'nonce': nonce,
    'from': from_account,
    'to': to_account,
    'value': web3.to_wei(0.0, 'ether'),  # NOTE! zero value tx
    'maxFeePerGas': web3.to_wei(maxFeePerGas, 'gwei'),
    'maxPriorityFeePerGas': web3.to_wei(maxPriorityFeePerGas, 'gwei'),
    'chainId': theChainIds[network]
}
# Estimate the amount of gas used by above tx (21_000 for a simple value transfer)
# This can return an error if the gas _price_ is too low also.
try:
    gas = web3.eth.estimate_gas(tx)
except ValueError as inst:
    print(f'Error:{inst.__class__}: estimate_gas: {inst.args}')
    exit()

tx['gas'] = gas

# Loop until tx is safe on chain
while True:
    print("Transaction to send:")
    print(json.dumps(tx, indent=4))

    try:
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    except (ValueError, TypeError) as inst:
        print(f'{inst.__class__}: sign_transaction: {inst.args}')
        exit()

    try:
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    except ValueError as inst:
        print(f'{inst.__class__}: send_raw_transaction: {inst.args}')
        # NOTE if replacement tx is underpriced then gas costs are probably rising fast
        #   It would be better to re-check the suggested gas prices and use those.
        exit()
    else:
        print("Transaction hash: " + str(web3.to_hex(tx_hash)))

    # use wait_for_transaction_receipt to poll for the tx on the chain
    try:
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        break
    except Exception as e:
        print(f'Error:{e.__class__}: estimate_gas: {e.args}')
        print("Increasing maxPriorityFeePerGas and maxFeePerGas an arbitrary amount to speed it up")
        tx['maxPriorityFeePerGas'] = web3.to_wei(
            maxPriorityFeePerGas + 1, 'gwei')
        tx['maxFeePerGas'] = web3.to_wei(maxFeePerGas + 1, 'gwei')

# One customer used this method to determine when the tx is mined -
#   problem is get_tx_receipt is better and costs one request instead of two
# while True:
    # tx_count = (web3.eth.get_transaction_count(from_account))
    # tx_pending_count = (web3.eth.get_transaction_count(from_account, block_identifier='pending'))
    # print(f'{tx_count=}, {tx_pending_count=}')
    # if tx_count == tx_pending_count or time.time()-t > timeout*1000:
    #    break
    # time.sleep(0.1)

print("Transaction receipt:")
print(json.dumps(dict(tx_receipt), indent=4, default=vars))

tx_onchain = web3.eth.get_transaction(tx_hash)
print("Transaction on chain:")
print(json.dumps(tx_onchain, indent=4, default=vars))
