import React from 'react'
import { Routes, Route } from 'react-router-dom';

import Home from './pages/Home.jsx';

function App() {
  return (
    <div className='bg-red-400'>
      <Routes>
        <Route path="/" element={<Home/>} />
      </Routes>
    </div>
  )
}

export default App