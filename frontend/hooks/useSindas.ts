/**
 * useSindas.ts — React Query hooks untuk integrasi SINDAS monitoring
 * Digunakan di halaman /admin/sindas untuk menampilkan status & log sinkronisasi
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "../lib/api-client";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface SindasSyncStatus {
  sindas_enabled: boolean;
  sindas_api_configured: boolean;
  today_total: number;
  today_success: number;
  today_failed: number;
  today_skipped: number;
  last_sync_at: string | null;
  last_sync_nis: string | null;
  total_all_time: number;
}

export interface SindasSyncLog {
  id: number;
  event_id: string | null;
  event_type: "created" | "updated" | "deleted" | "pull";
  nis_sindas: string | null;
  siswa_id: number | null;
  sekolah_id: number | null;
  status: "success" | "failed" | "skipped";
  error_message: string | null;
  changes_summary: Record<string, unknown> | null;
  processed_at: string;
  sindas_timestamp: string | null;
}

export interface SindasPullRequest {
  sekolah_id?: number | null;
  kelas?: string | null;
  limit?: number;
}

export interface SindasPullResponse {
  status: string;
  message: string;
  total_fetched: number;
  total_created: number;
  total_updated: number;
  total_skipped: number;
  total_failed: number;
  duration_ms: number | null;
}

// ─── Query Keys ───────────────────────────────────────────────────────────────

export const sindasKeys = {
  all: ["sindas"] as const,
  status: () => [...sindasKeys.all, "status"] as const,
  logs: (filters?: Record<string, unknown>) =>
    [...sindasKeys.all, "logs", filters] as const,
};

// ─── Hooks ────────────────────────────────────────────────────────────────────

/**
 * Hook untuk memantau status sinkronisasi SINDAS.
 * Auto-refresh setiap 30 detik.
 */
export function useSindasSyncStatus() {
  return useQuery<SindasSyncStatus>({
    queryKey: sindasKeys.status(),
    queryFn: async () => {
      const res = await apiClient.get("/sindas/sync-status");
      return res.data;
    },
    refetchInterval: 30_000, // polling setiap 30 detik
    staleTime: 15_000,
  });
}

/**
 * Hook untuk mengambil riwayat log sinkronisasi SINDAS.
 */
export function useSindasSyncLogs(filters?: {
  page?: number;
  limit?: number;
  status?: string;
  nis?: string;
}) {
  return useQuery<SindasSyncLog[]>({
    queryKey: sindasKeys.logs(filters),
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.page) params.set("page", String(filters.page));
      if (filters?.limit) params.set("limit", String(filters.limit));
      if (filters?.status) params.set("status", filters.status);
      if (filters?.nis) params.set("nis", filters.nis);
      const res = await apiClient.get(`/sindas/sync-logs?${params.toString()}`);
      return res.data;
    },
    staleTime: 10_000,
  });
}

/**
 * Mutation hook untuk trigger pull manual dari API SINDAS.
 * Hanya dapat digunakan oleh Super Admin.
 */
export function usePullSindas() {
  const queryClient = useQueryClient();
  return useMutation<SindasPullResponse, Error, SindasPullRequest>({
    mutationFn: async (payload) => {
      const res = await apiClient.post("/sindas/pull", payload);
      return res.data;
    },
    onSuccess: () => {
      // Invalidate queries agar status & log terupdate
      queryClient.invalidateQueries({ queryKey: sindasKeys.all });
    },
  });
}
