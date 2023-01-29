import datetime
import requests
import json
import calendar
import constants

# Teches the latest blocks target chain for L1 and L2
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