import datetime
import requests
import json
import calendar
import constants

# Teches the latest blocks target chain for L1 and L2
def getBlocks(api: str, key: str) -> int:
    date = datetime.datetime.utcnow()
    utcTime = calendar.timegm(date.utctimetuple())
    assert(constants.L1_OPTIMISM_BRIDGE is not None)
    urlParams = {
        'module': 'block',
        'action': 'getblocknobytime',
        'timestamp': utcTime,
        'closest': 'before',
        'apikey': key
    }

    response = requests.get(api, params=urlParams)
    responseParsed = json.loads(response.content)

    assert(responseParsed['message'] == 'OK')

    return int(responseParsed['result'])

# Simple helper function to take care of the API calls to Etherscan
def getTransactions(api: str, params: object) -> list:
    response = requests.get(api, params=params)
    responseParsed = json.loads(response.content)
    return responseParsed['result']


