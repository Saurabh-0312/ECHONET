import React from 'react';

function Header() {
    return (
        <header className="bg-white text-black py-6 shadow-lg">
            <div className="container mx-auto px-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <i className="fas fa-network-wired text-3xl"></i>
                        <div>
                            <h1 className="text-3xl font-bold text-black">DePIN Hypergraph</h1>
                            <p className="text-black">Cross-Project Sensor Discovery Network</p>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-sm text-black">Polygon Amoy Testnet</div>
                        <div className="text-xs text-black">🔌 Connected</div>
                    </div>
                </div>
            </div>
        </header>
    );
}

export default Header;