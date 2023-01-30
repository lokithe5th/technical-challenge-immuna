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

    # From time to time there are bad responses from the Etherscan API
    try:
        response = requests.get(api, params=urlParams)
        responseParsed = json.loads(response.content)
        assert(responseParsed['message'] == 'OK')

    except:
        print('Error in request or response from Etherscan API. Please check URL params or API service status.')

    else:
        return int(responseParsed['result'])

# Simple helper function to take care of the API calls to Etherscan
def getTransactions(api: str, params: object) -> list:
    response = requests.get(api, params=params)
    responseParsed = json.loads(response.content)
    return responseParsed['result']


