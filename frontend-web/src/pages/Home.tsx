import React from 'react';

const Home: React.FC = () => {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Welcome to GenXcover</h1>
      <p>AI-powered music generation and analysis platform</p>
      <div style={{ marginTop: '20px' }}>
        <a href="/login" style={{ marginRight: '10px', padding: '10px 20px', backgroundColor: '#1976d2', color: 'white', textDecoration: 'none', borderRadius: '4px' }}>
          Login
        </a>
        <a href="/register" style={{ padding: '10px 20px', backgroundColor: '#dc004e', color: 'white', textDecoration: 'none', borderRadius: '4px' }}>
          Register
        </a>
      </div>
    </div>
  );
};

export default Home;
