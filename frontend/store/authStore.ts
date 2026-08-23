/**
 * store/authStore.ts — Zustand store untuk state otentikasi siswa
 */
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export interface SiswaProfile {
  id: number;
  nis: string;
  nama_lengkap: string;
  kelas?: string;
  angkatan?: number;
  email?: string;
  telepon?: string;
  sekolah_id: number;
  foto_path?: string;
}

interface AuthState {
  isAuthenticated: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  siswa: SiswaProfile | null;
  login: (tokens: { access_token: string; refresh_token: string }, siswa: SiswaProfile) => void;
  logout: () => void;
  updateSiswa: (data: Partial<SiswaProfile>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      accessToken: null,
      refreshToken: null,
      siswa: null,

      login: (tokens, siswa) => {
        // Simpan token di localStorage untuk diambil axios interceptor
        if (typeof window !== "undefined") {
          localStorage.setItem("access_token", tokens.access_token);
          localStorage.setItem("refresh_token", tokens.refresh_token);
        }
        set({
          isAuthenticated: true,
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
          siswa,
        });
      },

      logout: () => {
        if (typeof window !== "undefined") {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        }
        set({
          isAuthenticated: false,
          accessToken: null,
          refreshToken: null,
          siswa: null,
        });
      },

      updateSiswa: (data) =>
        set((state) => ({
          siswa: state.siswa ? { ...state.siswa, ...data } : null,
        })),
    }),
    {
      name: "dms-auth-storage",
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        siswa: state.siswa,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
);
