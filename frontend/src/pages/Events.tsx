import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const Events: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box textAlign="center">
        <Typography variant="h4" component="h1" gutterBottom>
          Events
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Events functionality coming soon...
        </Typography>
      </Box>
    </Container>
  );
};

export default Events;
