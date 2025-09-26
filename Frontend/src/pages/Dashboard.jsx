// DashboardPage.jsx
import React, { useEffect } from 'react';
import { useAuth } from '../context/AuthContext.jsx';
import { Routes, Route } from 'react-router-dom';

import Navbar from '../components/dashboard/Navbar.jsx';
import RegistrationPrompt from '../components/dashboard/RegistrationPrompt.jsx';
import Exchange from '../components/exchange/ExchangeCurrency.jsx';
import UserDashboard from '@/components/dashboard/main/UserDashboard.jsx';
// import Market from './Market.jsx';
// import HyperGraphDevice from './HyperGraphDevice.jsx';

function DashboardPage() {
    const {isRegistered,ensName } = useAuth();

    return (
        <div className="h-screen w-screen bg-black text-white flex flex-col overflow-hidden">
            <style>{`
                @keyframes fade-in {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .animate-fade-in {
                    animation: fade-in 0.6s ease-out forwards;
                }
            `}</style>

            <Navbar />
            <main className="flex-1 relative overflow-hidden">
                <Routes>
                    <Route
                        path="/dashboard"
                        element={
                            isRegistered ? (
                                <UserDashboard />
                            ) : (
                                <RegistrationPrompt />
                            )
                        }
                    />
                    <Route path="/exchange" element={<Exchange />} />
                    {/* <Route path="/market" element={<Market />} />
                    <Route path="/hypergraph" element={<HyperGraphDevice />} /> */}
                </Routes>
            </main>
        </div>
    );
}

export default DashboardPage;
