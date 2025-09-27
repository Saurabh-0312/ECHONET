import fs from "fs";
import path from "path";
import "dotenv/config";

const SENSORS_FILE = path.resolve(path.dirname(new URL(import.meta.url).pathname), "registered-sensors.json");
let registeredSensors = [];
try {
  if (fs.existsSync(SENSORS_FILE)) {
    const data = fs.readFileSync(SENSORS_FILE, "utf8");
    registeredSensors = JSON.parse(data);
  }
} catch (error) {
  console.log("Starting with empty sensor list");
}

function saveSensors() {
  try {
    fs.writeFileSync(SENSORS_FILE, JSON.stringify(registeredSensors, null, 2));
  } catch (error) {
    console.error("Failed to save sensors:", error);
  }
}

async function getHypergraphLibs() {
  const { Graph, Ipfs, ContentIds } = await import("@graphprotocol/grc-20");
  const { Wallet, JsonRpcProvider } = await import("ethers");
  return { Graph, Ipfs, ContentIds, Wallet, JsonRpcProvider };
}

async function registerToHypergraph(sensorData) {
  try {
    const { Graph, Ipfs, ContentIds, Wallet, JsonRpcProvider } = await getHypergraphLibs();
    const privateKey = process.env.YOUR_PRIVATE_KEY;
    if (!privateKey) throw new Error("PRIVATE_KEY not found in environment variables");

    const rpcUrl = process.env.POLYGON_AMOY_RPC_URL || "https://rpc-amoy.polygon.technology";
    const provider = new JsonRpcProvider(rpcUrl);
    const wallet = new Wallet(privateKey, provider);

    const createStringProperty = (name, description) => Graph.createProperty({ name, description, dataType: "STRING" });
    const createNumberProperty = (name, description) => Graph.createProperty({ name, description, dataType: "NUMBER" });

    const props = {
      dataType: createStringProperty("Data Type", "The type of data collected by the sensor"),
      status: createStringProperty("Status", "The operational status of the sensor"),
      project: createStringProperty("Project", "The DePIN project this sensor belongs to"),
      locality: createStringProperty("Locality", "The specific locality within the city"),
      latitude: createNumberProperty("Latitude", "GPS latitude coordinate"),
      longitude: createNumberProperty("Longitude", "GPS longitude coordinate"),
      owner: createStringProperty("Owner Address", "Ethereum address of the sensor owner"),
      deviceId: createStringProperty("Device ID", "Unique identifier for the device")
    };

    const entityResult = Graph.createEntity({
      name: sensorData.name,
      description: sensorData.description,
      values: [
        { property: ContentIds.LOCATION_PROPERTY, value: sensorData.location },
        { property: props.locality.id, value: sensorData.locality },
        { property: props.latitude.id, value: sensorData.latitude.toString() },
        { property: props.longitude.id, value: sensorData.longitude.toString() },
        { property: props.dataType.id, value: sensorData.dataType },
        { property: props.status.id, value: sensorData.status },
        { property: props.project.id, value: sensorData.project },
        { property: props.owner.id, value: sensorData.ownerAddress },
        { property: props.deviceId.id, value: sensorData.deviceId }
      ],
    });

    const allOps = [].concat(...Object.values(props).map(p => p.ops), entityResult.ops);

    const publicationResult = await Ipfs.publishEdit({
      name: `Dynamic Registration: ${sensorData.name}`,
      ops: allOps, author: wallet.address, network: "TESTNET"
    });

    console.log("Published to Hypergraph:", publicationResult);

    return {
      success: true, entityId: entityResult.id,
      cid: publicationResult.cid, editId: publicationResult.editId
    };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

const registerSensor = async (req, res) => {
  try {
    const {
      deviceId, name, type, location, locality, latitude, longitude,
      dataType, project, ownerAddress, description
    } = req.body;

    console.log("hyperGraphDevice registerSensor called with:", req.body);
    

    if (!deviceId || !type || !location || !locality || latitude === undefined || longitude === undefined || !dataType || !project || !ownerAddress) {
      return res.status(400).json({ success: false, error: "Missing required fields" });
    }

    console.log("All required fields are present.");
    

    if (!/^0x[a-fA-F0-9]{40}$/.test(ownerAddress)) {
      return res.status(400).json({ success: false, error: "Invalid Ethereum address format" });
    }

    console.log("Owner address format is valid.");
    

    if (registeredSensors.find((s) => s.id === deviceId)) {
      return res.status(400).json({ success: false, error: "Device ID already exists." });
    }

    console.log("Device ID is unique.");
    

    console.log("Validated input data, proceeding to register sensor.");

    const sensorData = {
      id: deviceId, deviceId, 
      name: name || deviceId, 
      type, location, locality,
      latitude, 
      longitude, 
      dataType, 
      project, 
      ownerAddress,
      description: description || `${dataType} sensor monitoring in ${locality}, ${location}`,
      timestamp: new Date().toISOString(), status: "active",
    };

    console.log("Registering sensor:", sensorData);

    let hypergraphResult = { success: false };
    if (process.env.YOUR_PRIVATE_KEY) {
      hypergraphResult = await registerToHypergraph(sensorData);
    } else {
      hypergraphResult = {
        success: true, entityId: `demo-entity-${Date.now()}`,
        cid: `demo-cid-${Date.now()}`, editId: `demo-edit-${Date.now()}`
      };
    }
    console.log('registerToHypergraph result:', hypergraphResult);

    if (hypergraphResult.success) {
      sensorData.hypergraphEntityId = hypergraphResult.entityId;
      sensorData.hypergraphCID = hypergraphResult.cid;
      sensorData.hypergraphEditId = hypergraphResult.editId;

      registeredSensors.push(sensorData);
      saveSensors();

      res.status(201).json({ success: true, sensor: sensorData, message: "Sensor registered successfully!" });
    } else {
      res.status(500).json({ success: false, error: hypergraphResult.error || "Failed to register to Hypergraph" });
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
};

const getAllSensors = (req, res) => {
  const { location, type } = req.query;
  let filteredSensors = [...registeredSensors];

  if (location) {
    filteredSensors = filteredSensors.filter((sensor) =>
      sensor.location.toLowerCase().includes(location.toLowerCase())
    );
  }

  if (type && type !== "all") {
    filteredSensors = filteredSensors.filter((sensor) =>
      sensor.type.toLowerCase().includes(type.toLowerCase())
    );
  }

  res.json({
    success: true, sensors: filteredSensors,
    total: registeredSensors.length, filtered: filteredSensors.length
  });
};

const getSensorById = (req, res) => {
  const sensor = registeredSensors.find((s) => s.id === req.params.id);
  if (sensor) {
    res.json({ success: true, sensor });
  } else {
    res.status(404).json({ success: false, error: "Sensor not found" });
  }
};

const deleteSensor = async (req, res) => {
  try {
    const sensorId = req.params.id;
    const index = registeredSensors.findIndex((s) => s.id === sensorId);

    if (index === -1) {
      return res.status(404).json({ success: false, error: "Sensor not found" });
    }

    const sensorToDelete = registeredSensors[index];
    registeredSensors.splice(index, 1);
    saveSensors();

    res.json({
      success: true, message: "Sensor deleted successfully",
      deletedSensor: { id: sensorToDelete.id, name: sensorToDelete.name }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
};

export {
  registerSensor,
  getAllSensors,
  getSensorById,
  deleteSensor,
};