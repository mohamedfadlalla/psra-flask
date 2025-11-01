import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  Link as MuiLink,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const Register: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    phone_number: '',
    whatsapp_number: '',
    password: '',
    is_member: false,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'is_member' ? checked : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await register(formData);
      navigate('/');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="sm" sx={{ py: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography component="h1" variant="h4" align="center" gutterBottom>
          Sign Up
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="name"
            label="Full Name"
            name="name"
            autoComplete="name"
            autoFocus
            value={formData.name}
            onChange={handleChange}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            autoComplete="email"
            value={formData.email}
            onChange={handleChange}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            id="phone_number"
            label="Phone Number"
            name="phone_number"
            autoComplete="tel"
            value={formData.phone_number}
            onChange={handleChange}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            id="whatsapp_number"
            label="WhatsApp Number"
            name="whatsapp_number"
            autoComplete="tel"
            value={formData.whatsapp_number}
            onChange={handleChange}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="new-password"
            value={formData.password}
            onChange={handleChange}
          />
          <FormControlLabel
            control={
              <Checkbox
                name="is_member"
                checked={formData.is_member}
                onChange={handleChange}
                color="primary"
              />
            }
            label="I am a member of the Faculty of Pharmacy"
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? 'Creating Account...' : 'Sign Up'}
          </Button>
          <Box textAlign="center">
            <MuiLink component={Link} to="/login" variant="body2">
              {"Already have an account? Sign In"}
            </MuiLink>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default Register;
