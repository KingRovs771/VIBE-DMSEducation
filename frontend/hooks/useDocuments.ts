/**
 * Custom hooks untuk document API
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import toast from "react-hot-toast";

// ── Types ─────────────────────────────────────────────────────────────────────
export interface Document {
  id: number;
  title: string;
  description?: string;
  filename: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  document_key: string;
  tags: string[];
  status: string;
  access_level: string;
  version: number;
  owner_id: number;
  created_at: string;
  updated_at: string;
  download_url?: string;
}

export interface DocumentList {
  items: Document[];
  total: number;
  page: number;
  size: number;
}

// ── Hooks ─────────────────────────────────────────────────────────────────────

export function useDocuments(params: {
  query?: string;
  category_id?: number;
  status?: string;
  page?: number;
  size?: number;
}) {
  return useQuery({
    queryKey: ["documents", params],
    queryFn: async () => {
      const res = await apiClient.get<DocumentList>("/documents/search", {
        params,
      });
      return res.data;
    },
  });
}

export function useDocument(id: number) {
  return useQuery({
    queryKey: ["document", id],
    queryFn: async () => {
      const res = await apiClient.get<Document>(`/documents/${id}`);
      return res.data;
    },
    enabled: !!id,
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (formData: FormData) => {
      const res = await apiClient.post<Document>("/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      toast.success("Dokumen berhasil diunggah!");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Gagal mengunggah dokumen");
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/documents/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      toast.success("Dokumen berhasil dihapus");
    },
    onError: () => {
      toast.error("Gagal menghapus dokumen");
    },
  });
}

export function useApproveDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, status, note }: { id: number; status: string; note?: string }) => {
      const res = await apiClient.post(`/documents/${id}/approve`, { status, note });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      toast.success("Status dokumen berhasil diperbarui");
    },
  });
}
