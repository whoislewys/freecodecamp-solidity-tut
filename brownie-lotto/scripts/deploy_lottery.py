from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery, network, config
import time

def deploy_lottery():
  account = get_account()

  lottery = Lottery.deploy(
      get_contract("eth_usd_price_feed").address, # if testnet & no mock deployed, will deploy mock price feed for us. however if on real network, will grab deployed address of contract on the testnet and deploy mock contract using the real address, but mock abi and name
      get_contract("vrf_coordinator").address,
      get_contract("link_token").address,
      config["networks"][network.show_active()]["fee"],
      config["networks"][network.show_active()]["keyhash"],
      {"from": account},
      publish_source=config["networks"][network.show_active()].get("verify", False), # verify with etherscan. if no verify key, default to false 
      )
  print('deployed ltotery@!!! 8==D')
  return lottery

def start_lottery():
  account = get_account()
  lottery = Lottery[-1]
  start_tx = lottery.startLottery({'from': account})
  start_tx.wait(1)
  print('The lottery is started!')


def enter_lottery():
  account = get_account()
  lottery = Lottery[-1]
  value = lottery.getEntranceFee() + 10000000
  tx = lottery.enter({'from': account, 'value': value})
  tx.wait(1)
  print('You entered the lottery with account: ', account)


def end_lottery():
  account = get_account()
  lottery = Lottery[-1]

  # fund the contract with link, because endlotto needs vrf from chainlink
  tx = fund_with_link(lottery.address)
  tx.wait(1)

  endtx = lottery.endLottery({'from': account})
  endtx.wait(1)
  # remember end lotto will call chainlink node, chainlink node will call our fulfill randomness node asynchronously
  # need to wait for that call to finish
  time.sleep(60)
  # but wait, locally there's ackshually no chainlink node to respond to requestRandomness call and call our fulfillRandomness func
  # there is a workaround for local dev coming...
  # for now, let's write some unit tests
  print('lottery recent winner: ', lottery.recentWinner())

  

def main():
  deploy_lottery()
  start_lottery()
  enter_lottery()
  end_lottery()
