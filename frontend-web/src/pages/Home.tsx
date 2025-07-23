import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div style={{ padding: '40px 20px', textAlign: 'center', minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '20px', background: 'linear-gradient(45deg, #74b9ff, #0984e3)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          Welcome to GenXcover
        </h1>
        <p style={{ fontSize: '1.2rem', marginBottom: '40px', opacity: 0.9 }}>
          AI-powered music generation and analysis platform
        </p>
        
        <div style={{ display: 'flex', gap: '15px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/login" className="btn btn-secondary" style={{ textDecoration: 'none', minWidth: '120px' }}>
            Sign In
          </Link>
          <Link to="/register" className="btn btn-primary" style={{ textDecoration: 'none', minWidth: '120px' }}>
            Get Started
          </Link>
        </div>
        
        <div style={{ marginTop: '40px', padding: '20px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '12px' }}>
          <h3 style={{ marginTop: 0, color: '#74b9ff' }}>🎵 What You Can Do</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginTop: '20px' }}>
            <div>
              <h4 style={{ color: '#ff6b6b', margin: '0 0 10px 0' }}>Generate Music</h4>
              <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>Create original songs with AI</p>
            </div>
            <div>
              <h4 style={{ color: '#00b894', margin: '0 0 10px 0' }}>Record & Edit</h4>
              <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>Professional recording tools</p>
            </div>
            <div>
              <h4 style={{ color: '#fdcb6e', margin: '0 0 10px 0' }}>Analyze Trends</h4>
              <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>Market intelligence insights</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
