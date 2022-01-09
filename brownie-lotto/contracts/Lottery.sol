// SPDX-License-Identifier: Unlicense
pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is Ownable, VRFConsumerBase {
  // in tut: address payable[] public players; | but don't need to declare address payable in solidity 8
  address payable[] public players;
  address payable public recentWinner;
  uint256 public recentRandomness;
  uint256 public usdEntryFee;
  AggregatorV3Interface internal ethUsdPriceFeed;
  enum LOTTERY_STATE {
    OPEN,
    CLOSED,
    CALCULATING_WINNER
  }
  LOTTERY_STATE public lotteryState;
  uint256 public fee; // link VRF fee
  bytes32 public keyhash;
  event RequestedRandomness(bytes32 requestId);

  constructor(address _priceFeedAddress, address _vrfCoordinator, address linkToken, uint256 _fee, bytes32 _keyhash) public VRFConsumerBase(
    _vrfCoordinator, // vrfcoord addr
    linkToken // link tkn
  ) {
    usdEntryFee = 50 * (10 ** 18); // 50 usd in gwei
    ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
    lotteryState = LOTTERY_STATE.CLOSED;
    fee = _fee;
    keyhash = _keyhash;
  }

  function getNumPlayers() public view returns (uint256) {
    return players.length;
  }

  function enter() public payable {
    require(lotteryState == LOTTERY_STATE.OPEN);
    // $50 minimum
    require(msg.value >= getEntranceFee(), "Not enough ETH!");
    players.push(msg.sender);
  }

  function startLottery() public onlyOwner {
    require(lotteryState == LOTTERY_STATE.CLOSED, "Can't start a new lottery yet!");
    lotteryState = LOTTERY_STATE.OPEN;
  }

  function getEntranceFee() public view returns (uint256) {
    // use chainlink eth price feed * $50USD/gwei to calculate entrance fee
    (
      uint80 roundID, 
      int price,
      uint startedAt,
      uint timeStamp,
      uint80 answeredInRound
    ) = ethUsdPriceFeed.latestRoundData();

    // $50 / $2,000 / ETH (BUT solidity can't do decimals)
    // 50 * 100000 / 2000 (so do 50 * big number, then divide by eth price)
    uint256 base18Price = uint256(price) * 10 ** 10; // non-eth pairs have 8 decimals. https://coinmarketcap.com/currencies/octopus-network/ eth pairs (e.g x/eth) have 18 decimals
    uint256 costToEnter = (usdEntryFee * 10 ** 18) / base18Price; // prob use safemath .div()
    return costToEnter;

  }

  function endLottery() public onlyOwner {
    lotteryState = LOTTERY_STATE.CALCULATING_WINNER;
    // blockchain RNG is a big problem. need oracle (chainlink VRF) for truest source of randomness
    // could get some stuff that seems random & hash it, but this is insecure
    // Chainlink VRF follows request & receive pattern:
    // 1st request in one transaction. 2nd transaction chainlink does calculation and returns value
    bytes32 requestId = requestRandomness(keyhash, fee);

    // Emit event
    emit RequestedRandomness(requestId);

    // now, wait for the chainlink node to give us back the num
  }

  // internal so only VRFCoordinator can call it
  // override because VRFCoordinator defines this as virtual. just to show you it's on the interface, you need to implement it yourself
  function fulfillRandomness(bytes32 requestId, uint256 _randomness) internal override {
    require(lotteryState == LOTTERY_STATE.CALCULATING_WINNER, "Still calculating winner");
    require(_randomness > 0, "random-not-found");

    recentWinner = players[_randomness % players.length];
    recentWinner.transfer(address(this).balance);

    // Reset
    players = new address payable[](0); // array of size 0
    lotteryState = LOTTERY_STATE.CLOSED;
    recentRandomness = _randomness;
  }
}

