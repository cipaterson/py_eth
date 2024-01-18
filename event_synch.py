#!/usr/bin/env python3

from web3 import Web3, IPCProvider
import time
import os
InfuraApiKey = os.environ.get("INFURA_API_KEY")


# instantiate Web3 instance
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/' + InfuraApiKey))

def handle_event(event):
    print(event)

def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        time.sleep(poll_interval)

def main():
    block_filter = w3.eth.filter('latest')
    log_loop(block_filter, 2)

if __name__ == '__main__':
    main()
