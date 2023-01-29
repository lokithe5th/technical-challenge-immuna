import requests
import json
import time
import constants
from helpers import getBlocks

blockHeightL1: str
blockHeightL2: str

# Checks the owner of the Bridge Contracts for transactions
# As a primary point of failure it can be an indicator of suspicious activity
def checkBridgeOwnerTransactions(bridgeOwner: str = None):
    assert(constants.L1_OPTIMISM_BRIDGE is not None)
    url_params = {
        'module': 'account',
        'action': 'txlist',
        'address': bridgeOwner,
        'startblock': int(blockHeightL1) - 100,
        'endblock': 99999999,
        'soft': 'asc',
        'apikey': constants.ETHERSCAN_L1_KEY
    }

    response = requests.get('https://api.etherscan.io/api', params=url_params)
    responseParsed = json.loads(response.content)

    txs = responseParsed['result']
    # Craft the `logs`, filtering for txs that were made by the `Bridge Owner Account` to the bridge
    # in the last 60 seconds
    logs = [ {'from': tx['from'], 'to': tx['to'], 'value': tx['value'], 'timestamp': tx['timeStamp']} 
         for tx in txs if tx['to'] == constants.L1_OPTIMISM_BRIDGE]
    # Ideally we don't want any logs to survive
    if (logs == []):
        print('Bridge Owner Txs: OK')
        return True
    else:
        print('CAUTION: new Txs by the Bridge Owner!')
        for log in logs:
            print(log)
        return False

# Check that there hasn't been any ETH transferred out of the bridge directly
# Direct ETH transfers are unlikely and should be flagged as highly suspicious
# This function searches for ETHER out transactions in the last 100 blocks
def checkBridgeEtherOut(bridge: str = None):
    url_params = {
        'module': 'account',
        'action': 'txlist',
        'address': bridge,
        'startblock': int(blockHeightL1) - 100,
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
        print('Bridge Ether Out: OK')
        return True
    else:
        print('CAUTION: new ether OUT Txs by the Bridge')
        for log in logs:
            print(log)
        return False

# Check the bridge reserves
# The assumption is that any drop in reserves greater than `RESERVE_DIFFERENCE` is suspicious
# Ideally this check should use the ETHER balance at a block height in the past and check the difference
# between the current reserves and the reserves at that point in time.
# That functionality is not available with the free etherscan API calls, but can be done on `pro` plans
# For now, the expected bridge reserve is given by `BRIDGE_RESERVE`, not ideal, but demonstrates the functionality
def checkL1Reserves(bridge: str = None):
    url_params = {
        'module': 'account',
        'action': 'balance',
        'address': bridge,
        'tag': 'latest',
        'apikey': constants.ETHERSCAN_L1_KEY
    }

    response = requests.get('https://api.etherscan.io/api', params=url_params)
    responseParsed = json.loads(response.content)
    assert(responseParsed['message'] == 'OK')

    l1Reserves = responseParsed['result']
    if (int(l1Reserves) < (constants.BRIDGE_RESERVE - constants.BRIDGE_RESERVE/constants.RESERVE_DIFFERENCE)):
        print('Reserves: Not OK')
        return False

    print('Reserves: OK')
    return True

# Check L1 deposits made against L2 deposits finalized
# The funtion takes a sample of the last 75 to 100 blocks and looks for deposits to the bridge
# Then it scans the L2 block range starting at (rouhgly) 25 minutes in the past
# This is taken as a sample of bridge health
def checkL1toL2(l1Bridge, l2Bridge):
    # Find the L1 deposit events
    url_params = {
        'module': 'logs',
        'action': 'getLogs',
        'address': l1Bridge,
        'fromBlock': str(int(blockHeightL1) - 100),
        'toBlock': str(int(blockHeightL1) - 50),
        'topic0' : constants.EVENT_INITIATE_DEPOSIT,
        'apikey': constants.ETHERSCAN_L1_KEY
    }

    response = requests.get(constants.ETHERSCAN_L1, params=url_params)
    responseParsed = json.loads(response.content)
    assert(responseParsed['message'] == 'OK')

    txs = responseParsed['result']
    l1Logs = [ {'fromAddress': tx['topics'][1], 'toAddress': tx['topics'][2], 'value': tx['data'][2:65]} 
         for tx in txs if (tx['topics'][0] == constants.EVENT_INITIATE_DEPOSIT)]

    # Find the L2 withdraw events
    healthCheck : bool = True
    for log in l1Logs:

        url_params = {
            'module': 'logs',
            'action': 'getLogs',
            'address': l2Bridge,
            'fromBlock': str(int(blockHeightL2) - 1500),
            'toBlock': 99999999,
            'topic0': constants.EVENT_DEPOSIT_FINALIZED,
            'topic0_3_opr' : 'and',
            'topic3' : log['fromAddress'],
            'apikey': constants.ETHERSCAN_L2_KEY
        }

        response = requests.get(constants.ETHERSCAN_L2, params=url_params)
        responseParsed = json.loads(response.content)

        txs = responseParsed['result']
        l2Logs = [ {'fromAddress': tx['topics'][1], 'toAddress': tx['topics'][2], 'value': tx['data'][66:129]} 
            for tx in txs]

        # If the response is NOTOK the check fails
        # If the value of the L2 tx is not the same as the value of the L1, the check fails
        if (responseParsed['message'] != 'OK' or (l2Logs[0]['value'] != log['value'])):
            healthCheck = False

    if (healthCheck):
        print('L1 -> L2 Deposits: OK')
        return healthCheck
    else:
        print('l1 -> L2 Deposits: NOT OK')
        return healthCheck

# Block heights are needed as starting points for the script
blockHeightL1 = getBlocks(constants.ETHERSCAN_L1, constants.ETHERSCAN_L1_KEY)
blockHeightL2 = getBlocks(constants.ETHERSCAN_L2, constants.ETHERSCAN_L2_KEY)

while True:
    # Check and report each component
    bridgeOwnerCheck = checkBridgeOwnerTransactions(constants.BRIDGE_OWNER)
    bridgeEtherCheck = checkBridgeEtherOut(constants.L1_OPTIMISM_BRIDGE)
    bridgeL1Reserves = checkL1Reserves(constants.L1_OPTIMISM_BRIDGE)
    # Fix for etherscan API rate limit bug
    time.sleep(2)
    bridgeDepositHealth = checkL1toL2(constants.L1_OPTIMISM_BRIDGE, constants.L2_OPTIMISM_BRIDGE)

    # Return the status of the bridge
    bridgeHealth = bridgeOwnerCheck or bridgeEtherCheck or bridgeL1Reserves or bridgeDepositHealth
    print(bridgeHealth)
    time.sleep(constants.POLLING_TIME)