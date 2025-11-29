import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || '';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Добавляем API ключ в заголовки (если указан)
    if (API_KEY) {
      this.client.defaults.headers.common['X-API-Key'] = API_KEY;
    }

    // Interceptor для обработки ошибок
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          console.error('Unauthorized: Check your API key');
        }
        return Promise.reject(error);
      }
    );
  }

  get instance(): AxiosInstance {
    return this.client;
  }

  setApiKey(key: string) {
    this.client.defaults.headers.common['X-API-Key'] = key;
  }
}

export const apiClient = new ApiClient();
export default apiClient.instance;
