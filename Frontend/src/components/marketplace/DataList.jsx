import React from 'react';
import decibelData from '../../DummyData/decibelData.json';

const DataCard = ({ dataPoint }) => (
  <div className="border border-gray-200 rounded-xl p-6 hover:shadow-xl hover:border-indigo-300 transition-all duration-300 bg-gray-50">
    <div className="flex justify-between items-start mb-3">
        <span className="bg-indigo-100 text-indigo-800 text-xs font-semibold px-3 py-1 rounded-full">{dataPoint.deviceId}</span>
        <span className="text-gray-500 text-sm">{new Date(dataPoint.timeline).toLocaleString()}</span>
    </div>
    <div className="text-center my-4">
        <p className="text-5xl font-bold text-indigo-600">{dataPoint.data.decibel} <span className="text-2xl text-gray-500">dB</span></p>
        <p className="text-sm text-gray-400">Decibel Level</p>
    </div>
    <div className="text-gray-600 mt-4 border-t pt-3">
       <p className="flex items-center text-sm"><i className="fas fa-user-circle w-6 text-gray-400"></i><span className="font-mono text-xs break-all">{dataPoint.owner}</span></p>
    </div>
     <button className="w-full mt-4 bg-indigo-600 text-white font-bold py-2 rounded-lg hover:bg-indigo-700 transition-colors">
      Buy Data
    </button>
  </div>
);

const DataList = () => {
  return (
    <div>
      <h2 className="text-3xl font-semibold text-gray-700 mb-6">Available Data Streams</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {decibelData.map(item => (
          <DataCard key={item.id} dataPoint={item} />
        ))}
      </div>
    </div>
  );
};

export default DataList;