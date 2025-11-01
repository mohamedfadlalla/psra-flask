import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const Forum: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box textAlign="center">
        <Typography variant="h4" component="h1" gutterBottom>
          Forum
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Forum functionality coming soon...
        </Typography>
      </Box>
    </Container>
  );
};

export default Forum;
