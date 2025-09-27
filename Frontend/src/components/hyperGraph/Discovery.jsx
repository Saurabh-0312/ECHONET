import React, { useState } from 'react';
import SensorCard from './SensorCard';

function Discovery({ onSearch, results, onDelete }) {
    const [location, setLocation] = useState('Delhi');
    const [type, setType] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSearch = async () => {
        setIsLoading(true);
        await onSearch(location, type);
        setIsLoading(false);
    };

    return (
        <div className="bg-white text-black rounded-lg shadow-lg p-6">
            <div className="flex items-center mb-6">
                <i className="fas fa-search-location text-2xl text-purple-500 mr-3"></i>
                <h2 className="text-2xl font-bold text-black">Discover Devices</h2>
            </div>
            <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <input type="text" value={location} onChange={(e) => setLocation(e.target.value)} placeholder="Enter area name..." className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-black" />
                    <select value={type} onChange={(e) => setType(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-black">
                        <option value="">All Device Types</option>
                        <option value="sound">Sound</option>
                        <option value="air">Air Quality</option>
                        <option value="weather">Weather</option>
                    </select>
                </div>
                <button onClick={handleSearch} disabled={isLoading} className="w-full bg-purple-600 text-white py-3 px-4 rounded-md hover:bg-purple-700 transition duration-200 flex items-center justify-center disabled:opacity-50">
                    <i className="fas fa-search mr-2"></i>
                    <span>{isLoading ? 'Searching...' : 'Search Cross-Project Devices'}</span>
                    {isLoading && <i className="fas fa-spinner loading-spinner ml-2"></i>}
                </button>
            </div>
            <div className="mt-6">
                {results === null ? (
                    <div className="text-center text-gray-500"><i className="fas fa-search text-4xl mb-4"></i><p>Search for devices to see results.</p></div>
                ) : results.length === 0 ? (
                    <div className="text-center text-gray-500"><i className="fas fa-box-open text-4xl mb-4"></i><p>No devices found for this query.</p></div>
                ) : (
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                        {results.map(device => <SensorCard key={device.id} device={device} onDelete={onDelete} isSearchResult={true} />)}
                    </div>
                )}
            </div>
        </div>
    );
}

export default Discovery;