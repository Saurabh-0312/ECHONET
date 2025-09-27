import React from 'react';

const dummyDevices = [
  {
    id: "SOUND-SENSOR-001",
    price: "0.5 ETH",
    owner: "0xB5f278f22c5E5C42174FC312cc593493d2f3570D",
    location: { name: "Golden Temple, Amritsar", lat: 31.6200, lng: 74.8765 }
  },
  {
    id: "SOUND-SENSOR-002",
    price: "120 USDC",
    owner: "0x1a2B3c4D5e6F7a8B9c0D1e2F3a4B5c6d7E8f9A0b",
    location: { name: "Jallianwala Bagh, Amritsar", lat: 31.6207, lng: 74.8801 }
  },
  {
    id: "SOUND-SENSOR-003",
    price: "0.75 ETH",
    owner: "0xFfEeDdCcBbAa99887766554433221100abCdeFfF",
    location: { name: "Wagah Border, Amritsar", lat: 31.6050, lng: 74.5753 }
  }
];

const DeviceCard = ({ device }) => (
  <div className="border border-gray-200 rounded-xl p-6 hover:shadow-2xl hover:scale-105 transition-all duration-300 bg-white">
    <div className="flex justify-between items-start">
      <h3 className="text-2xl font-bold text-gray-800 mb-4">{device.id}</h3>
      <span className="bg-blue-100 text-blue-800 font-bold text-lg px-4 py-1 rounded-full">{device.price}</span>
    </div>
    <div className="space-y-3 text-gray-600">
      <p className="flex items-center"><i className="fas fa-user-circle w-6 text-gray-400"></i><span className="font-mono text-sm break-all">{device.owner}</span></p>
      <p className="flex items-center"><i className="fas fa-map-marker-alt w-6 text-gray-400"></i><span>{device.location.name}</span></p>
      <p className="flex items-center text-sm"><i className="fas fa-compass w-6 text-gray-400"></i><span>Lat: {device.location.lat}, Lng: {device.location.lng}</span></p>
    </div>
    <button className="w-full mt-6 bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 transition-colors">
      Purchase
    </button>
  </div>
);

const DeviceList = () => {
  return (
    <div>
      <h2 className="text-3xl font-semibold text-gray-700 mb-6">Available Devices for Purchase</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {dummyDevices.map(device => (
          <DeviceCard key={device.id} device={device} />
        ))}
      </div>
    </div>
  );
};

export default DeviceList;