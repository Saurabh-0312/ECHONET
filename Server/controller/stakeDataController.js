import dotenv from 'dotenv';
dotenv.config();

import { gql, request } from 'graphql-request';

const apiKey = "20182ea32cbdba66ea1592d3a499b4b5";
const url = "https://api.studio.thegraph.com/query/120234/polygon-contract/version/latest";
const headers = { Authorization: `Bearer ${apiKey}` };

const getStakeData = async (req, res) => {
    try {
        const walletAddress = req.body.walletAddress;
        // Dynamically build the query with the provided wallet address
        const dynamicQuery = gql`
          {
            sensorRegistereds(first: 10, where: { owner: "${walletAddress}" }, orderBy: blockTimestamp, orderDirection: desc) {
              id
              owner
              deviceId
              stakeAmount
              blockNumber
              blockTimestamp
              transactionHash
            }
          }
        `;
        const data = await request(url, dynamicQuery, {}, headers);
        // console.log("Fetched data from The Graph:", data);
        
        res.status(200).json({success:true,data});
    } catch (error) {
        console.error('Error fetching data from The Graph:', error);
        res.status(500).json({success:false, message: 'Failed to fetch subgraph data' });
    }
}

export { getStakeData };
