import { useState, useEffect } from "react";
import Head from "next/head";
import AdminLayout from "@/components/AdminLayout";
import { ChartBarSquareIcon, CheckBadgeIcon, ExclamationTriangleIcon, MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import { dinasApi } from "@/lib/api";

interface KepatuhanData {
  sekolah_id: number;
  nama_sekolah: string;
  total_siswa: number;
  siswa_punya_dokumen: number;
  persentase_kepatuhan: number;
}

interface BatchVerifyResult {
  nisn: string;
  status_terdaftar: boolean;
  jumlah_dokumen: number;
}

export default function DinasPage() {
  const [kepatuhan, setKepatuhan] = useState<KepatuhanData[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Batch verify states
  const [npsn, setNpsn] = useState("");
  const [nisnList, setNisnList] = useState("");
  const [verifying, setVerifying] = useState(false);
  const [verifyResults, setVerifyResults] = useState<BatchVerifyResult[]>([]);

  useEffect(() => {
    fetchKepatuhan();
  }, []);

  const fetchKepatuhan = async () => {
    try {
      setLoading(true);
      const res = await dinasApi.getKepatuhan();
      setKepatuhan(res.data);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Gagal mengambil data monitoring");
    } finally {
      setLoading(false);
    }
  };

  const handleBatchVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!npsn || !nisnList) {
      toast.error("NPSN dan Daftar NISN wajib diisi");
      return;
    }

    const nisnArr = nisnList.split("\n").map(s => s.trim()).filter(s => s.length > 0);
    if (nisnArr.length === 0) {
      toast.error("Format daftar NISN tidak valid");
      return;
    }

    try {
      setVerifying(true);
      const res = await dinasApi.batchVerify({
        npsn_sekolah: npsn,
        daftar_nisn: nisnArr
      });
      setVerifyResults(res.data.hasil || []);
      toast.success(`Berhasil memverifikasi ${res.data.total_diproses} NISN`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Gagal melakukan verifikasi batch");
    } finally {
      setVerifying(false);
    }
  };

  if (loading) {
    return (
      <AdminLayout title="Supervisi Dinas">
        <div className="flex justify-center p-20">
          <div className="animate-spin w-8 h-8 border-4 border-[#3DB891] border-t-transparent rounded-full" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title="Supervisi Dinas Pendidikan">
      <Head>
        <title>Supervisi Dinas - Admin DokumenSekolah</title>
      </Head>

      <div className="space-y-8">
        
        {/* Kepatuhan Upload Section */}
        <section className="bg-white rounded-2xl shadow-sm border border-[#D4DDD9]/60 p-6 md:p-8">
          <div className="flex items-center gap-4 mb-6 pb-4 border-b border-gray-100">
            <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600">
              <ChartBarSquareIcon className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-display font-bold text-gray-900">Monitoring Kepatuhan Upload</h2>
              <p className="text-xs text-gray-500 font-medium mt-0.5">Persentase siswa yang sudah memiliki minimal 1 dokumen digital di sekolah binaan.</p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 text-[11px] uppercase tracking-widest text-gray-500 font-bold border-y border-gray-200">
                  <th className="py-3 px-4">Nama Sekolah</th>
                  <th className="py-3 px-4">Siswa Terdaftar</th>
                  <th className="py-3 px-4">Memiliki Dokumen</th>
                  <th className="py-3 px-4">Persentase Kepatuhan</th>
                  <th className="py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="text-sm font-medium text-gray-700 divide-y divide-gray-100">
                {kepatuhan.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-gray-400">Belum ada data sekolah binaan.</td>
                  </tr>
                ) : (
                  kepatuhan.map((row) => (
                    <tr key={row.sekolah_id} className="hover:bg-gray-50/50 transition-colors">
                      <td className="py-3 px-4 font-bold text-gray-900">{row.nama_sekolah}</td>
                      <td className="py-3 px-4">{row.total_siswa}</td>
                      <td className="py-3 px-4">{row.siswa_punya_dokumen}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-3">
                          <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${row.persentase_kepatuhan >= 80 ? 'bg-green-500' : row.persentase_kepatuhan >= 50 ? 'bg-amber-400' : 'bg-red-500'}`}
                              style={{ width: `${row.persentase_kepatuhan}%` }}
                            />
                          </div>
                          <span className="text-xs">{row.persentase_kepatuhan.toFixed(1)}%</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        {row.persentase_kepatuhan >= 80 ? (
                          <span className="inline-flex items-center gap-1 text-green-700 bg-green-100 px-2 py-1 rounded text-xs font-bold">
                            <CheckBadgeIcon className="w-4 h-4" /> Baik
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-amber-700 bg-amber-100 px-2 py-1 rounded text-xs font-bold">
                            <ExclamationTriangleIcon className="w-4 h-4" /> Perlu Ditingkatkan
                          </span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

        {/* Batch Verify Section */}
        <section className="bg-white rounded-2xl shadow-sm border border-[#D4DDD9]/60 p-6 md:p-8">
          <div className="flex items-center gap-4 mb-6 pb-4 border-b border-gray-100">
            <div className="w-12 h-12 rounded-xl bg-purple-50 flex items-center justify-center text-purple-600">
              <MagnifyingGlassIcon className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-display font-bold text-gray-900">Verifikasi Batch NISN</h2>
              <p className="text-xs text-gray-500 font-medium mt-0.5">Cek pendaftaran siswa dan dokumen dari sekolah binaan secara massal.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <form onSubmit={handleBatchVerify} className="space-y-5">
              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">NPSN Sekolah Tujuan</label>
                <input
                  type="text"
                  value={npsn}
                  onChange={(e) => setNpsn(e.target.value)}
                  placeholder="Contoh: 20101234"
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-[#3DB891] focus:ring-4 focus:ring-[#3DB891]/10 outline-none transition-all text-sm font-medium"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
                  Daftar NISN <span className="text-gray-400 font-normal lowercase">(Satu per baris)</span>
                </label>
                <textarea
                  value={nisnList}
                  onChange={(e) => setNisnList(e.target.value)}
                  rows={6}
                  placeholder="0011223344&#10;0055667788"
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-[#3DB891] focus:ring-4 focus:ring-[#3DB891]/10 outline-none transition-all text-sm font-medium font-mono"
                />
              </div>

              <button
                type="submit"
                disabled={verifying}
                className="bg-purple-600 hover:bg-purple-700 text-white w-full py-2.5 rounded-xl font-bold text-sm transition-colors shadow-sm disabled:opacity-50 flex justify-center items-center gap-2"
              >
                {verifying ? "Memproses..." : "Mulai Verifikasi"}
              </button>
            </form>

            <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 overflow-y-auto max-h-[350px]">
              <h3 className="text-xs font-bold text-gray-700 uppercase tracking-widest mb-4">Hasil Verifikasi</h3>
              
              {verifyResults.length === 0 ? (
                <div className="text-sm text-gray-400 text-center py-10">Hasil verifikasi akan muncul di sini.</div>
              ) : (
                <ul className="space-y-3">
                  {verifyResults.map((r, i) => (
                    <li key={i} className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-100 shadow-sm">
                      <span className="font-mono text-sm font-bold text-gray-700">{r.nisn}</span>
                      {r.status_terdaftar ? (
                        <span className="flex items-center gap-2 text-xs font-bold text-green-700">
                          <CheckBadgeIcon className="w-5 h-5 text-green-500" /> Terdaftar ({r.jumlah_dokumen} Dokumen)
                        </span>
                      ) : (
                        <span className="flex items-center gap-2 text-xs font-bold text-red-600">
                          <ExclamationTriangleIcon className="w-5 h-5" /> Tidak Terdaftar
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </section>

      </div>
    </AdminLayout>
  );
}
