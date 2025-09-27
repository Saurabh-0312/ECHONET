import React from 'react';

const DetailRow = ({ label, value, isMono = false }) => (
    <div className="flex justify-between">
        <span>{label}:</span>
        <span className={isMono ? "font-mono" : ""}>{value || "N/A"}</span>
    </div>
);

function SensorCard({ device, onDelete, isSearchResult = false }) {
    const cardClasses = isSearchResult
        ? `p-4 rounded-lg border-l-4 bg-white text-black ${device.isYours ? "border-green-500" : "border-blue-500"}`
        : "sensor-card p-4 rounded-lg card-hover bg-white text-black";

    return (
        <div className={cardClasses}>
            <div className="flex items-center justify-between mb-3">
                <h4 className="font-bold text-black text-sm truncate">{device.name}</h4>
                <div className="flex items-center space-x-2">
                    <div className="flex items-center space-x-1">
                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                        <span className="text-xs text-green-600">Live</span>
                    </div>
                    <button onClick={() => onDelete(device.id, device.name)} className="bg-red-500 hover:bg-red-600 text-white text-xs px-1 py-1 rounded transition-colors" title="Delete sensor">
                        <i className="fas fa-trash">Delete</i>
                    </button>
                </div>
            </div>
            <div className="space-y-2 text-xs text-black">
                <DetailRow label="Type" value={device.type} />
                <DetailRow label="Data Type" value={device.dataType} />
                <DetailRow label="Project" value={device.project} />
                <DetailRow label="Locality" value={device.locality} />
                <DetailRow label="Coordinates" value={`${device.latitude}, ${device.longitude}`} isMono={true} />
                <div className="flex justify-between items-center">
                    <span>Owner:</span>
                    <span className="font-mono text-xs break-all truncate" title={device.ownerAddress}>{device.ownerAddress}</span>
                </div>
                {device.hypergraphEntityId && (
                     <div className="flex justify-between items-center">
                        <span>Entity ID:</span>
                        <span className="font-mono text-xs break-all truncate" title={device.hypergraphEntityId}>{device.hypergraphEntityId}</span>
                    </div>
                )}
            </div>
            <div className="mt-3 pt-2 border-t border-gray-200">
                <div className="flex items-center text-xs text-black">
                    <i className="fas fa-map-marker-alt mr-1"></i>
                    <span>{device.location}</span>
                </div>
            </div>
        </div>
    );
}

export default SensorCard;