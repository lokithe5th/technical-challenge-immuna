import requests
import json
import datetime
import time
import calendar
import constants

blockHeightL1: str
blockHeightL2: str

# Let's get the latest blocks for L1 and L2
def getBlocks(api: str, key: str):
    date = datetime.datetime.utcnow()
    utc_time = calendar.timegm(date.utctimetuple())
    assert(constants.L1_OPTIMISM_BRIDGE is not None)
    url_params = {
        'module': 'block',
        'action': 'getblocknobytime',
        'timestamp': utc_time,
        'closest': 'before',
        'apikey': key
    }

    response = requests.get(api, params=url_params)
    responseParsed = json.loads(response.content)

    assert(responseParsed['message'] == 'OK')

    return responseParsed['result']

# Checks the owner of the Bridge Contracts for transactions
# As a primary point of failure it can be an indicator of suspicious activity
def checkBridgeOwnerTransactions(bridgeOwner: str = None):
    date = datetime.datetime.utcnow()
    utc_time = calendar.timegm(date.utctimetuple())
    assert(constants.L1_OPTIMISM_BRIDGE is not None)
    url_params = {
        'module': 'account',
        'action': 'txlist',
        'address': bridgeOwner,
        'startblock': constants.OWNER_START_BLOCK,
        'endblock': 99999999,
        'soft': 'asc',
        'apikey': constants.ETHERSCAN_L1_KEY
    }

    response = requests.get('https://api.etherscan.io/api', params=url_params)
    responseParsed = json.loads(response.content)
    assert(responseParsed['message'] == 'OK')

    txs = responseParsed['result']
    # Craft the `logs`, including only the txs that were made by the `Bridge Owner Account` to the bridge
    logs = [ {'from': tx['from'], 'to': tx['to'], 'value': tx['value'], 'timestamp': tx['timeStamp']} 
         for tx in txs if (tx['to'] == constants.L1_OPTIMISM_BRIDGE and int(tx['timeStamp']) > (utc_time - 60)) ]
    if (logs == []):
        print(f'Bridge Owner Txs: OK')
    else:
        print('New Txs by the Bridge Owner!')
        for log in logs:
            print(log)

# Check that there hasn't been any ETH transferred out of the bridge directly
# Direct ETH transfers are unlikely and should be flagged as suspicious
def checkBridgeEtherOut(bridge: str = None):
    url_params = {
        'module': 'account',
        'action': 'txlist',
        'address': bridge,
        'startblock': constants.BRIDGE_START_BLOCK,
        'endblock': 99999999,
        'soft': 'asc',
        'apikey': constants.ETHERSCAN_L1_KEY
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

# Check L1 deposits against L2 withdrawals
def checkL1toL2(l1Bridge, l2Bridge):
    # Find the L1 deposit events
    url_params = {
        'module': 'logs',
        'action': 'getLogs',
        'address': l1Bridge,
        'startblock': str(int(blockHeightL1) - 100),
        'endblock': 99999999,
        'apikey': constants.ETHERSCAN_L1_KEY
    }

    response = requests.get(constants.ETHERSCAN_L1, params=url_params)
    responseParsed = json.loads(response.content)
    assert(responseParsed['message'] == 'OK')

    txs = responseParsed['result']
    #print(txs)
    l1Logs = [ {'topics': tx['topics'], 'data': tx['data'], 'timestamp': tx['timeStamp']} 
         for tx in txs if (tx['topics'][0] == constants.EVENT_INITIATE_DEPOSIT)]

    # Find the L2 withdraw events
    url_params = {
        'module': 'logs',
        'action': 'getLogs',
        'address': l2Bridge,
        'startblock': str(int(blockHeightL2) - 100),
        'endblock': 99999999,
        'apikey': constants.ETHERSCAN_L2_KEY
    }

    response = requests.get(constants.ETHERSCAN_L2, params=url_params)
    responseParsed = json.loads(response.content)
    assert(responseParsed['message'] == 'OK')

    txs = responseParsed['result']
    #print(txs)
    l2Logs = [ {'topics': tx['topics'], 'data': tx['data'], 'timestamp': tx['timeStamp']} 
         for tx in txs if (tx['topics'][0] == constants.EVENT_DEPOSIT_FINALIZED)]

    if (l1Logs == []):
        print('Bridge Ether Out Cehck OK: TRUE')
    else:
        print('New Events by the Bridge!')
        for log in l1Logs:
            depositorAddress = '0x' + log['data'][27:66]
            print(depositorAddress)
        print('L2 logs')
        for log in l2Logs:
            withdrawAddress = '0x' + log['data'][27:66]
            print(withdrawAddress)

blockHeightL1 = getBlocks(constants.ETHERSCAN_L1, constants.ETHERSCAN_L1_KEY)
blockHeightL2 = getBlocks(constants.ETHERSCAN_L2, constants.ETHERSCAN_L2_KEY)
print('L1: ', blockHeightL1, ' L2: ', blockHeightL2)

checkL1toL2(constants.L1_OPTIMISM_BRIDGE, constants.L2_OPTIMISM_BRIDGE)

# Run the script
#while True:
    #checkBridgeOwnerTransactions(constants.BRIDGE_OWNER)
    #checkBridgeEtherOut(constants.OPTIMISM_BRIDGE)
    #print('Repolling in 12s')
    #time.sleep(12)