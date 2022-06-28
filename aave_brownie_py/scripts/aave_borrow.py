from brownie import network, config, interface, Contract
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3

REPAY_MODE = 2 # 1 stable, 2 variable

def main():
  account = get_account()
  weth_address = config['networks'][network.show_active()]['weth_token']

  if network.show_active() in ['mainnet-fork']:
    # get weth if no weth (local env)
    # make sure you got weth in your respective testnet if running in testnet
    get_weth()

  # how to lend? look docs....
  # https://docs.aave.com/developers/the-core-protocol/protocol-overview

  # lendingp ool contract
  # u know the drill... get ABI, Address
  lending_pool = get_lending_pool()
  print('got lending pool :', lending_pool)

  # now let's lend
  # 1. Approve
  # ERC20 tokens have an approve function to make sure contracts can't spend our tokens without our approval
  amt = 0.05 * 10 ** 18
  approve_erc20(amt, lending_pool.address, weth_address, account)
  print('Depositing...')
  # function deposit(
  #   address asset,
  #   uint256 amount,
  #   address onBehalfOf,
  #   uint16 referralCode
  # ) external;
  tx = lending_pool.deposit(weth_address, amt, account.address, 0, {'from': account})
  tx.wait(1)
  print('deposited!')


  available_borrow_eth, total_debt_eth = get_borrowable_data(lending_pool, account)
  print()
  print('Borrowing...')

  # Need DAI/ETH price feed to know how much we can borrow
  dai_eth_price_feed = config['networks'][network.show_active()]['dai_eth_price_feed']
  dai_eth_price = get_asset_price(dai_eth_price_feed)

  # convert borrowable eth -> borrowable dai * some % (to makes sure health factor > 1)
  amount_dai_to_borrow = (1 / dai_eth_price) * (available_borrow_eth * 0.8)
  amount_dai_to_borrow_wei = Web3.toWei((1 / dai_eth_price) * (available_borrow_eth * 0.8), 'ether')
  print(f'Borrowing {amount_dai_to_borrow} Dai')
  print(f'Borrowing {amount_dai_to_borrow_wei} Dai in wei')

  # Now lets borrowwww ooh im borooowing
  # For kovan, you may have to get testnet aave dai address using getReserveTokensAddresses or looking at their json file linked at the bottom here:
  # https://docs.aave.com/developers/deployed-contracts/deployed-contracts
  dai_address = config['networks'][network.show_active()]['dai_token']
  borrow_tx = lending_pool.borrow(
    dai_address,
    Web3.toWei(amount_dai_to_borrow, 'ether'),
    REPAY_MODE,
    0,
    account.address,
    {'from': account}
  )
  borrow_tx.wait(1)
  print('borrow complete!')
  available_borrow_eth, total_debt_eth = get_borrowable_data(lending_pool, account)

  print()
  # print('Repaying...')
  # print('Amount to repay in dai: ', amount_dai_to_borrow)
  # amount_to_repay = Web3.toWei(amount_dai_to_borrow, 'ether')
  # print('Amount to repay: ', amount_to_repay)
  # repay_all(amount_to_repay, lending_pool, account)
  # print('Just repayed! you\'re a god ready for flash loan haxxxx')
  # print()
  # get_borrowable_data(lending_pool, account)
  return


# function approve(address spender, uint value) external returns (bool);
def approve_erc20(amount, spender, erc20_address, account):
  # ABI
  # Address
  print('Approving ERC20 token')
  erc20 = interface.IERC20(erc20_address)
  tx = erc20.approve(spender, amount, {'from': account})
  tx.wait(1)
  print('Approved')
  return tx


def get_lending_pool():
  # aave has a contract that gives the addresses of their various lending pool contracts
  lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(config['networks'][network.show_active()]['lending_pool_addresses_provider'])

  # got lending pool addr...
  # now we need lending pool abi (can get from interface on aave github)
  lending_pool_address = lending_pool_addresses_provider.getLendingPool()
  lending_pool = interface.ILendingPool(lending_pool_address)
  return lending_pool


def get_borrowable_data(lending_pool, account):
  # api here: https://docs.aave.com/developers/the-core-protocol/lendingpool#getuseraccountdata
  (
      total_collateral_eth,
      total_debt_eth,
      available_borrow_eth,
      current_liq_threshold,
      ltv,
      health_factor
  ) = lending_pool.getUserAccountData(account.address)
  available_borrow_eth = Web3.fromWei(available_borrow_eth, 'ether')
  total_collateral_eth = Web3.fromWei(total_collateral_eth, 'ether')
  total_debt_eth = Web3.fromWei(total_debt_eth, 'ether')
  print(f'Available borrow: {available_borrow_eth} | Total collat: {total_collateral_eth} |  Total debt: {total_debt_eth}')
  return (float(available_borrow_eth), float(total_debt_eth))


def get_asset_price(price_feed_address):
  # abi , address
  dai_eth_price_feed = interface.IAggregatorV3(price_feed_address)
  latest_price = dai_eth_price_feed.latestRoundData()[1]
  print('dai/eth price: ', latest_price) # 309532395130763

  # 18 decimals | 0.000309532395130763
  base10_latest_price = Web3.fromWei(latest_price, 'ether')
  print('converted latest price: ', base10_latest_price) # 309532395130763

  return (float(base10_latest_price))


def repay_all(amount, lending_pool, account):
  dai_address = config['networks'][network.show_active()]['dai_token']
  approve_erc20(
    amount,
    lending_pool,
    dai_address,
    account
  )

  repay_tx = lending_pool.repay(dai_address,
    amount,
    REPAY_MODE,
    account.address,
    {'from': account}
  )
  repay_tx.wait(1)
  print('Repayed!')

