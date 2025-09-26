import { http } from "viem";
import { mainnet } from "viem/chains";
import { createEnsPublicClient } from "@ensdomains/ensjs";

const client = createEnsPublicClient({
    chain: mainnet,
    transport: http(),
});

const nameToAddress = async (req,res) => {
    try {
        const ensname = req.body.ensname;
        if (!ensname) {
            return res.status(400).json({ error: "ENS name required" });
        }

        const ethAddress = await client.getAddressRecord({ name: ensname });
        if (!ethAddress) {
            return res.status(404).json({ error: "ENS name not found" });
        }

        res.status(200).json(ethAddress);
    } catch (error) {
        console.error("Error resolving ENS:", error);
        res.status(500).json({ error: "Internal server error" });
    }
}

const addressToName = async (req,res) => {
    try {
        const address = req.body.address;
        if (!address) {
            return res.status(204).json({ error: "Ethereum address required" });
        }

        // console.log("Performing reverse ENS lookup for address:", address);

        const ensName = await client.getName({ address });

        if (!ensName || !ensName.name) {
            return res.status(204).json({success:false, error: "No ENS name set for this address" });
        }

        // Optional forward verification: check if name resolves back to same address
        // const checkAddr = await client.getAddressRecord({ name: ensName.name });
        // if (!checkAddr || checkAddr.address.toLowerCase() !== address.toLowerCase()) {
        //   return res.status(400).json({ error: "ENS reverse record does not match forward resolution" });
        // }

        res.status(200).json({success:true, ensName: ensName.name });
    } catch (error) {
        console.error("Error in reverse ENS lookup:", error);
        res.status(500).json({success:false, error: "Internal server error" });
    }
}

export { nameToAddress, addressToName };