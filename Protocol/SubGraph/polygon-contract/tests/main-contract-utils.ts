import { newMockEvent } from "matchstick-as"
import { ethereum, Address, BigInt } from "@graphprotocol/graph-ts"
import {
  ReadingSubmitted,
  RewardMinted,
  SensorDeregistered,
  SensorRegistered,
  StakeSlashed
} from "../generated/MainContract/MainContract"

export function createReadingSubmittedEvent(
  owner: Address,
  ipfsCID: string,
  rewardAmount: BigInt
): ReadingSubmitted {
  let readingSubmittedEvent = changetype<ReadingSubmitted>(newMockEvent())

  readingSubmittedEvent.parameters = new Array()

  readingSubmittedEvent.parameters.push(
    new ethereum.EventParam("owner", ethereum.Value.fromAddress(owner))
  )
  readingSubmittedEvent.parameters.push(
    new ethereum.EventParam("ipfsCID", ethereum.Value.fromString(ipfsCID))
  )
  readingSubmittedEvent.parameters.push(
    new ethereum.EventParam(
      "rewardAmount",
      ethereum.Value.fromUnsignedBigInt(rewardAmount)
    )
  )

  return readingSubmittedEvent
}

export function createRewardMintedEvent(
  to: Address,
  amount: BigInt
): RewardMinted {
  let rewardMintedEvent = changetype<RewardMinted>(newMockEvent())

  rewardMintedEvent.parameters = new Array()

  rewardMintedEvent.parameters.push(
    new ethereum.EventParam("to", ethereum.Value.fromAddress(to))
  )
  rewardMintedEvent.parameters.push(
    new ethereum.EventParam("amount", ethereum.Value.fromUnsignedBigInt(amount))
  )

  return rewardMintedEvent
}

export function createSensorDeregisteredEvent(
  owner: Address
): SensorDeregistered {
  let sensorDeregisteredEvent = changetype<SensorDeregistered>(newMockEvent())

  sensorDeregisteredEvent.parameters = new Array()

  sensorDeregisteredEvent.parameters.push(
    new ethereum.EventParam("owner", ethereum.Value.fromAddress(owner))
  )

  return sensorDeregisteredEvent
}

export function createSensorRegisteredEvent(
  owner: Address,
  deviceId: string,
  stakeAmount: BigInt
): SensorRegistered {
  let sensorRegisteredEvent = changetype<SensorRegistered>(newMockEvent())

  sensorRegisteredEvent.parameters = new Array()

  sensorRegisteredEvent.parameters.push(
    new ethereum.EventParam("owner", ethereum.Value.fromAddress(owner))
  )
  sensorRegisteredEvent.parameters.push(
    new ethereum.EventParam("deviceId", ethereum.Value.fromString(deviceId))
  )
  sensorRegisteredEvent.parameters.push(
    new ethereum.EventParam(
      "stakeAmount",
      ethereum.Value.fromUnsignedBigInt(stakeAmount)
    )
  )

  return sensorRegisteredEvent
}

export function createStakeSlashedEvent(
  sensorAddress: Address,
  userStake: BigInt
): StakeSlashed {
  let stakeSlashedEvent = changetype<StakeSlashed>(newMockEvent())

  stakeSlashedEvent.parameters = new Array()

  stakeSlashedEvent.parameters.push(
    new ethereum.EventParam(
      "sensorAddress",
      ethereum.Value.fromAddress(sensorAddress)
    )
  )
  stakeSlashedEvent.parameters.push(
    new ethereum.EventParam(
      "userStake",
      ethereum.Value.fromUnsignedBigInt(userStake)
    )
  )

  return stakeSlashedEvent
}
