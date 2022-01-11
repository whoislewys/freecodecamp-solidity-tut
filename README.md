here's where im putting my solutions/follow along code + modifications to select projects from this tutorial: https://www.youtube.com/watch?v=M576WGiDBdQ

it's quick and dirty

--------------

Lesson 0: Blockchain basics

Features
* censorship resistant
* decentralized using cryptography
* Security + immutability
* removal of counterparty risk (e.g. insurance products
* party executes agreement against their interest leads to them not wanting to fulfill)
* trust minimzed agreements. deterministic code works the same way every time.

vitalik is cracked, instead of creating special purpose blockchains and coins, create blockchain with smart contracts

actually, in 1994, nick szabo (super cracked wtf) came up with the idea for smart contracts

Technically, BTC also has smart contracts, but they're not turing complete (technically, gas makes eth not turing complete as well, but it's about as turing complete as it gets. pedants)

#### Oracle problem
Blockchains are deterministic.

Superior agreements need real world data, outside of the blockchain. Hard to do this deterministically.

Oracles solve this (maybe types?). Oracles and their offchain data + computations have to be decentralized as well. or else, what's the point of doing a smart contract?

Chainlink is a decentralized modular oracle network. Allows bringing external data on chain + do external computation

Data, randomness, any computation you could imagine 😎

## How blockchains work
Great learn by doing example
https://andersbrownworth.com/blockchain/

#### What is a block?
It's a hashed chunk of data
The properties of this "Block" data type are:

Block
Nonce
Data

What is "mining a block"?
From the miner's perspective, block has a known block number, data, and hash. Miner must guess (brute-force, unless you can break keccak256 hash function) the nonce. When a miner guesses the nonce that resolves to the proper hash, they get a reward

(question, why keccak256?)

#### Blockchain:

Linked list of blocks, each Block now has an additional "previous" property pointing to the hash of the previous block


You can change a piece of data early in the chain, but this will change the hash of that block, which makes the "prev" property of all following blocks invalid (Block1.cur_hash != Block2.prev_hash)

If you want to change data on chain, you can. Change data in block n, you can mine all n+... blocks and chain becomes valid again

#### Distrubuted blockchains:
Multiple copies of the chain. Each peer has a copy of the chain, all peers equally powerful.

Look at the head of each copy of the chain to make sure they are all matched up.

(question, what happens if there are 2 blocks in a row with colliding hashes?)

If a certain peer has a different HEAD hash, democracy reigns supreme. If peer 1 has HEAD hash of 9999999, but peer 2 and peer 3 have HEAD hash of 6969696969, peer 2 and peer 3 continue getting mining rewards, peer 1 is left behind as the chain with consensus marches on, peers mining new blocks.


What is nonce?
Short for "number used once"
Meant to be a "number used once" to get a hash collision when hashing together with the other data in a block

However, it's ALSO used to define the tx number for an account address in ethereum


#### Private/public keys, elliptic curves

Private key, only known to the holder. Used to "sign" transactions

Elliptic Curve Digital Signature Algorithm used to create a private key & public key. The private key maps to the public key such that people can verify you are doing something on-chain, however, With proper safety, your private key is unguessable. So as long as you keep your private key safe, you and only you are in charge of whatever your wallet contains and the txs of your account

Your address is essentially a "human-readable" version of your public key









