import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { RootState } from '../store';
import { registerUser } from '../store/slices/authSlice';

const Register: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { isLoading, error } = useSelector((state: RootState) => state.auth);

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }

    try {
      const result = await dispatch(registerUser({
        username: formData.username,
        email: formData.email,
        password: formData.password
      }) as any);
      
      if (result.type === 'auth/register/fulfilled') {
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Registration failed:', error);
    }
  };

  return (
    <div className="auth-container">
      <div className="card" style={{ maxWidth: '400px', margin: '50px auto' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '30px' }}>Create Account</h2>
        
        {error && (
          <div style={{ 
            background: 'rgba(255, 0, 0, 0.1)', 
            border: '1px solid rgba(255, 0, 0, 0.3)',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '20px',
            color: '#ff6b6b'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="form-input"
              placeholder="Enter your username"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="form-input"
              placeholder="Enter your email"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="form-input"
              placeholder="Enter your password"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Confirm Password</label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              className="form-input"
              placeholder="Confirm your password"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading}
            style={{ width: '100%', marginTop: '20px' }}
          >
            {isLoading ? (
              <>
                <div className="spinner" style={{ width: '20px', height: '20px', display: 'inline-block', marginRight: '10px' }}></div>
                Creating Account...
              </>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '20px' }}>
          <p>Already have an account? <Link to="/login" style={{ color: '#74b9ff' }}>Sign in</Link></p>
        </div>
      </div>
    </div>
  );
};

export default Register;
