import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const Messages: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box textAlign="center">
        <Typography variant="h4" component="h1" gutterBottom>
          Messages
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Messages functionality coming soon...
        </Typography>
      </Box>
    </Container>
  );
};

export default Messages;
