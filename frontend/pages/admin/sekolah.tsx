import { useState, useEffect } from "react";
import Head from "next/head";
import AdminLayout from "@/components/AdminLayout";
import { BuildingOffice2Icon, MapPinIcon, PhoneIcon, GlobeAltIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import { sekolahApi } from "@/lib/api";

interface SekolahData {
  id: number;
  nama: string;
  kode: string; // NPSN
  alamat: string | null;
  kota: string | null;
  provinsi: string | null;
  kode_pos: string | null;
  telepon: string | null;
  email: string | null;
  website: string | null;
}

export default function BiodataSekolahPage() {
  const [sekolah, setSekolah] = useState<SekolahData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState<Partial<SekolahData>>({});

  useEffect(() => {
    fetchSekolah();
  }, []);

  const fetchSekolah = async () => {
    try {
      setLoading(true);
      const res = await sekolahApi.getBiodata();
      setSekolah(res.data);
      setFormData(res.data);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Gagal mengambil data sekolah");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      // Backend expects: nama, alamat, kota, provinsi, telepon, email, website
      // NOTE: `kode` (NPSN) is generated/set securely in NeuralKeyGen, if we allow edit, it's risky for existing docs.
      // But the endpoint only allows updating standard fields.
      const payload = {
        nama: formData.nama,
        alamat: formData.alamat,
        kota: formData.kota,
        provinsi: formData.provinsi,
        telepon: formData.telepon,
        email: formData.email,
        website: formData.website,
      };
      await sekolahApi.updateBiodata(payload);
      toast.success("Biodata sekolah berhasil diperbarui");
      fetchSekolah();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Gagal menyimpan biodata");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <AdminLayout title="Biodata Sekolah">
        <div className="flex justify-center p-20">
          <div className="animate-spin w-8 h-8 border-4 border-[#3DB891] border-t-transparent rounded-full" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title="Biodata Sekolah">
      <Head>
        <title>Biodata Sekolah - Admin DokumenSekolah</title>
      </Head>

      <div className="bg-white rounded-2xl shadow-sm border border-[#D4DDD9]/60 p-6 md:p-8 max-w-4xl">
        <div className="flex items-center gap-4 mb-8 pb-6 border-b border-gray-100">
          <div className="w-14 h-14 rounded-2xl bg-[#3DB891]/10 flex items-center justify-center text-[#208C68]">
            <BuildingOffice2Icon className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-xl font-display font-extrabold text-gray-900">Profil Institusi</h2>
            <p className="text-sm text-gray-500 font-medium mt-1">Kelola informasi sekolah yang ditampilkan pada dokumen.</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">Nama Sekolah</label>
              <input
                type="text"
                name="nama"
                value={formData.nama || ""}
                onChange={handleChange}
                required
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-[#3DB891] focus:ring-4 focus:ring-[#3DB891]/10 outline-none transition-all text-sm font-medium"
              />
            </div>
            
            <div>
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2 flex items-center gap-2">
                NPSN / Kode Sekolah 
                <span className="bg-amber-100 text-amber-700 text-[10px] px-2 py-0.5 rounded-full lowercase tracking-normal">Immutable</span>
              </label>
              <input
                type="text"
                value={formData.kode || ""}
                disabled
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-gray-500 outline-none transition-all text-sm font-medium cursor-not-allowed"
                title="NPSN terikat pada NeuralKeyGen dan tidak bisa diubah"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <MapPinIcon className="w-4 h-4 text-gray-400" />
                Alamat Lengkap
              </label>
              <textarea
                name="alamat"
                value={formData.alamat || ""}
                onChange={handleChange}
                rows={3}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-[#3DB891] focus:ring-4 focus:ring-[#3DB891]/10 outline-none transition-all text-sm font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">Kota / Kabupaten</label>
              <input
                type="text"
                name="kota"
                value={formData.kota || ""}
                onChange={handleChange}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-[#3DB891] focus:ring-4 focus:ring-[#3DB891]/10 outline-none transition-all text-sm font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">Provinsi</label>
              <input
                type="text"
                name="provinsi"
                value={formData.provinsi || ""}
                onChange={handleChange}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-[#3DB891] focus:ring-4 focus:ring-[#3DB891]/10 outline-none transition-all text-sm font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <PhoneIcon className="w-4 h-4 text-gray-400" />
                Telepon
              </label>
              <input
                type="text"
                name="telepon"
                value={formData.telepon || ""}
                onChange={handleChange}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-[#3DB891] focus:ring-4 focus:ring-[#3DB891]/10 outline-none transition-all text-sm font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">Email Sekolah</label>
              <input
                type="email"
                name="email"
                value={formData.email || ""}
                onChange={handleChange}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-[#3DB891] focus:ring-4 focus:ring-[#3DB891]/10 outline-none transition-all text-sm font-medium"
              />
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <GlobeAltIcon className="w-4 h-4 text-gray-400" />
                Website
              </label>
              <input
                type="text"
                name="website"
                value={formData.website || ""}
                onChange={handleChange}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-[#3DB891] focus:ring-4 focus:ring-[#3DB891]/10 outline-none transition-all text-sm font-medium"
              />
            </div>
          </div>

          <div className="pt-6 border-t border-gray-100 flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="bg-[#208C68] hover:bg-[#1A7456] text-white px-6 py-2.5 rounded-xl font-bold text-sm transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {saving ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Menyimpan...
                </>
              ) : (
                "Simpan Perubahan"
              )}
            </button>
          </div>
        </form>
      </div>
    </AdminLayout>
  );
}
