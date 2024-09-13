#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import requests
import json
import sys
import argparse
from chainids import theChainIds

parser = argparse.ArgumentParser(
    description='Test each Gas API endpoint is up.')
parser.add_argument('-k', '--api_key', metavar='INFURA_API_KEY', default=None,
                    help='Infura API Key to use (INFURA_API_KEY env var used by default).')
parser.add_argument('-v', '--verbose', action='store_true', default=False,
                    help='Make output more verbose.')

args = parser.parse_args()

load_dotenv()
if os.environ.get("INFURA_API_KEY") is None:
    print("ERROR: These environment vars need to exist: INFURA_API_KEY", file=sys.stderr)
    parser.print_help()
    exit(1)

InfuraApiKey = args.api_key or os.getenv("INFURA_API_KEY")

gasApiChains = {
  "arbitrum-nova": 42170,
  "cronos": 25,
  "fantom": 250,
  "filecoin": 314,
}

# Add chains that gas api supports but are not in chainids.py (i.e. not supported by Infura)
for c in gasApiChains:
  theChainIds[c] = gasApiChains[c]

for chain in theChainIds:
  # Get the current gas price from our Gas API
  gas_url = f'https://gas.api.infura.io/v3/{InfuraApiKey}/networks/{theChainIds[chain]}/suggestedGasFees'
  if args.verbose:
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

  print(f'{chain}: HTTP Status: {response.status_code}')

  if response.status_code == 502 or response.status_code == 404:
    print(response.text)
  else:
    jResponse = response.json()
    if response.status_code == 400:
        print(jResponse)
    if args.verbose:
        print(f'{json.dumps(jResponse, indent=4)}')

