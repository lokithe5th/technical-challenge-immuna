# technical challenge immuna
 Monitoring the optimism bridge

## Background
Bridges allow blockchains to represent the assets on a specific chain (for example, Ethereum Mainnnet) on another chain (for example, Optimistic Ethereum). This allows a user to “move” their assets onto other chains. This might be useful if one chain offers a 3% yield on TokenX, but another chain offers 5% yield on TokenX. A user who wishes to maximize returns would bridge their TokenX onto the chain with the higher yield. Another use case would be in making use of the reduced transaction fees on a Layer-2 like Optimism or Abritrum.

The on chain effect of bridging is that the specified token is locked inside a smart contract on the initial chain. Once the corresponding bridge on the target chain has determined that the asset has been transferred to the bridge contract, it mints an asset corresponding 1:1 (minus fees, if any) to the specified receiver address on the target chain.

In our example, if a user wants to transfer ETH from Ethereum Mainnet to Optimism they would deposit X amount of ETH into the Optimism Gateway (the bridge from Mainnet to Optimism, which can be viewed here). The transaction is relayed to the Optimism L2 Bridge and once the contract is satisfied that the ETH is successfully locked in the Mainnet bridge contract, it mints Optimistic ETH to the target address specified by the user. This allows the user to utilize his L1 assets on the Optimism L2. 

For ERC20 tokens the process is the same in principle, but care must be taken to inspect the business logic of the bridge being used. Tokens should not be minted out of nothing and the corresponding collateral must be locked on the origin chain. For example, should the amount of TokenX on Optimism be greater than the amount bridged to it from an origin chain - like Mainnet Ethereum - then users have liquidity risk in that there is not enough TokenX locked in the bridge contract on Mainnet to bridge all the TokenX tokens Mainnet. Should the bridge run out of TokenX, users will have to wait until liquidity is provided (i.e. when another deposits the same token into the bridge contract when bridging to Optimism). Only then would they be able to bridge their tokens back to Mainnet. 

The above is a simplification and it must be kept in mind that there may be multiple chains with a specific token operating at once. In addition, the possibility exists that some tokens are minted natively on an L2 or other chain. Liquidity challenges may arise out of normal economic activity and not only from malicious actors.
 
## Problem
The technical challenge requires: a proposal on how to monitor the Optimism: Gateway (the Optimism L1 bridge) for hacks or malfunction.

Bridge Specifics
Functionality: The bridge allows users to deposit ETH and other ERC20 tokens into it, and mints these tokens to the user. It should also facilitate the withdrawal of ETH and other tokens from the Optimism L2 back to Mainnet Ethereum, although this is disincentivized through contract design. Any withdrawals made through the L2 bridge to the L1 bridge have a waiting period of 7 days. Users bridging tokens back from the L2 are thus encouraged to do so through other third-party bridges. 

## Main vulnerabilities
Business logic operations remain in the hands of the multisig. The multisig for the Optimism ecosystem (including the Optimism L1 bridge) is in the hands of an anonymous set of individuals. Although this design is still standard, it remains a vulnerability.
The L1 contracts are proxied using a custom proxy which allows code changes and changes to data in storage slots through `setCode` and `setStorage` respectively. The trust assumption remains that the multisig (should it remain uncompromised) will continue to operate in the best interests of users.

*Please note: This design is common among current gen Layer-2s (and even some Layer-1s). Optimism PBC has long reiterated their commitment to decentralizing the protocol away from the multisig setup; the contracts in the upcoming Bedrock upgrade repo shows a movement towards this decentralization.*

## On-chain Indicators of Compromise/Malfunction
Given the characteristics of cross-chain bridges the below should be monitored to determine Optimism Bridge Health.

### Ether Balance of the Optimism L1 Bridge
The bridge should be monitored for large decreases in ETH balance. This can be achieved by polling the chain in regular intervals to determine if the ETH balance has a delta over time that is greater than expected.

### Direct ETH Transfers
The bridge is not expected to make normal transaction calls that directly affect the ether reserves. Direct calls by the contract to other addresses which transfer ETH away from the contract address should be treated as suspicious. The `_finalizeWithdrawal` is not called directly by the contract and transfers ETH from the contract address through an internal transaction. The chain should be polled regularly for such transactions.

### Success of Deposits from L1 to L2
Deposits into the L1 bridge should reflect as complete in around 25 minutes on the Layer 2 Network. On the L1 the deposit will emit an event with signature 0x35d79ab81f2b2017e19afb5c5571778877782d7a8786f5907f93b0f4702f4f23. 

The finalization of this deposit on the L2 (when the 1:1 value is minted to the depositor) will emit a Deposit Finalized event with signature 0xb0444523268717a02698be47d0803aa7468c00acbed2f8bd93a0459cde61dd89. 

A check can be performed to compare the deposits within a certain block range on the L1 bridge and the finalization of those deposits on the L2. For a given set of events within a block interval on L1 there must be a corresponding set of events on the L2. The L1 and L2 should be polled at regular intervals to check this indicator.

### High risk calls from Owner Account to the L1 Optimism Bridge
The primary concern for the bridge is multisig compromise, we should identify accounts that might have the power to compromise the system. The `owner` of the L1 Optimism Gateway (or bridge) is the Optimism Multisig at  0x9BA6e03D8B90dE867373Db8cF1A58d2F7F006b3A

Should the account become compromised it will result in a critical threat to all assets held in the bridge. The `owner` of the bridge contract can deploy arbitrary code and make changes to the storage of the bridge contract. 

Monitoring the transactions made by the Multisig to the bridge contract address allows early warning that the account has been compromised.

The expectation would be that Optimism PBC would notify users should any calls to these functions be expected as part of an upgrade or maintenance; an unexpected call should be treated as highly suspicious. 

The monitoring is complicated by the fact that the proxy contract used for the bridge (`L1ChugSplashProxy`) does not emit any events when the aforementioned functions are called. But, only the `owner` address can call these functions, thus any transaction from the `owner` to the bridge should be monitored at regular intervals.

## Risk Management and Mitigation Strategies
Although not required in the technical challenge, the intent of managing the risk of bridge compromise is clear. It is the nature of the blockchain that such attacks are likely to occur programmatically; the reality is that a user may not be able to save the ETH or tokens locked in the bridge contract itself once the attack or malfunction occurs. This does not mean nothing should be done. 

At the first sign of bridge compromise there will be panic in the market due to fear, uncertainty and doubt (because the collateral on the L1 Optimism Bridge has been drained). Risk management should focus on programmatically enabling accounts to exit the Optimism L2 chain through a third-party bridge (which is still likely to have liquidity for a short while) before the L1 bridge’s liquidity is drained.

In addition, DeFi strategies can be implemented to benefit the user account on L1 and L2 to further reduce the impact of losses (or perhaps generate a profit). This will depend on account and bridge specifics as well as client risk tolerance and investment timeline.
