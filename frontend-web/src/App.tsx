import React from 'react';
import { Provider } from 'react-redux';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { store } from './store';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import './App.css';

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <Router>
        <div className="App">
          {/* Authentication temporarily disabled - routing directly to main functionality */}
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Home />} />
            <Route path="/register" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/generate-music" element={<Home />} />
          </Routes>
        </div>
      </Router>
    </Provider>
  );
};

export default App;
