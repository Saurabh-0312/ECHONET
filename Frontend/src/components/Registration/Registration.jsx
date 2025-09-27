import React, { useState } from 'react';
import MapPinIcon from './icons/MapPinIcon.jsx';
import GlobeIcon from './icons/GlobeIcon.jsx';
import ServerIcon from './icons/ServerIcon.jsx';
import { useRegisterDevice } from '../../hooks/UseRegisterDevice.jsx';
import { useAuth } from '@/context/AuthContext.jsx';
import { Navigate, useNavigate } from 'react-router-dom';

// --- Main App Component ---

// --- Main App Component ---

function Registration() {
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [macAddress, setMacAddress] = useState('');
  
  const { registerDevice, isLoading, error, isSuccess } = useRegisterDevice();
  const { setIsRegistered } = useAuth();    

  const Navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    // The hook will handle setting loading, error, and success states
    const result = await registerDevice({ latitude, longitude, macAddress });
    
    // If the registration was successful, clear the form fields
    if (result.success) {
      setLatitude('');
      setLongitude('');
      setMacAddress('');
      setIsRegistered(true); // Update the registration status in AuthContext
      Navigate('/dashboard'); // Redirect to dashboard after successful registration
    }
  };

  return (
    <div className="min-h-screen w-full bg-black text-white flex items-center justify-center p-4 font-sans">
      <div className="w-full max-w-md mx-auto p-8 space-y-8 bg-gray-900 rounded-2xl shadow-2xl border border-gray-700">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white">Register Device</h1>
          <p className="text-gray-400 mt-2">Enter location and device details below.</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Latitude Input */}
          <div className="relative">
            <label htmlFor="latitude" className="sr-only">Latitude</label>
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MapPinIcon />
            </div>
            <input
              id="latitude"
              type="text"
              required
              value={latitude}
              onChange={(e) => setLatitude(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="Latitude (e.g., 34.0522)"
            />
          </div>

          {/* Longitude Input */}
          <div className="relative">
            <label htmlFor="longitude" className="sr-only">Longitude</label>
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <GlobeIcon />
            </div>
            <input
              id="longitude"
              type="text"
              required
              value={longitude}
              onChange={(e) => setLongitude(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="Longitude (e.g., -118.2437)"
            />
          </div>

          {/* MAC Address Input */}
          <div className="relative">
            <label htmlFor="mac-address" className="sr-only">Device MAC Address</label>
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <ServerIcon />
            </div>
            <input
              id="mac-address"
              type="text"
              required
              value={macAddress}
              onChange={(e) => setMacAddress(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="MAC Address (e.g., 00:1A:2B:3C:4D:5E)"
            />
          </div>

          {/* Feedback Area */}
          <div className="h-5 text-center">
            {error && <p className="text-red-500 text-sm">{error}</p>}
            {isSuccess && <p className="text-green-500 text-sm">Device registered successfully!</p>}
          </div>

          {/* Submit Button */}
          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-blue-500 transition duration-300 ease-in-out transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:scale-100 flex justify-center items-center"
            >
              {isLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Registering...
                  </>
              ) : (
                'Register Device'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Registration;

