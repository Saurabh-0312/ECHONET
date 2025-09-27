import React, { useState } from "react";
import DeviceList from "../components/marketplace/DeviceList.jsx";
import DataList from "../components/marketplace/DataList.jsx";
import { ChevronDown } from "lucide-react";

const Market = () => {
  const [selectedMarketplace, setSelectedMarketplace] = useState("devices");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const marketplaceOptions = [
    { value: "devices", label: "Devices" },
    { value: "data", label: "Data Streams" },
  ];

  return (
    <div className="bg-black min-h-screen">
      <div className="container mx-auto w-[90%] md:w-[85%] lg:w-[80%] max-w-7xl pt-28">
        {/* Marketplace Selector */}
        <div className="relative mb-8">
          <button
            className="flex items-center justify-between w-full bg-neutral-900 text-white px-5 py-3 rounded-xl shadow-md border border-gray-700 hover:bg-neutral-800 transition-colors"
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          >
            <span className="text-lg font-semibold">
              {marketplaceOptions.find((opt) => opt.value === selectedMarketplace)?.label}
            </span>
            <ChevronDown className={`transition-transform ${isDropdownOpen ? "rotate-180" : ""}`} />
          </button>

          {isDropdownOpen && (
            <div className="absolute mt-2 w-full bg-neutral-900 border border-gray-700 rounded-xl shadow-lg overflow-hidden">
              {marketplaceOptions.map((option) => (
                <button
                  key={option.value}
                  className={`w-full text-left px-5 py-3 text-white hover:bg-neutral-700 transition-colors ${
                    selectedMarketplace === option.value ? "bg-neutral-800" : ""
                  }`}
                  onClick={() => {
                    setSelectedMarketplace(option.value);
                    setIsDropdownOpen(false);
                  }}
                >
                  {option.label}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Marketplace Content */}
        <div className="bg-neutral-950 p-6 sm:p-10 rounded-2xl shadow-xl border border-gray-700">
          {selectedMarketplace === "devices" && <DeviceList />}
          {selectedMarketplace === "data" && <DataList />}
        </div>
      </div>
    </div>
  );
};

export default Market;
