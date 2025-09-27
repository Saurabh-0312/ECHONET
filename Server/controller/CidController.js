import { gql, request } from 'graphql-request';

const apiKey = "20182ea32cbdba66ea1592d3a499b4b5";
const url = "https://api.studio.thegraph.com/query/120234/main-contract/version/latest";
const headers = { Authorization: `Bearer ${apiKey}` };

const getCidData = async (req, res) => {
    try {
						const walletAddress = req.body.walletAddress;
                        // console.log("Received wallet address for CID fetch:", walletAddress);
                        
						const query = gql`
							{
								readingSubmitteds(
									first: 1
									orderBy: blockTimestamp
									orderDirection: desc
									where: { owner: "${walletAddress}" }
								) {
									id
									owner
									ipfsCID
									rewardAmount
									blockNumber
									blockTimestamp
								}
							}
						`;
        const data = await request(url, query, {}, headers);
        console.log("Fetched CID data from The Graph:", data);
        res.status(200).json({ success: true, data });
    } catch (error) {
        console.error('Error fetching CID data from The Graph:', error);
        res.status(500).json({ success: false, message: 'Failed to fetch subgraph data' });
    }
};

export { getCidData };