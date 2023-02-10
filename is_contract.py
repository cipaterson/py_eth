from web3 import Web3
import os

InfuraApiKey = os.environ.get("INFURA_API_KEY")

def is_contract(w3: Web3, address, block_number):
	code = w3.eth.get_code(address )
	return len(code) != 0

w3a = Web3(Web3.HTTPProvider('https://mainnet.aurora.dev'))
w3i = Web3(Web3.HTTPProvider('https://aurora-mainnet.infura.io/v3/' + InfuraApiKey))

print(is_contract(w3a, '0x4E8fE8fd314cFC09BDb0942c5adCC37431abDCD0', 68202136))
print(is_contract(w3i, '0x4E8fE8fd314cFC09BDb0942c5adCC37431abDCD0', 68202136))

print(is_contract(w3a, '0x00000fc3E1d134BdC21E2A0dcD343CfE68e8610d', 68202136))
print(is_contract(w3i, '0x00000fc3E1d134BdC21E2A0dcD343CfE68e8610d', 68202136))

