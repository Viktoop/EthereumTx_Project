from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from web3 import Web3
import requests
from requests.structures import CaseInsensitiveDict
import datetime
import json


provider = Web3.HTTPProvider('https://mainnet.infura.io/v3/b7930bdbe91a4c04921e12e001bea157')
w3 = Web3(provider)


def tx_search(request):
    address_checksum = request.GET.get('address_checksum')
    block_number = request.GET.get('block_number')
    context = None
    if address_checksum is not None and block_number is not None:
        df = find_tx(int(block_number), address_checksum.lower())
        context = {
            'df': df.to_html(classes="table table-dark"),
            'address': address_checksum,
            'block': block_number
        }
    return render(request, 'eth_tx.html', context)


def wallet_balance(request):
    address_checksum = request.GET.get('address_checksum')
    date_str = request.GET.get('date')
    context = None
    if address_checksum is not None and date_str is not None:
        date_list = date_str.split('-')
        date = datetime.datetime(int(date_list[0]), int(date_list[1]), int(date_list[2]), 2)
        eth, tokens = get_balance(address_checksum.lower(), date)
        context = {
            'address': address_checksum,
            'date': date_str,
            'eth': eth,
            'tokens': tokens
        }
    return render(request, 'eth_balance.html', context)


def find_tx(st_blk, adr_lower):
    df = pd.DataFrame(columns=['Address From', 'Address To', 'Amount ETH', 'Amount USD'])
    end_blk = int(w3.eth.get_block_number())
    for idx in range(st_blk, end_blk):
        print('Fetching block %d, remaining: %d, progress: %d%%' % (
            idx, (end_blk - idx), 100 * (idx - st_blk) / (end_blk - st_blk)))

        block = w3.eth.getBlock(idx, full_transactions=True)

        for tx in block.transactions:
            if tx['to']:
                to_matches = tx['to'].lower() == adr_lower
            else:
                to_matches = False

            if tx['from']:
                from_matches = tx['from'].lower() == adr_lower
            else:
                from_matches = False

            if to_matches or from_matches:
                print('Found transaction with hash %s' % tx['hash'].hex())
                new_row = {'Address From': tx['from'].lower(),
                           'Address To': tx['to'].lower(),
                           'Amount ETH': tx['value'] / 1000000000000000000,
                           'Amount USD': round(tx['value'] / 1000000000000000000 * 3440, 2)}
                print('Adding to dataframe')
                df = df.append(new_row, ignore_index=True)
    return df


def find_block(date, low, high):
    print('Binary searching blocks: ' + str(low) + ' - ' + str(high))
    if high >= low:
        middle = low + (high - low) // 2
        block = w3.eth.getBlock(middle, full_transactions=True)
        dt = datetime.datetime.fromtimestamp(block['timestamp'])
        dt = datetime.datetime(dt.year, dt.month, dt.day, dt.hour)

        if dt == date:
            return middle
        elif dt < date:
            return find_block(date, middle + 1, high)
        else:
            return find_block(date, low, middle - 1)

    else:
        return high


# Request to get list of ERC20 tokens for wallet at specific block
# Returns number of tokens as length of received list
def get_token_amount(adr_checksum, block_no):
    url = "https://deep-index.moralis.io/api/v2/" + adr_checksum + "/erc20?chain=eth&to_block=" + str(block_no)

    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["X-API-Key"] = "r6K1Y6a8vM6XHxNN4KcDIbgF9UqCPmgFSQrGj02AGQ75nV29jUo6Q8Qs6mMvWqBW"

    resp = requests.get(url, headers=headers)
    resp_json = resp.json()
    return len(resp_json)


def get_balance(adr_checksum, date):
    block_low, block_high = 0, int(w3.eth.get_block_number())
    block_number = find_block(date, block_low, block_high)

    provider_url = 'https%3A%2F%2Fpydtqqecvnto.bigmoralis.com%3A2053%2Fserver'
    url = "https://deep-index.moralis.io/api/v2/" + adr_checksum + "/balance?chain=eth&providerUrl=" + provider_url + "&to_block=" + str(block_number) + ""

    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["X-API-Key"] = "r6K1Y6a8vM6XHxNN4KcDIbgF9UqCPmgFSQrGj02AGQ75nV29jUo6Q8Qs6mMvWqBW"

    resp = requests.get(url, headers=headers)
    resp_json = resp.json()

    token_no = get_token_amount(adr_checksum, block_number)

    return int(resp_json['balance']) / 1000000000000000000, token_no
