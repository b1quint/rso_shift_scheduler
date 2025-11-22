import { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';
import { authService } from '../services';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    // Load user on mount if tokens exist
    useEffect(() => {
        const loadUser = async () => {
            const token = localStorage.getItem('access_token');
            if (token) {
                try {
                    const response = await authService.getCurrentUser();
                    setUser(response.data);
                    setIsAuthenticated(true);
                } catch (error) {
                    // Token invalid or expired
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                }
            }
            setIsLoading(false);
        };

        loadUser();
    }, []);

    const login = async (username, password) => {
        try {
            const response = await authService.login(username, password);
            const { access, refresh } = response.data;

            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);

            // Get user info
            const userResponse = await authService.getCurrentUser();
            setUser(userResponse.data);
            setIsAuthenticated(true);

            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Login failed'
            };
        }
    };

    const logout = async () => {
        try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                await authService.logout(refreshToken);
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            setUser(null);
            setIsAuthenticated(false);
        }
    };

    const refreshUser = async () => {
        try {
            const response = await authService.getCurrentUser();
            setUser(response.data);
            return response.data;
        } catch (error) {
            console.error('Failed to refresh user:', error);
            return null;
        }
    };

    const value = {
        user,
        isAuthenticated,
        isLoading,
        login,
        logout,
        refreshUser,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
