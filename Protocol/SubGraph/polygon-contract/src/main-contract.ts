import {
  ReadingSubmitted as ReadingSubmittedEvent,
  RewardMinted as RewardMintedEvent,
  SensorDeregistered as SensorDeregisteredEvent,
  SensorRegistered as SensorRegisteredEvent,
  StakeSlashed as StakeSlashedEvent
} from "../generated/MainContract/MainContract"
import {
  ReadingSubmitted,
  RewardMinted,
  SensorDeregistered,
  SensorRegistered,
  StakeSlashed
} from "../generated/schema"

export function handleReadingSubmitted(event: ReadingSubmittedEvent): void {
  let entity = new ReadingSubmitted(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.owner = event.params.owner
  entity.ipfsCID = event.params.ipfsCID
  entity.rewardAmount = event.params.rewardAmount

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleRewardMinted(event: RewardMintedEvent): void {
  let entity = new RewardMinted(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.to = event.params.to
  entity.amount = event.params.amount

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleSensorDeregistered(event: SensorDeregisteredEvent): void {
  let entity = new SensorDeregistered(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.owner = event.params.owner

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleSensorRegistered(event: SensorRegisteredEvent): void {
  let entity = new SensorRegistered(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.owner = event.params.owner
  entity.deviceId = event.params.deviceId
  entity.stakeAmount = event.params.stakeAmount

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleStakeSlashed(event: StakeSlashedEvent): void {
  let entity = new StakeSlashed(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.sensorAddress = event.params.sensorAddress
  entity.userStake = event.params.userStake

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}
