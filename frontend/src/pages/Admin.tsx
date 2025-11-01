import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const Admin: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box textAlign="center">
        <Typography variant="h4" component="h1" gutterBottom>
          Admin Panel
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Admin functionality coming soon...
        </Typography>
      </Box>
    </Container>
  );
};

export default Admin;
