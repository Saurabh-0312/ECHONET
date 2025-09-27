import React from "react";
// Corrected imports: Removed 'SiUsdcoin' and added 'FaDollarSign'
import { FaEthereum, FaDollarSign } from "react-icons/fa";
import { FaUserAstronaut, FaMapMarkedAlt, FaSatelliteDish } from "react-icons/fa";

const dummyDevices = [
  {
    id: "SOUND-SENSOR-001",
    price: "0.5 ETH",
    owner: "0xB5f278f22c5E5C42174FC312cc593493d2f3570D",
    location: { name: "Golden Temple, Amritsar", lat: 31.62, lng: 74.8765 },
  },
  {
    id: "SOUND-SENSOR-002",
    price: "120 USDC",
    owner: "0x1a2B3c4D5e6F7a8B9c0D1e2F3a4B5c6d7E8f9A0b",
    location: { name: "Jallianwala Bagh, Amritsar", lat: 31.6207, lng: 74.8801 },
  },
  {
    id: "SOUND-SENSOR-003",
    price: "0.75 ETH",
    owner: "0xFfEeDdCcBbAa99887766554433221100abCdeFfF",
    location: { name: "Wagah Border, Amritsar", lat: 31.605, lng: 74.5753 },
  },
   {
    id: "AIR-QUALITY-017",
    price: "250 USDC",
    owner: "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
    location: { name: "India Gate, New Delhi", lat: 28.6129, lng: 77.2295 },
  },
];


const PriceDisplay = ({ price }) => {
  const isEth = price.includes("ETH");
  const isUsdc = price.includes("USDC");
  
  // Use the corrected icon for USDC
  const icon = isEth ? <FaEthereum /> : isUsdc ? <FaDollarSign /> : null;
  const gradient = isEth 
    ? "from-purple-500 to-indigo-500" 
    : "from-blue-500 to-cyan-500";

  return (
    <div className={`flex items-center gap-2 text-lg font-bold text-white px-4 py-2 rounded-full bg-gradient-to-r ${gradient} shadow-lg`}>
      {icon}
      <span>{price}</span>
    </div>
  );
};


const DeviceCard = ({ device }) => (
  <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 transition-all duration-300 group hover:border-violet-500 hover:shadow-2xl hover:shadow-violet-500/20">
    <div className="flex justify-between items-center mb-5">
      <div className="flex items-center gap-3">
        <FaSatelliteDish className="text-violet-400 text-xl" />
        <h3 className="text-lg font-bold text-white tracking-wider">{device.id}</h3>
      </div>
      <PriceDisplay price={device.price} />
    </div>

    <div className="space-y-4 my-6 text-gray-300">
      <div className="flex items-center gap-3">
        <FaUserAstronaut className="text-cyan-400 text-lg w-5 text-center" />
        <p className="font-mono text-xs break-all text-cyan-200">{device.owner}</p>
      </div>
      <div className="flex items-center gap-3">
        <FaMapMarkedAlt className="text-pink-400 text-lg w-5 text-center" />
        <div>
          <p className="font-semibold text-pink-200">{device.location.name}</p>
          <p className="text-xs text-gray-400">Lat: {device.location.lat}, Lng: {device.location.lng}</p>
        </div>
      </div>
    </div>
    
    <div className="border-t border-gray-700 my-4"></div>

    <button className="w-full mt-4 bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-bold py-3 rounded-xl hover:from-violet-500 hover:to-indigo-500 transition-all duration-300 transform hover:scale-105 shadow-lg">
      Purchase Device
    </button>
  </div>
);

const DeviceList = () => (
  <div className="w-full">
    <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-cyan-400 mb-10 text-center">
      DePIN Device Marketplace
    </h2>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
      {dummyDevices.map((device) => (
        <DeviceCard key={device.id} device={device} />
      ))}
    </div>
  </div>
);

export default DeviceList;