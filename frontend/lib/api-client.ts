/**
 * API client — axios instance dengan interceptors JWT untuk Admin & Siswa
 */
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const apiClient = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

// ── Request interceptor: attach JWT ──────────────────────────────────────────
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    // Admin menyimpan token di "admin_access_token", siswa di "access_token"
    // Prioritaskan admin terlebih dahulu karena apiClient dipakai di halaman admin
    const token =
      localStorage.getItem("admin_access_token") ||
      localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// ── Response interceptor: handle 401 → refresh ───────────────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // Deteksi apakah ini admin atau siswa berdasarkan token yang aktif
      const isAdmin = !!localStorage.getItem("admin_access_token");
      const refreshToken = localStorage.getItem(
        isAdmin ? "admin_refresh_token" : "refresh_token"
      );

      if (refreshToken) {
        try {
          const res = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token, refresh_token: newRefresh } = res.data;

          if (isAdmin) {
            localStorage.setItem("admin_access_token", access_token);
            localStorage.setItem("admin_refresh_token", newRefresh);
          } else {
            localStorage.setItem("access_token", access_token);
            localStorage.setItem("refresh_token", newRefresh);
          }

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        } catch {
          // Refresh gagal → logout ke halaman yang sesuai
          if (isAdmin) {
            localStorage.removeItem("admin_access_token");
            localStorage.removeItem("admin_refresh_token");
            window.location.href = "/admin/login";
          } else {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            window.location.href = "/login";
          }
        }
      } else {
        // Tidak ada refresh token → redirect ke login
        if (isAdmin) {
          window.location.href = "/admin/login";
        } else {
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
