require("dotenv").config();
const { ethers } = require("hardhat");
const { hethers } = require("@hashgraph/hethers");

async function main() {
  const name = process.env.TOKEN_NAME || "EchoNetToken";
  const symbol = process.env.TOKEN_SYMBOL || "ECH";

  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);

  const Token = await ethers.getContractFactory("EchoNetToken");
  const token = await Token.deploy(name, symbol);
  await token.deployed();

  console.log("EchoNetToken deployed to:", token.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
