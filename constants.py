# Constants
# IMPORTANT: the API Keys should be moved in to an .env if deployed publicly

# Etherscan
# Etherscan APIs
ETHERSCAN_L1 = 'https://api.etherscan.io/api'
ETHERSCAN_L2 = 'https://api-optimistic.etherscan.io/api'
# Etherscan API keys
ETHERSCAN_L1_KEY = "A93198DXZCATMIY5D79ECVWIVTTNPPUR9G"
ETHERSCAN_L2_KEY = "1S8RNDEVJXIT1MP36XSR699BWUXIU6JP64"

# Optimism Bridge Addresses Layer 1 and Layer 2
L2_OPTIMISM_BRIDGE = "0x4200000000000000000000000000000000000010"
L1_OPTIMISM_BRIDGE = "0x99c9fc46f92e8a1c0dec1b1747d010903e884be1"
# Optimism bridge owner address
BRIDGE_OWNER = "0x9996571372066A1545D3435C6935e3F9593A7eF5"

# Reserve constants
# The expect brdige reserve as of 29 Jan 2023
BRIDGE_RESERVE = 250*10**21
RESERVE_DIFFERENCE = 10

# Block constants
STARTBLOCK_OFFSET = 100 

# Polling time in seconds
POLLING_TIME = 60

# Event signatures (used for filtering)
EVENT_INITIATE_DEPOSIT = '0x35d79ab81f2b2017e19afb5c5571778877782d7a8786f5907f93b0f4702f4f23'
EVENT_DEPOSIT_FINALIZED = '0xb0444523268717a02698be47d0803aa7468c00acbed2f8bd93a0459cde61dd89'

# Fallback startblocks
L1_FALLBACK_START_BLOCK = 16516334
L2_FALLBACK_START_BLOCK = 71216274