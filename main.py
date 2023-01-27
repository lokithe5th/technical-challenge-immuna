import requests
import json
import datetime
import time
import calendar

ETHERSCAN_KEY = "A93198DXZCATMIY5D79ECVWIVTTNPPUR9G"
OPTIMISTIC_ETHERSCAN_KEY = "1S8RNDEVJXIT1MP36XSR699BWUXIU6JP64"
wallet = "0x809f55d088872ffb148f86b5c21722caa609ac72"
OPTIMISM_BRIDGE = "0x99c9fc46f92e8a1c0dec1b1747d010903e884be1"
BRIDGE_OWNER = "0x9996571372066A1545D3435C6935e3F9593A7eF5"
# Very few transactions occur from this address
OWNER_START_BLOCK = 12686795
# The Bridge has many transactions, no need to go back so far
BRIDGE_START_BLOCK = 16496975

# Checks the owner of the Bridge Contracts for transactions
def checkBridgeOwnerTransactions(bridgeOwner: str = None):
    date = datetime.datetime.utcnow()
    utc_time = calendar.timegm(date.utctimetuple())
    assert(wallet is not None)
    url_params = {
        'module': 'account',
        'action': 'txlist',
        'address': bridgeOwner,
        'startblock': OWNER_START_BLOCK,
        'endblock': 99999999,
        'soft': 'asc',
        'apikey': ETHERSCAN_KEY
    }

    response = requests.get('https://api.etherscan.io/api', params=url_params)
    responseParsed = json.loads(response.content)
    assert(responseParsed['message'] == 'OK')

    txs = responseParsed['result']
    # Craft the `logs`, including only the txs that were made by the `Bridge Owner Account` to the bridge
    logs = [ {'from': tx['from'], 'to': tx['to'], 'value': tx['value'], 'timestamp': tx['timeStamp']} 
         for tx in txs if (tx['to'] == OPTIMISM_BRIDGE and int(tx['timeStamp']) > (utc_time - 60)) ]
    if (logs == []):
        print(f'Bridge Owner Txs: OK')
    else:
        print('New Txs by the Bridge Owner!')
        for log in logs:
            print(log)

def checkBridgeEtherOut(bridge: str = None):
    url_params = {
        'module': 'account',
        'action': 'txlist',
        'address': bridge,
        'startblock': BRIDGE_START_BLOCK,
        'endblock': 99999999,
        'soft': 'asc',
        'apikey': ETHERSCAN_KEY
    }

    response = requests.get('https://api.etherscan.io/api', params=url_params)
    responseParsed = json.loads(response.content)
    assert(responseParsed['message'] == 'OK')

    txs = responseParsed['result']
    logs = [ {'from': tx['from'], 'to': tx['to'], 'value': tx['value'], 'timestamp': tx['timeStamp']} 
         for tx in txs if int(tx['value']) > 0 and tx['from'] == bridge ]
    if (logs == []):
        print('Bridge Ether Out Cehck OK: TRUE')
    else:
        print('New Txs by the Bridge!')
        for log in logs:
            print(log)

while True:
    checkBridgeOwnerTransactions(BRIDGE_OWNER)
    checkBridgeEtherOut(OPTIMISM_BRIDGE)
    print('Repolling in 12s')
    time.sleep(12)