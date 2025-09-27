import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import Header from "../components/hyperGraph/Header.jsx";
import Stats from "../components/hyperGraph/Stats";
import RegistrationForm from "../components/hyperGraph/RegistrationForm";
import Discovery from "../components/hyperGraph/Discovery";
import LiveFeed from "../components/hyperGraph/LiveFeed";
import SuccessModal from "../components/hyperGraph/SuccessModal";

const API_URL = "http://localhost:3001/api/hypergraph";

function App() {
  const [stats, setStats] = useState({
    totalSensors: 0,
    totalProjects: 0,
    activeLocations: 0,
  });
  const [liveFeedSensors, setLiveFeedSensors] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMessage, setModalMessage] = useState("");
  const [discoveryResults, setDiscoveryResults] = useState(null);

  const fetchSensors = useCallback(async () => {
    try {
      const response = await axios.get(API_URL);
      if (response.data.success) {
        const sensors = response.data.sensors;
        setStats({
          totalSensors: sensors.length,
          totalProjects: new Set(sensors.map((s) => s.project)).size,
          activeLocations: new Set(sensors.map((s) => s.location)).size,
        });
        setLiveFeedSensors(sensors.slice(0, 6));
      }
    } catch (error) {
      console.error("Failed to fetch sensors:", error);
    }
  }, []);

  useEffect(() => {
    fetchSensors();
    const interval = setInterval(fetchSensors, 30000);
    return () => clearInterval(interval);
  }, [fetchSensors]);

  const handleRegister = async (deviceData) => {
    try {
      // Map frontend fields to backend expected fields
      const mappedData = {
        deviceId: deviceData.deviceId,
        type: deviceData.deviceType,
        location: deviceData.deviceLocation,
        locality: deviceData.locality,
        latitude: deviceData.latitude,
        longitude: deviceData.longitude,
        dataType: deviceData.dataType,
        project: deviceData.projectName,
        ownerAddress: deviceData.ownerAddress,
      };
      console.log("Registering device data:", mappedData);
      const response = await axios.post(API_URL, mappedData);
      if (response.data.success) {
        setModalMessage(
          `${response.data.sensor.name} has been registered and is now discoverable!`
        );
        setIsModalOpen(true);
        fetchSensors();
        return true;
      }
    } catch (error) {
      alert(`Registration failed: ${error.response?.data?.error || error.message}`);
      return false;
    }
  };

  const handleSearch = async (location, type) => {
    try {
        const response = await axios.get(`${API_URL}?location=${location}&type=${type}`);
        if(response.data.success) {
            setDiscoveryResults(response.data.sensors);
        }
    } catch (error) {
        alert(`Search failed: ${error.message}`);
    }
  };

  const handleDelete = async (sensorId, sensorName) => {
    if (!window.confirm(`Are you sure you want to delete "${sensorName}"?`)) {
      return;
    }
    try {
      console.log(`Deleting sensor with ID: ${sensorId}`);
      console.log("API URL:", `${API_URL}/${sensorId}`);
      
      const response = await axios.delete(`${API_URL}/${sensorId}`);
      if (response.data.success) {
        alert(`Successfully deleted "${sensorName}"!`);
        fetchSensors();
        if (discoveryResults) {
            setDiscoveryResults(prevResults => prevResults.filter(s => s.id !== sensorId));
        }
      }
    } catch (error) {
      alert(`Failed to delete sensor: ${error.message}`);
    }
  };

  return (
    <div className="bg-gray-50 min-h-screen">
      <Header />
      <main className="container mx-auto px-4 py-8 max-h-[90vh] overflow-y-auto">
        <Stats stats={stats} />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
          <RegistrationForm onRegister={handleRegister} />
          <Discovery onSearch={handleSearch} results={discoveryResults} onDelete={handleDelete} />
        </div>
        <LiveFeed sensors={liveFeedSensors} onDelete={handleDelete} />
      </main>
      <SuccessModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        message={modalMessage}
      />
    </div>
  );
}

export default App;