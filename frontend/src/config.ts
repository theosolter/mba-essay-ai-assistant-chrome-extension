export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error('VITE_API_BASE_URL environment variable is not defined');
}

console.log("API_BASE_URL:", API_BASE_URL);