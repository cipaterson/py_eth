#!/usr/bin/env python3
import requests
import os
import time
import json

def get_balance(InfuraApiKey):
  response = requests.post(
    "https://polygon-mainnet.infura.io/v3/" + InfuraApiKey,
    data='{"id": "1", "jsonrpc": "2.0", "method": "relay_getBalance", "params": ["0x90953B94B6F18c23eE0707ec6e4532A2411C3333"]}'
  )
  ## print(response.text)
  balance = float(json.loads(response.text)["result"]["balance"])
  balance /= 1000000000000000000
  return balance

def main():
    InfuraApiKey = os.environ.get("INFURA_API_KEY")

    prev_balance = get_balance(InfuraApiKey)
    pos_neg_count = 0
    while True:
      time.sleep(1)
      balance = get_balance(InfuraApiKey)
      if balance != prev_balance:
        if prev_balance-balance >0:
          pos_neg_count += 1
        else:
          pos_neg_count -= 1
        print(f"{time.asctime()}: Balance={balance:.3f}, difference={prev_balance-balance:.3f}, pos_neg_count={pos_neg_count}")
        prev_balance = balance

if __name__ == "__main__":
  main()