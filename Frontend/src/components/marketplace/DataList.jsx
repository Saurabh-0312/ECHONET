import React from "react";
import decibelData from "../../DummyData/decibelData.json";
import { BsSoundwave } from "react-icons/bs";
import { FaUserAstronaut } from "react-icons/fa";


const DataCard = ({ dataPoint }) => (
  <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 transition-all duration-300 group hover:border-teal-500 hover:shadow-2xl hover:shadow-teal-500/20">
    <div className="flex justify-between items-center mb-4">
      <span className="bg-teal-900 text-teal-300 text-xs font-semibold px-3 py-1 rounded-full">
        {dataPoint.deviceId}
      </span>
      <span className="text-gray-400 text-xs">
        {new Date(dataPoint.timeline).toLocaleDateString()}
      </span>
    </div>

    <div className="text-center my-6">
      <BsSoundwave className="text-teal-400 text-4xl mx-auto mb-3" />
      <p className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-teal-300 to-sky-400">
        {dataPoint.data.decibel}
        <span className="text-2xl text-gray-400 align-text-top"> dB</span>
      </p>
      <p className="text-sm text-gray-500 mt-1">Decibel Level</p>
    </div>

    <div className="flex items-center gap-3 text-gray-300 border-t border-gray-700 pt-4">
      <FaUserAstronaut className="text-gray-400 text-lg w-5 text-center" />
      <p className="font-mono text-xs break-all text-gray-400">{dataPoint.owner}</p>
    </div>

    <button className="w-full mt-6 bg-gradient-to-r from-teal-600 to-sky-600 text-white font-bold py-3 rounded-xl hover:from-teal-500 hover:to-sky-500 transition-all duration-300 transform hover:scale-105 shadow-lg">
      Purchase Data
    </button>
  </div>
);

const DataList = () => (
  <div className="w-full">
    <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-sky-400 mb-10 text-center">
      Data Stream Marketplace
    </h2>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
      {decibelData.map((item) => (
        <DataCard key={item.id} dataPoint={item} />
      ))}
    </div>
  </div>
);

export default DataList;