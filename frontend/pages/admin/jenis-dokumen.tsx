/**
 * pages/admin/jenis-dokumen.tsx — Manajemen Jenis Dokumen (Kategori)
 * Mengikuti spesifikasi [TABLE_COMPONENT], [TYPOGRAPHY], [SPACING_SHADOW] dari DESIGN.md
 */
import { useState } from "react";
import Head from "next/head";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { categoriesApi } from "@/lib/api";
import AdminLayout from "@/components/AdminLayout";
import { useRequireAdmin } from "@/hooks/useAdminAuth";
import {
  FolderIcon,
  PlusIcon,
  TrashIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon
} from "@heroicons/react/24/solid";
import { FolderOpenIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";

export default function AdminJenisDokumen() {
  useRequireAdmin();
  const queryClient = useQueryClient();

  const [newCat, setNewCat] = useState({
    name: "",
    description: "",
  });

  // Query ambil data categories
  const { data: categories = [], isLoading, refetch } = useQuery({
    queryKey: ["admin-categories"],
    queryFn: () => categoriesApi.getAll().then(res => res.data),
  });

  // Mutation Tambah Category
  const createMutation = useMutation({
    mutationFn: categoriesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-categories"] });
      toast.success("Jenis dokumen baru berhasil ditambahkan!");
      setNewCat({ name: "", description: "" });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Gagal menambahkan jenis dokumen.");
    },
  });

  // Mutation Hapus Category
  const deleteMutation = useMutation({
    mutationFn: categoriesApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-categories"] });
      toast.success("Jenis dokumen berhasil dihapus.");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Gagal menghapus jenis dokumen.");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCat.name.trim()) {
      toast.error("Nama kategori wajib diisi.");
      return;
    }
    // Normalisasi nama menjadi lowercase alphanumeric & underscore
    const normalizedName = newCat.name
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9_]/g, "_");

    createMutation.mutate({
      name: normalizedName,
      description: newCat.description.trim(),
    });
  };

  return (
    <AdminLayout title="Manajemen Jenis Dokumen">
      <Head>
        <title>Jenis Dokumen — DokumenSekolah Admin</title>
      </Head>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 font-body text-neutral-800">
        
        {/* Kolom Kiri: Daftar Jenis Dokumen */}
        <div className="lg:col-span-2 bg-white border border-[#D4DDD9] rounded-[20px] shadow-sm overflow-hidden flex flex-col">
          <div className="px-6 py-4 border-b border-[#EDF2F0] bg-[#F5F8F7] flex items-center justify-between">
            <div>
              <h3 className="font-display font-bold text-neutral-950 text-sm">Daftar Jenis Dokumen Aktif</h3>
              <p className="text-[11px] font-semibold text-[#8FA39B] mt-0.5">Tipe klasifikasi berkas terenkripsi di sistem</p>
            </div>
            <button
              onClick={() => refetch()}
              className="p-2 bg-white border border-[#D4DDD9] hover:bg-[#F5F8F7] text-neutral-400 hover:text-neutral-750 rounded-xl transition-all"
              title="Refresh Data"
            >
              <ArrowPathIcon className="w-4 h-4" />
            </button>
          </div>

          <div className="overflow-x-auto flex-1">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-[#F5F8F7] border-b border-[#D4DDD9]">
                  <th className="px-6 py-3 text-left text-[11px] font-bold text-[#8FA39B] uppercase tracking-wider">Nama Kunci (Sistem)</th>
                  <th className="px-6 py-3 text-left text-[11px] font-bold text-[#8FA39B] uppercase tracking-wider">Deskripsi Tampilan</th>
                  <th className="px-6 py-3 text-right text-[11px] font-bold text-[#8FA39B] uppercase tracking-wider">Aksi</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#EDF2F0]">
                {isLoading ? (
                  <tr>
                    <td colSpan={3} className="text-center py-12 text-[#8FA39B]">
                      <div className="w-6 h-6 border-2 border-[#208C68] border-t-transparent rounded-full animate-spin mx-auto" />
                    </td>
                  </tr>
                ) : categories.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="py-16 text-center text-[#8FA39B]">
                      <FolderOpenIcon className="w-10 h-10 mx-auto mb-2 opacity-35" />
                      <p className="text-xs font-semibold">Belum ada jenis dokumen tersedia</p>
                    </td>
                  </tr>
                ) : (
                  categories.map((cat: any) => (
                    <tr key={cat.id} className="hover:bg-[#F0FAF6] transition-colors duration-120">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="font-mono text-xs font-bold text-[#0F4C39] bg-[#E0F5EE] px-2.5 py-1 rounded-lg">
                          {cat.name}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-xs font-semibold text-neutral-700">
                        {cat.description || "—"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <button
                          onClick={() => {
                            if (confirm(`Hapus jenis dokumen "${cat.name}"? Dokumen terenkripsi yang sudah terunggah dengan jenis ini mungkin tidak dapat diklasifikasikan.`)) {
                              deleteMutation.mutate(cat.id);
                            }
                          }}
                          className="w-[28px] h-[28px] bg-red-50 hover:bg-red-100 rounded-lg flex items-center justify-center text-red-655 transition-colors shadow-sm inline-flex"
                          title="Hapus Jenis Dokumen"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Kolom Kanan: Tambah Baru Form */}
        <div className="bg-white border border-[#D4DDD9] rounded-[20px] p-6 shadow-sm h-fit space-y-4">
          <div className="border-b border-[#EDF2F0] pb-3 mb-2 flex items-center gap-2">
            <FolderIcon className="w-5 h-5 text-[#208C68]" />
            <h3 className="font-display font-bold text-neutral-950 text-sm">Tambah Jenis Dokumen</h3>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[10px] font-bold text-neutral-700 mb-1.5 uppercase">Nama Kunci (Lowercase & Alphanumeric) *</label>
              <input
                type="text"
                required
                value={newCat.name}
                onChange={(e) => setNewCat({ ...newCat, name: e.target.value })}
                placeholder="e.g. raport_kip, transkrip_nilai"
                className="w-full px-3 py-2 text-xs font-semibold rounded-xl border border-[#D4DDD9] bg-[#F5F8F7] text-neutral-800 focus:outline-none focus:border-[#3DB891] focus:ring-2 focus:ring-[#3DB891]/25 transition-all"
              />
              <p className="text-[9px] text-[#8FA39B] font-semibold mt-1">Spasi atau karakter non-alphanumeric akan dikonversi otomatis menjadi underscore (`_`).</p>
            </div>

            <div>
              <label className="block text-[10px] font-bold text-neutral-700 mb-1.5 uppercase">Deskripsi Tampilan</label>
              <textarea
                value={newCat.description}
                onChange={(e) => setNewCat({ ...newCat, description: e.target.value })}
                placeholder="e.g. Laporan Hasil Belajar Program KIP"
                rows={3}
                className="w-full px-3 py-2 text-xs font-semibold rounded-xl border border-[#D4DDD9] bg-[#F5F8F7] text-neutral-800 focus:outline-none focus:border-[#3DB891] focus:ring-2 focus:ring-[#3DB891]/25 transition-all resize-none"
              />
            </div>

            <button
              type="submit"
              disabled={createMutation.isPending}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-[#208C68] hover:bg-[#14503C] text-white text-xs font-bold rounded-xl transition-all shadow shadow-[#208C68]/15 disabled:opacity-50"
            >
              {createMutation.isPending ? (
                <div className="w-4 h-4 border border-white border-t-transparent rounded-full animate-spin" />
              ) : <PlusIcon className="w-4 h-4" />}
              Tambah Jenis Dokumen
            </button>
          </form>
        </div>

      </div>
    </AdminLayout>
  );
}
