/**
 * components/Layout.tsx — Layout utama portal siswa (Sidebar-Only layout)
 * Mengikuti spesifikasi [SIDEBAR], [TYPOGRAPHY], dan [COLORS] dari DESIGN.md
 */
import { ReactNode, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import {
  HomeIcon,
  FolderIcon,
  UserIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  ShieldCheckIcon
} from "@heroicons/react/24/solid";
import { useAuthStore } from "@/store/authStore";
import { authApi } from "@/lib/api";
import toast from "react-hot-toast";
import { clsx } from "clsx";

const navItems = [
  { href: "/dashboard", icon: HomeIcon, label: "Dashboard", section: "MENU UTAMA" },
  { href: "/dokumen", icon: FolderIcon, label: "Dokumen Saya", section: "MENU UTAMA" },
  { href: "/profil", icon: UserIcon, label: "Profil Saya", section: "MENU UTAMA" },
];

interface LayoutProps {
  children: ReactNode;
  title?: string;
}

export default function Layout({ children, title }: LayoutProps) {
  const router = useRouter();
  const { siswa, logout } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch { /* silent */ }
    logout();
    toast.success("Berhasil keluar dari portal siswa!");
    router.push("/login");
  };

  const Sidebar = () => (
    <div className="flex flex-col h-full bg-[#0F3D29] select-none text-white font-body">
      {/* Top Logo & Branding */}
      <div className="p-5 border-b border-white/5 flex items-center gap-3">
        <div className="w-9 h-9 flex-shrink-0 bg-white rounded-lg flex items-center justify-center overflow-hidden shadow-lg shadow-[#3DB891]/20 p-1">
          <Image src="/Logo DS.png" alt="DokumenSekolah" width={32} height={32} className="rounded-md" priority />
        </div>
        <div>
          <span className="font-display font-extrabold text-white text-[13px] leading-tight block tracking-tight">DokumenSekolah</span>
          <span className="text-[9px] font-bold text-[#7AD4B8] uppercase tracking-widest">Portal Siswa</span>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 px-3 py-6 space-y-5">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-widest text-white/30 px-3 mb-2 font-body">MENU UTAMA</p>
          <div className="space-y-1">
            {navItems.map((item) => {
              const isActive = router.pathname === item.href;
              return (
                <Link key={item.href} href={item.href} onClick={() => setSidebarOpen(false)} className="block relative">
                  <div className={clsx(
                    "flex items-center gap-2.5 px-3 py-2.5 rounded-xl transition-all duration-150 group cursor-pointer font-body relative",
                    isActive
                      ? "bg-white/10 text-[#7AD4B8] font-bold"
                      : "text-white/60 hover:bg-white/5 hover:text-white"
                  )}>
                    {isActive && (
                      <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-6 bg-[#3DB891] rounded-r-sm" />
                    )}
                    <item.icon className={clsx("w-5 h-5 flex-shrink-0 transition-transform group-hover:scale-105", isActive ? "text-[#3DB891]" : "text-white/65")} />
                    <span className="text-[13px]">{item.label}</span>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Bottom Status, Profile & Logout */}
      <div className="p-4 border-t border-white/5 space-y-4 bg-black/10">
        {/* Profile Info */}
        <div className="flex items-center gap-3 px-1">
          <div className="w-9 h-9 rounded-full bg-[#208C68] flex items-center justify-center text-white font-display font-extrabold text-xs shadow border border-white/10 shrink-0">
            {siswa?.nama_lengkap?.charAt(0).toUpperCase() || "S"}
          </div>
          <div className="min-w-0">
            <p className="text-xs font-bold text-white truncate">{siswa?.nama_lengkap || "Siswa"}</p>
            <p className="text-[9px] text-[#7AD4B8] font-bold uppercase">Siswa Aktif</p>
          </div>
        </div>

        {/* Status Indicator */}
        <div className="flex items-center gap-2 px-1 text-white/40 text-[10px] font-bold">
          <div className="w-2 h-2 rounded-full bg-[#15803D] animate-pulse-dot" />
          <span>Sistem Online</span>
        </div>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="flex items-center gap-2.5 w-full px-3 py-2 rounded-xl text-white/50 hover:bg-red-500/10 hover:text-red-400 transition-all duration-150 group font-bold text-left text-xs"
        >
          <ArrowRightOnRectangleIcon className="w-4 h-4 group-hover:scale-105 transition-transform" />
          <span>Keluar</span>
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#F5F8F7] text-[#1F2421] flex flex-col lg:flex-row font-body">
      
      {/* ── MOBILE HEADER (lg:hidden) ── */}
      <header className="lg:hidden h-[50px] bg-[#14503C] px-4 flex items-center justify-between shadow z-35 shrink-0">
        <button
          onClick={() => setSidebarOpen(true)}
          className="p-1.5 rounded-lg text-white/70 hover:bg-white/10"
        >
          <Bars3Icon className="w-5 h-5" />
        </button>
        <span className="font-display font-extrabold text-white text-sm">DokumenSekolah</span>
        <div className="w-7 h-7 rounded-full bg-[#208C68] flex items-center justify-center text-white font-display font-extrabold text-[10px] border border-white/10 shadow shrink-0">
          {siswa?.nama_lengkap?.charAt(0).toUpperCase() || "S"}
        </div>
      </header>

      {/* ── DESKTOP SIDEBAR (lg:block) ── */}
      <aside className="hidden lg:block w-[220px] h-screen sticky top-0 shrink-0 z-30 shadow-sm border-r border-[#D4DDD9]/65">
        <Sidebar />
      </aside>

      {/* ── MOBILE DRAWER OVERLAY ── */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="lg:hidden fixed inset-0 bg-[#0A2E1F]/60 backdrop-blur-xs z-45"
              onClick={() => setSidebarOpen(false)}
            />
            <motion.div
              initial={{ x: -220 }}
              animate={{ x: 0 }}
              exit={{ x: -220 }}
              transition={{ type: "spring", damping: 30, stiffness: 350 }}
              className="lg:hidden fixed inset-y-0 left-0 w-[220px] z-50 shadow-2xl"
            >
              <div className="relative h-full flex flex-col">
                <button
                  onClick={() => setSidebarOpen(false)}
                  className="absolute top-4 right-4 z-50 p-1.5 rounded-lg text-white/50 hover:text-white"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
                <Sidebar />
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* ── MAIN CONTENT AREA ── */}
      <div className="flex-1 flex flex-col min-w-0 min-h-screen">
        <main className="flex-1 p-6 lg:p-8 max-w-7xl mx-auto w-full">
          {title && (
            <div className="mb-6">
              <h1 className="text-3xl font-display font-extrabold text-neutral-950 tracking-tight">{title}</h1>
            </div>
          )}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.22 }}
          >
            {children}
          </motion.div>
        </main>

        {/* ── FOOTER ── */}
        <footer className="border-t border-[#D4DDD9] py-5 text-center bg-white/40 mt-auto">
          <p className="text-[11px] font-medium tracking-wide text-neutral-400">
            © 2026 DokumenSekolah · Powered by NeuralKeyGen
          </p>
        </footer>
      </div>

    </div>
  );
}
