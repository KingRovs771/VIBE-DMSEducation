/**
 * pages/dashboard.tsx — Dashboard portal siswa
 * Mengikuti token [DASHBOARD_PAGE], [STAT_CARDS], [DASHBOARD_CONTENT_GRID] dari DESIGN.md
 */
import Head from "next/head";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  FolderIcon,
  CheckCircleIcon,
  ClockIcon,
  AcademicCapIcon,
  BellIcon,
  ChevronRightIcon,
  EyeIcon,
  ArrowDownTrayIcon
} from "@heroicons/react/24/solid";
import {
  FolderIcon as FolderOutline,
  BellIcon as BellOutline,
  EyeIcon as EyeOutline,
  ArrowDownTrayIcon as ArrowDownOutline,
  UserIcon as UserOutline
} from "@heroicons/react/24/outline";
import { format } from "date-fns";
import { id as localeId } from "date-fns/locale";

import Layout from "@/components/Layout";
import { Skeleton } from "@/components/Skeleton";
import StatusBadge from "@/components/StatusBadge";
import { dokumenApi, profilApi, categoriesApi } from "@/lib/api";
import { useRequireAuth } from "@/hooks/useAuth";
import { useAuthStore } from "@/store/authStore";
import { useMemo } from "react";
import { clsx } from "clsx";

export default function DashboardPage() {
  const { isAuthenticated, mounted } = useRequireAuth();
  const { siswa } = useAuthStore();

  const { data: dokumenData, isLoading: dokLoading } = useQuery({
    queryKey: ["dokumen-saya"],
    queryFn: () => dokumenApi.getSaya().then(r => r.data),
    enabled: isAuthenticated,
    staleTime: 3 * 60 * 1000,
  });

  const { data: categoriesData } = useQuery({
    queryKey: ["categories"],
    queryFn: () => categoriesApi.getAll().then(r => r.data),
    enabled: isAuthenticated,
  });

  const categoryMap = useMemo(() => {
    const map: Record<string, string> = {
      rapor: "Rapor",
      raport: "Raport Akademik",
      ijazah: "Ijazah",
      khs: "KHS",
      transkrip_nilai: "Transkrip Nilai",
      sertifikat: "Sertifikat",
      surat_ket: "Surat Keterangan",
      surat_keterangan: "Surat Keterangan",
      lainnya: "Lainnya",
    };
    if (categoriesData) {
      categoriesData.forEach((c: any) => {
        map[c.name] = c.description || c.name;
      });
    }
    return map;
  }, [categoriesData]);

  const getJenisLabel = (jenis: string) => {
    if (categoryMap[jenis]) return categoryMap[jenis];
    return jenis
      .replace(/_/g, " ")
      .replace(/\b\w/g, c => c.toUpperCase());
  };
  if (!mounted || !isAuthenticated) return null;

  const dokumen: any[] = Array.isArray(dokumenData) ? dokumenData : (dokumenData?.items || []);
  const totalDok = Array.isArray(dokumenData) ? dokumenData.length : (dokumenData?.total || 0);
  const recentDok = dokumen.slice(0, 6);
  const approvedCount = dokumen.filter(d => d.status === "approved").length;
  const pendingCount = dokumen.filter(d => d.status === "pending_review").length;

  const greetingHour = new Date().getHours();
  const greeting = greetingHour < 11 ? "Selamat Pagi" : greetingHour < 15 ? "Selamat Siang" : greetingHour < 18 ? "Selamat Sore" : "Selamat Malam";

  return (
    <>
      <Head>
        <title>Dashboard Portal Siswa — DokumenSekolah</title>
        <meta name="description" content="Dashboard portal siswa DokumenSekolah" />
      </Head>
      <Layout>
        {/* Greeting Banner (Warna Brand Forest Green) */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative bg-gradient-to-r from-[#14503C] to-[#0A2E1F] rounded-[20px] p-6 lg:p-8 mb-6 overflow-hidden text-white shadow-md"
        >
          <div className="absolute right-0 top-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="absolute right-16 bottom-0 w-32 h-32 bg-white/5 rounded-full translate-y-1/2" />
          <div className="relative z-10">
            <p className="text-[#B8EAD9] text-xs font-semibold uppercase tracking-wider mb-1">{greeting}, 👋</p>
            <h2 className="text-2xl lg:text-3xl font-display font-extrabold mb-1">{siswa?.nama_lengkap || "Siswa"}</h2>
            <p className="text-white/70 text-sm font-medium">
              NIS: {siswa?.nis} {siswa?.kelas && `· Kelas ${siswa.kelas}`}
            </p>
          </div>
        </motion.div>

        {/* ── [STAT_CARDS] ── */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          
          {/* Card 1: Total Dokumen */}
          <div className="bg-[#DFF2EC] border border-black/5 rounded-[20px] p-5 shadow-sm hover:translate-y-[-2px] hover:shadow-md transition-all duration-200">
            <div className="flex justify-between items-start mb-4">
              <span className="text-[13px] font-semibold text-[#0F4C39]/70 uppercase tracking-wider">Total Dokumen</span>
              <div className="w-9 h-9 rounded-xl bg-black/5 flex items-center justify-center">
                <FolderIcon className="w-5 h-5 text-[#1A7A5E]" />
              </div>
            </div>
            <h3 className="text-3xl font-display font-extrabold text-[#0F4C39] leading-none mb-2">{totalDok}</h3>
            <span className="text-xs text-[#0F4C39]/65 font-medium">Dokumen terunggah</span>
          </div>

          {/* Card 2: Dokumen Disetujui */}
          <div className="bg-[#E0F0E0] border border-black/5 rounded-[20px] p-5 shadow-sm hover:translate-y-[-2px] hover:shadow-md transition-all duration-200">
            <div className="flex justify-between items-start mb-4">
              <span className="text-[13px] font-semibold text-[#14532D]/70 uppercase tracking-wider">Disetujui</span>
              <div className="w-9 h-9 rounded-xl bg-black/5 flex items-center justify-center">
                <CheckCircleIcon className="w-5 h-5 text-[#15803D]" />
              </div>
            </div>
            <h3 className="text-3xl font-display font-extrabold text-[#14532D] leading-none mb-2">{approvedCount}</h3>
            <span className="text-xs text-[#14532D]/65 font-medium">Siap diunduh</span>
          </div>

          {/* Card 3: Menunggu Review */}
          <div className="bg-[#FDE8D8] border border-black/5 rounded-[20px] p-5 shadow-sm hover:translate-y-[-2px] hover:shadow-md transition-all duration-200">
            <div className="flex justify-between items-start mb-4">
              <span className="text-[13px] font-semibold text-[#7A2D0F]/70 uppercase tracking-wider">Menunggu Review</span>
              <div className="w-9 h-9 rounded-xl bg-black/5 flex items-center justify-center">
                <ClockIcon className="w-5 h-5 text-[#C2410C]" />
              </div>
            </div>
            <h3 className="text-3xl font-display font-extrabold text-[#7A2D0F] leading-none mb-2">{pendingCount}</h3>
            <span className="text-xs text-[#7A2D0F]/65 font-medium">Dalam antrean verifikasi</span>
          </div>

          {/* Card 4: Angkatan */}
          <div className="bg-[#DDE9F8] border border-black/5 rounded-[20px] p-5 shadow-sm hover:translate-y-[-2px] hover:shadow-md transition-all duration-200">
            <div className="flex justify-between items-start mb-4">
              <span className="text-[13px] font-semibold text-[#1A3D6B]/70 uppercase tracking-wider">Angkatan</span>
              <div className="w-9 h-9 rounded-xl bg-black/5 flex items-center justify-center">
                <AcademicCapIcon className="w-5 h-5 text-[#2563EB]" />
              </div>
            </div>
            <h3 className="text-3xl font-display font-extrabold text-[#1A3D6B] leading-none mb-2">{siswa?.angkatan || "—"}</h3>
            <span className="text-xs text-[#1A3D6B]/65 font-medium">Tahun ajaran masuk</span>
          </div>

        </div>

        {/* ── [DASHBOARD_CONTENT_GRID] ── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 items-start">
          
          {/* PANEL KIRI (Tabel Dokumen Terbaru) */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white border border-neutral-200 rounded-[20px] p-5 shadow-sm">
              <div className="flex items-center justify-between mb-4 border-b border-neutral-100 pb-3">
                <div className="flex items-center gap-2">
                  <div className="w-[34px] h-[34px] bg-[#E0F5EE] rounded-xl flex items-center justify-center">
                    <FolderIcon className="w-[18px] h-[18px] text-[#14503C]" />
                  </div>
                  <h3 className="font-display font-bold text-neutral-950 text-sm">Dokumen Terbaru Saya</h3>
                </div>
                <Link href="/dokumen" className="text-xs font-semibold text-[#208C68] hover:text-[#14503C] transition-colors">
                  Lihat semua →
                </Link>
              </div>

              {/* [TABLE_COMPONENT] */}
              <div className="w-full overflow-hidden border border-neutral-200 rounded-xl">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="bg-neutral-50 border-b border-neutral-200">
                      <th className="text-[11px] font-bold uppercase tracking-wider text-neutral-400 px-4 py-2.5 text-left">Jenis</th>
                      <th className="text-[11px] font-bold uppercase tracking-wider text-neutral-400 px-4 py-2.5 text-left">Tahun Ajaran</th>
                      <th className="text-[11px] font-bold uppercase tracking-wider text-neutral-400 px-4 py-2.5 text-left">Tanggal</th>
                      <th className="text-[11px] font-bold uppercase tracking-wider text-neutral-400 px-4 py-2.5 text-left">Status</th>
                      <th className="text-[11px] font-bold uppercase tracking-wider text-neutral-400 px-4 py-2.5 text-right">Aksi</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dokLoading ? (
                      <tr>
                        <td colSpan={5} className="text-center py-8">
                          <div className="w-6 h-6 border-2 border-[#208C68] border-t-transparent rounded-full animate-spin mx-auto" />
                        </td>
                      </tr>
                    ) : recentDok.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="text-center py-12 text-neutral-400 text-xs font-semibold">
                          <FolderOutline className="w-10 h-10 mx-auto mb-2 opacity-30" />
                          Belum ada dokumen yang tersedia
                        </td>
                      </tr>
                    ) : (
                      recentDok.map((dok) => {
                        const isRapor = dok.jenis_dok?.toLowerCase().includes("rapor");
                        const isIjazah = dok.jenis_dok?.toLowerCase().includes("ijazah");
                        const isTranskrip = dok.jenis_dok?.toLowerCase().includes("transkrip");

                        return (
                          <tr key={dok.id} className="border-b border-neutral-100 hover:bg-[#F0FAF6] transition-colors duration-120 last:border-none">
                            <td className="px-4 py-3 whitespace-nowrap">
                              <span className={clsx(
                                "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-bold leading-normal",
                                isRapor && "bg-[#DFF2EC] text-[#0F4C39]",
                                isIjazah && "bg-[#FCEEDD] text-[#78350F]",
                                isTranskrip && "bg-[#EDE0F8] text-[#4A1D7A]",
                                !isRapor && !isIjazah && !isTranskrip && "bg-[#DDE9F8] text-[#1A3D6B]"
                              )}>
                                📄 {getJenisLabel(dok.jenis_dok)} {dok.semester && `— Sem ${dok.semester}`}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-sm text-neutral-700 font-semibold">{dok.tahun_ajaran}</td>
                            <td className="px-4 py-3 text-xs text-neutral-400 font-semibold">
                              {dok.created_at ? format(new Date(dok.created_at), "d MMM yyyy", { locale: localeId }) : "—"}
                            </td>
                            <td className="px-4 py-3">
                              <StatusBadge status={dok.status || "approved"} />
                            </td>
                            <td className="px-4 py-3 text-right">
                              <div className="flex justify-end gap-1.5">
                                <button className="w-[30px] h-[30px] bg-[#E0F5EE] hover:bg-[#B8EAD9] rounded-lg flex items-center justify-center text-[#14503C] transition-colors shadow-sm">
                                  <EyeOutline className="w-4 h-4" />
                                </button>
                                <button className="w-[30px] h-[30px] bg-[#EDE0F8] hover:bg-purple-200 rounded-lg flex items-center justify-center text-[#4A1D7A] transition-colors shadow-sm">
                                  <ArrowDownOutline className="w-4 h-4" />
                                </button>
                              </div>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* PANEL KANAN (Notifikasi & Aksi Cepat) */}
          <div className="space-y-6">
            
            {/* Notifikasi */}
            <div className="bg-white border border-neutral-200 rounded-[20px] p-5 shadow-sm">
              <div className="flex items-center gap-2 border-b border-neutral-100 pb-3 mb-4">
                <BellIcon className="w-5 h-5 text-[#D97706]" />
                <h3 className="font-display font-bold text-neutral-950 text-sm">Notifikasi</h3>
                <span className="ml-auto text-[10px] font-extrabold bg-[#FEF3C7] text-[#D97706] px-2 py-0.5 rounded-full uppercase">Baru</span>
              </div>
              <div className="text-center py-10 text-neutral-400 text-xs font-semibold px-4">
                <BellOutline className="w-10 h-10 mx-auto mb-2 opacity-25 text-neutral-400" />
                Semua aman! Tidak ada notifikasi baru.
              </div>
            </div>

            {/* Aksi Cepat */}
            <div className="bg-white border border-neutral-200 rounded-[20px] p-5 shadow-sm">
              <div className="flex items-center border-b border-neutral-100 pb-3 mb-4">
                <h3 className="font-display font-bold text-neutral-950 text-sm">Aksi Cepat</h3>
              </div>
              <div className="space-y-2">
                <Link href="/dokumen" className="flex items-center gap-2.5 p-3.5 bg-white border border-[#D4DDD9] rounded-xl hover:border-[#3DB891] hover:bg-[#F0FAF6] transition-all hover:translate-y-[-1px] group">
                  <div className="w-9 h-9 bg-[#DFF2EC] rounded-lg flex items-center justify-center">
                    <FolderIcon className="w-4 h-4 text-[#1A7A5E]" />
                  </div>
                  <span className="text-xs font-bold text-neutral-700">Lihat semua dokumen</span>
                  <ChevronRightIcon className="w-3.5 h-3.5 ml-auto text-neutral-400 group-hover:translate-x-0.5 transition-transform" />
                </Link>

                <Link href="/profil" className="flex items-center gap-2.5 p-3.5 bg-white border border-[#D4DDD9] rounded-xl hover:border-[#3DB891] hover:bg-[#F0FAF6] transition-all hover:translate-y-[-1px] group">
                  <div className="w-9 h-9 bg-[#DDE9F8] rounded-lg flex items-center justify-center">
                    <UserOutline className="w-4 h-4 text-[#2563EB]" />
                  </div>
                  <span className="text-xs font-bold text-neutral-700">Profil Saya</span>
                  <ChevronRightIcon className="w-3.5 h-3.5 ml-auto text-neutral-400 group-hover:translate-x-0.5 transition-transform" />
                </Link>
              </div>
            </div>

          </div>

        </div>

      </Layout>
    </>
  );
}
