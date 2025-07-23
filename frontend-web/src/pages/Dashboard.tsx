import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { RootState } from '../store';
import { logout } from '../store/slices/authSlice';

const Dashboard: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state: RootState) => state.auth);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/');
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '30px',
        padding: '20px',
        background: 'rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        backdropFilter: 'blur(10px)'
      }}>
        <div>
          <h1 style={{ margin: 0, marginBottom: '5px' }}>Welcome to GenXcover</h1>
          <p style={{ margin: 0, opacity: 0.8 }}>
            {user ? `Hello, ${user.username}!` : 'Hello, User!'}
          </p>
        </div>
        <button 
          onClick={handleLogout}
          className="btn btn-secondary"
          style={{ padding: '8px 16px' }}
        >
          Logout
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        <div className="card">
          <h3 style={{ marginTop: 0, color: '#74b9ff' }}>🎵 Music Generation</h3>
          <p>Create AI-powered music with advanced algorithms and machine learning.</p>
          <button className="btn btn-primary" style={{ marginTop: '15px' }}>
            Generate Music
          </button>
        </div>

        <div className="card">
          <h3 style={{ marginTop: 0, color: '#ff6b6b' }}>🎤 Recording Studio</h3>
          <p>Record, edit, and enhance your music with professional tools.</p>
          <button className="btn btn-primary" style={{ marginTop: '15px' }}>
            Start Recording
          </button>
        </div>

        <div className="card">
          <h3 style={{ marginTop: 0, color: '#00b894' }}>📊 Analytics</h3>
          <p>Analyze your music's potential and get insights on market trends.</p>
          <button className="btn btn-primary" style={{ marginTop: '15px' }}>
            View Analytics
          </button>
        </div>

        <div className="card">
          <h3 style={{ marginTop: 0, color: '#fdcb6e' }}>🎼 My Songs</h3>
          <p>Manage your created songs and track their performance.</p>
          <button className="btn btn-primary" style={{ marginTop: '15px' }}>
            View Songs
          </button>
        </div>
      </div>

      <div className="card" style={{ marginTop: '30px' }}>
        <h3 style={{ marginTop: 0, color: '#e17055' }}>🚀 Getting Started</h3>
        <p>Welcome to GenXcover! Here are some quick actions to get you started:</p>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '20px' }}>
          <button className="btn btn-secondary">Create Your First Song</button>
          <button className="btn btn-secondary">Explore Templates</button>
          <button className="btn btn-secondary">Join Community</button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
