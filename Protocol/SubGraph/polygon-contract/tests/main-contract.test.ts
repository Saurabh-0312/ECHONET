import {
  assert,
  describe,
  test,
  clearStore,
  beforeAll,
  afterAll
} from "matchstick-as/assembly/index"
import { Address, BigInt } from "@graphprotocol/graph-ts"
import { ReadingSubmitted } from "../generated/schema"
import { ReadingSubmitted as ReadingSubmittedEvent } from "../generated/MainContract/MainContract"
import { handleReadingSubmitted } from "../src/main-contract"
import { createReadingSubmittedEvent } from "./main-contract-utils"

// Tests structure (matchstick-as >=0.5.0)
// https://thegraph.com/docs/en/subgraphs/developing/creating/unit-testing-framework/#tests-structure

describe("Describe entity assertions", () => {
  beforeAll(() => {
    let owner = Address.fromString("0x0000000000000000000000000000000000000001")
    let ipfsCID = "Example string value"
    let rewardAmount = BigInt.fromI32(234)
    let newReadingSubmittedEvent = createReadingSubmittedEvent(
      owner,
      ipfsCID,
      rewardAmount
    )
    handleReadingSubmitted(newReadingSubmittedEvent)
  })

  afterAll(() => {
    clearStore()
  })

  // For more test scenarios, see:
  // https://thegraph.com/docs/en/subgraphs/developing/creating/unit-testing-framework/#write-a-unit-test

  test("ReadingSubmitted created and stored", () => {
    assert.entityCount("ReadingSubmitted", 1)

    // 0xa16081f360e3847006db660bae1c6d1b2e17ec2a is the default address used in newMockEvent() function
    assert.fieldEquals(
      "ReadingSubmitted",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "owner",
      "0x0000000000000000000000000000000000000001"
    )
    assert.fieldEquals(
      "ReadingSubmitted",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "ipfsCID",
      "Example string value"
    )
    assert.fieldEquals(
      "ReadingSubmitted",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "rewardAmount",
      "234"
    )

    // More assert options:
    // https://thegraph.com/docs/en/subgraphs/developing/creating/unit-testing-framework/#asserts
  })
})
