import React from 'react';

const StatCard = ({ icon, label, value }) => (
    <div className="bg-white text-black rounded-lg shadow-md p-6 text-center card-hover">
        <i className={`${icon} text-3xl mb-2`}></i>
        <div className="text-2xl font-bold text-black">{value}</div>
        <div className="text-black text-sm">{label}</div>
    </div>
);

function Stats({ stats }) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 bg-white text-black">
            <StatCard icon="fas fa-satellite-dish text-blue-500" label="Total Sensors" value={stats.totalSensors} />
            <StatCard icon="fas fa-project-diagram text-green-500" label="DePIN Projects" value={stats.totalProjects} />
            <StatCard icon="fas fa-map-marker-alt text-purple-500" label="Active Locations" value={stats.activeLocations} />
            <StatCard icon="fas fa-clock text-orange-500" label="Live Monitoring" value="24/7" />
        </div>
    );
}

export default Stats;