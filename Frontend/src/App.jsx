import React from 'react'
import { Routes, Route } from 'react-router-dom';

import Home from './pages/Home.jsx';
import ProtectedRoute from './components/ProtectedRoutes.jsx';
import Dashboard from './pages/Dashboard.jsx';

function App() {
  return (
    <div className='bg-red-400'>
      <Routes>
        <Route path="/" element={<Home/>} />

        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  )
}

export default App