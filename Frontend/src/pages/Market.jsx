import React, { useState } from 'react';
import DeviceList from '../components/marketplace/DeviceList.jsx';
import DataList from '../components/marketplace/DataList.jsx';

const Market = () => {
  const [activeTab, setActiveTab] = useState('devices');

  const tabStyle = "px-6 py-2 text-lg font-semibold rounded-t-lg transition-colors duration-300";
  const activeTabStyle = "bg-white text-blue-600 shadow-md";
  const inactiveTabStyle = "bg-blue-500 text-white hover:bg-blue-600";

  return (
    <div className="bg-gray-100 min-h-screen p-4 sm:p-8">
      <div className="container mx-auto">
        <h1 className="text-4xl font-bold text-gray-800 text-center mb-8">DePIN Marketplace</h1>
        
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('devices')}
            className={`${tabStyle} ${activeTab === 'devices' ? activeTabStyle : inactiveTabStyle}`}
          >
            <i className="fas fa-satellite-dish mr-2"></i>Devices
          </button>
          <button
            onClick={() => setActiveTab('data')}
            className={`${tabStyle} ${activeTab === 'data' ? activeTabStyle : inactiveTabStyle}`}
          >
            <i className="fas fa-chart-line mr-2"></i>Data Streams
          </button>
        </div>

        <div className="bg-white p-4 sm:p-8 rounded-b-lg rounded-r-lg shadow-lg">
          {activeTab === 'devices' && <DeviceList />}
          {activeTab === 'data' && <DataList />}
        </div>
      </div>
    </div>
  );
};

export default Market;