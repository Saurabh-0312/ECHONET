import React, { useState } from 'react';

const InputField = ({ id, label, ...props }) => (
    <div>
        <label htmlFor={id} className="block text-sm font-medium text-black mb-2">{label}</label>
        <input id={id} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black" {...props} />
    </div>
);

function RegistrationForm({ onRegister }) {
    const [formData, setFormData] = useState({
        deviceId: '', deviceType: '', dataType: '', deviceLocation: '', locality: '',
        latitude: '', longitude: '', projectName: '', ownerAddress: ''
    });
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.id]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        const success = await onRegister({
            ...formData,
            latitude: parseFloat(formData.latitude),
            longitude: parseFloat(formData.longitude)
        });
        if (success) {
            e.target.reset();
            setFormData({
                deviceId: '', deviceType: '', dataType: '', deviceLocation: '', locality: '',
                latitude: '', longitude: '', projectName: '', ownerAddress: ''
            });
        }
        setIsLoading(false);
    };

    return (
        <div className="bg-white text-black rounded-lg shadow-lg p-6">
            <div className="flex items-center mb-6">
                <i className="fas fa-plus-circle text-2xl text-blue-500 mr-3"></i>
                <h2 className="text-2xl font-bold text-black">Register New Device</h2>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
                <InputField id="deviceId" label="Device ID" type="text" placeholder="e.g., SENSOR-001" required value={formData.deviceId} onChange={handleChange} />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <InputField id="deviceType" label="Type of Sensor" type="text" placeholder="e.g., Temperature" required value={formData.deviceType} onChange={handleChange} />
                    <InputField id="dataType" label="Data Type" type="text" placeholder="e.g., Ambient Sound Level (dB)" required value={formData.dataType} onChange={handleChange} />
                </div>
                <InputField id="deviceLocation" label="Location" type="text" placeholder="e.g., New Delhi, India" required value={formData.deviceLocation} onChange={handleChange} />
                <InputField id="locality" label="Locality in City" type="text" placeholder="e.g., Connaught Place" required value={formData.locality} onChange={handleChange} />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <InputField id="latitude" label="Latitude" type="number" step="any" placeholder="e.g., 28.6139" required value={formData.latitude} onChange={handleChange} />
                    <InputField id="longitude" label="Longitude" type="number" step="any" placeholder="e.g., 77.2090" required value={formData.longitude} onChange={handleChange} />
                </div>
                <InputField id="projectName" label="Project Name" type="text" placeholder="e.g., AirNet DePIN" required value={formData.projectName} onChange={handleChange} />
                <InputField id="ownerAddress" label="Owner ETH Address" type="text" placeholder="0x..." pattern="^0x[a-fA-F0-9]{40}$" required value={formData.ownerAddress} onChange={handleChange} />
                
                <button type="submit" disabled={isLoading} className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 transition duration-200 flex items-center justify-center disabled:opacity-50">
                    <i className="fas fa-cloud-upload-alt mr-2"></i>
                    <span>{isLoading ? 'Registering...' : 'Register Device & Auto-Publish'}</span>
                    {isLoading && <i className="fas fa-spinner loading-spinner ml-2"></i>}
                </button>
            </form>
        </div>
    );
}

export default RegistrationForm;