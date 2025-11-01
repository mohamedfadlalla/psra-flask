import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Box,
  Badge,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  AccountCircle,
  Message,
  AdminPanelSettings,
  Logout,
  Login,
  PersonAdd,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const Navbar: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleProfileMenuClose();
    navigate('/');
  };

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = [
    { text: 'Home', path: '/' },
    { text: 'Forum', path: '/forum' },
    { text: 'Events', path: '/events' },
  ];

  const drawer = (
    <Box onClick={handleDrawerToggle} sx={{ textAlign: 'center' }}>
      <Typography variant="h6" sx={{ my: 2, color: theme.palette.primary.main }}>
        PSRA
      </Typography>
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton component={Link} to={item.path}>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
        {isAuthenticated ? (
          <>
            <ListItem disablePadding>
              <ListItemButton component={Link} to="/messages">
                <ListItemText primary="Messages" />
              </ListItemButton>
            </ListItem>
            <ListItem disablePadding>
              <ListItemButton component={Link} to="/profile">
                <ListItemText primary="Profile" />
              </ListItemButton>
            </ListItem>
            {user?.is_admin && (
              <ListItem disablePadding>
                <ListItemButton component={Link} to="/admin">
                  <ListItemText primary="Admin" />
                </ListItemButton>
              </ListItem>
            )}
            <ListItem disablePadding>
              <ListItemButton onClick={handleLogout}>
                <ListItemText primary="Logout" />
              </ListItemButton>
            </ListItem>
          </>
        ) : (
          <>
            <ListItem disablePadding>
              <ListItemButton component={Link} to="/login">
                <ListItemText primary="Sign In" />
              </ListItemButton>
            </ListItem>
            <ListItem disablePadding>
              <ListItemButton component={Link} to="/register">
                <ListItemText primary="Sign Up" />
              </ListItemButton>
            </ListItem>
          </>
        )}
      </List>
    </Box>
  );

  return (
    <>
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <Typography
            variant="h6"
            component={Link}
            to="/"
            sx={{
              flexGrow: 1,
              textDecoration: 'none',
              color: 'inherit',
              fontWeight: 'bold',
            }}
          >
            PSRA
          </Typography>

          {isMobile ? (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
            >
              <MenuIcon />
            </IconButton>
          ) : (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {menuItems.map((item) => (
                <Button
                  key={item.text}
                  color="inherit"
                  component={Link}
                  to={item.path}
                  sx={{ mx: 1 }}
                >
                  {item.text}
                </Button>
              ))}

              {isAuthenticated ? (
                <>
                  <IconButton
                    color="inherit"
                    component={Link}
                    to="/messages"
                    sx={{ mx: 1 }}
                  >
                    <Badge badgeContent={0} color="error">
                      <Message />
                    </Badge>
                  </IconButton>

                  <IconButton
                    color="inherit"
                    onClick={handleProfileMenuOpen}
                    sx={{ mx: 1 }}
                  >
                    <AccountCircle />
                  </IconButton>

                  <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={handleProfileMenuClose}
                  >
                    <MenuItem component={Link} to="/profile" onClick={handleProfileMenuClose}>
                      Profile
                    </MenuItem>
                    {user?.is_admin && (
                      <MenuItem component={Link} to="/admin" onClick={handleProfileMenuClose}>
                        <AdminPanelSettings sx={{ mr: 1 }} />
                        Admin
                      </MenuItem>
                    )}
                    <MenuItem onClick={handleLogout}>
                      <Logout sx={{ mr: 1 }} />
                      Logout
                    </MenuItem>
                  </Menu>
                </>
              ) : (
                <>
                  <Button
                    color="inherit"
                    component={Link}
                    to="/login"
                    startIcon={<Login />}
                    sx={{ mx: 1 }}
                  >
                    Sign In
                  </Button>
                  <Button
                    variant="outlined"
                    color="inherit"
                    component={Link}
                    to="/register"
                    startIcon={<PersonAdd />}
                    sx={{ mx: 1 }}
                  >
                    Sign Up
                  </Button>
                </>
              )}
            </Box>
          )}
        </Toolbar>
      </AppBar>

      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 240 },
        }}
      >
        {drawer}
      </Drawer>
    </>
  );
};

export default Navbar;
