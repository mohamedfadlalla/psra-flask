import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface User {
  id: number;
  name: string;
  email: string;
  is_admin: boolean;
  profile_picture_url?: string;
  phone_number?: string;
  whatsapp_number?: string;
  is_member?: boolean;
  status?: string;
  headline?: string;
  location?: string;
  about?: string;
  skills?: string;
  linkedin_url?: string;
  website_url?: string;
  languages?: string;
  certifications?: string;
  projects?: string;
  publications?: string;
  professional_summary?: string;
  cover_photo_url?: string;
  created_at?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => void;
  updateProfile: (profileData: any) => Promise<void>;
  isAuthenticated: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  // Set up axios interceptor for token
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Check if user is authenticated on app start
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const response = await axios.get('/api/auth/me');
          setUser(response.data.user);
        } catch (error) {
          // Token is invalid, remove it
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  const login = async (email: string, password: string) => {
    try {
      const response = await axios.post('/api/auth/login', { email, password });
      const { token: newToken, user: userData } = response.data;

      localStorage.setItem('token', newToken);
      setToken(newToken);
      setUser(userData);
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Login failed');
    }
  };

  const register = async (userData: any) => {
    try {
      const response = await axios.post('/api/auth/register', userData);
      const { token: newToken, user: newUser } = response.data;

      localStorage.setItem('token', newToken);
      setToken(newToken);
      setUser(newUser);
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Registration failed');
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  const updateProfile = async (profileData: any) => {
    try {
      const response = await axios.put('/api/profile/update', profileData);
      setUser(response.data.user);
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Profile update failed');
    }
  };

  const value = {
    user,
    token,
    login,
    register,
    logout,
    updateProfile,
    isAuthenticated: !!user,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
