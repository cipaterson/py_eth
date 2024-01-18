#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from web3 import Web3, exceptions

load_dotenv()

theChainIds = {
    "mainnet": 1,
    "goerli": 5,
    "sepolia": 11155111,
    "linea-mainnet": 59144,
    "linea-goerli": 59140,
}

network='sepolia'

infura_url = f'https://{network}.infura.io/v3/{os.getenv("INFURA_API_KEY")}'

private_key = os.getenv('SIGNER_PRIVATE_KEY')
from_account = os.getenv('SIGNER_ACCOUNT')
to_account = os.getenv('SIGNER_ACCOUNT')  # same address as source!
web3 = Web3(Web3.HTTPProvider(infura_url))

try:
    from_account = web3.to_checksum_address(from_account)
except exceptions.InvalidAddress:
    print(f"Invalid 'from_account' address: {from_account}")

try:
    to_account = web3.to_checksum_address(to_account)
except exceptions.InvalidAddress:
    print(f"Invalid 'to_account' address: {to_account}")

nonce = web3.eth.get_transaction_count(from_account)
print(f'get_transaction_count={nonce}')
fee_per_gas='0.1'
tx = {
    'type': '0x2',
    'nonce': nonce,
    'from': from_account,
    'to': to_account,
    'value': web3.to_wei(0.0, 'ether'), # zero
    'maxFeePerGas': web3.to_wei(fee_per_gas, 'gwei'),
    'maxPriorityFeePerGas': web3.to_wei(fee_per_gas, 'gwei'),
    'chainId': theChainIds[network]
}
try:
  gas = web3.eth.estimate_gas(tx)
except ValueError as inst:
  print(f'{inst.__class__}: estimate_gas: {inst.args}')
  exit()
tx['gas'] = gas

print(f'{tx=}')
try:
  signed_tx = web3.eth.account.sign_transaction(tx, private_key)
except (ValueError, TypeError) as inst:
   print(f'{inst.__class__}: sign_transaction: {inst.args}')
   exit()

try:
  tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
except ValueError as inst:
  print(f'{inst.__class__}: send_raw_transaction: {inst.args}')
  exit()
else:
  print("Transaction hash: " + str(web3.to_hex(tx_hash)))

# could use wait_for_transaction_receipt here


