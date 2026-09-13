import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api';

export const getStats = async () => {
    const response = await axios.get(`${API_URL}/stats`);
    return response.data;
};

export const getEvents = async (skip = 0, limit = 50, q = '') => {
    const response = await axios.get(`${API_URL}/events`, {
        params: { skip, limit, q: q || undefined }
    });
    return response.data;
};

export const uploadVideo = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.post(`${API_URL}/upload`, formData);
    return response.data;
};
