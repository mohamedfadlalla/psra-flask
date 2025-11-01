import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box, Container, CssBaseline } from '@mui/material';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Forum from './pages/Forum';
import Events from './pages/Events';
import Profile from './pages/Profile';
import Messages from './pages/Messages';
import Admin from './pages/Admin';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <AuthProvider>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Navbar />
        <Container component="main" sx={{ flexGrow: 1, py: 4 }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forum" element={<Forum />} />
            <Route path="/events" element={<Events />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/messages" element={<Messages />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </Container>
      </Box>
    </AuthProvider>
  );
}

export default App;
