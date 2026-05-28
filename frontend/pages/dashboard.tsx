import type { NextPage } from "next";
import Head from "next/head";
import { useState } from "react";
import {
  FileText, Upload, Search, Bell, Settings, LogOut,
  Home, FolderOpen, Users, BarChart3, ChevronDown,
  File, Clock, CheckCircle, AlertCircle, TrendingUp,
} from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";
import { useAuthStore } from "@/store/authStore";
import { useDocuments } from "@/hooks/useDocuments";

const stats = [
  { label: "Total Dokumen", value: "1,247", icon: FileText, change: "+12%", color: "text-blue-400" },
  { label: "Upload Bulan Ini", value: "89", icon: Upload, change: "+24%", color: "text-emerald-400" },
  { label: "Menunggu Review", value: "14", icon: Clock, change: "-3%", color: "text-amber-400" },
  { label: "Disetujui", value: "1,102", icon: CheckCircle, change: "+8%", color: "text-green-400" },
];

const navItems = [
  { href: "/dashboard", icon: Home, label: "Dashboard" },
  { href: "/dashboard/documents", icon: FolderOpen, label: "Dokumen" },
  { href: "/dashboard/upload", icon: Upload, label: "Upload" },
  { href: "/dashboard/users", icon: Users, label: "Pengguna" },
  { href: "/dashboard/analytics", icon: BarChart3, label: "Analitik" },
  { href: "/dashboard/settings", icon: Settings, label: "Pengaturan" },
];

const DashboardPage: NextPage = () => {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const [searchQuery, setSearchQuery] = useState("");
  const { data: documents, isLoading } = useDocuments({ query: searchQuery, size: 5 });

  return (
    <>
      <Head>
        <title>Dashboard — DMS Sekolah</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      </Head>

      <div className="flex h-screen bg-slate-950 font-sans text-white overflow-hidden">
        {/* ── Sidebar ── */}
        <aside className="flex w-64 flex-col border-r border-slate-800 bg-slate-900">
          {/* Logo */}
          <div className="flex h-16 items-center gap-3 border-b border-slate-800 px-6">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600">
              <FileText className="h-4 w-4" />
            </div>
            <span className="font-bold">DMS Sekolah</span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 overflow-y-auto p-4">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-400 transition hover:bg-slate-800 hover:text-white"
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            ))}
          </nav>

          {/* User */}
          <div className="border-t border-slate-800 p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-600 text-sm font-bold">
                {user?.full_name?.[0] ?? "U"}
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">{user?.full_name ?? "User"}</p>
                <p className="truncate text-xs text-slate-500 capitalize">{user?.role ?? "—"}</p>
              </div>
              <button onClick={logout} className="text-slate-500 hover:text-red-400 transition-colors">
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          </div>
        </aside>

        {/* ── Main Content ── */}
        <div className="flex flex-1 flex-col overflow-hidden">
          {/* Header */}
          <header className="flex h-16 items-center justify-between border-b border-slate-800 bg-slate-900/50 px-8">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                placeholder="Cari dokumen..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-80 rounded-lg border border-slate-700 bg-slate-800 py-2 pl-9 pr-4 text-sm placeholder-slate-500 outline-none focus:border-primary-500 transition"
              />
            </div>
            <div className="flex items-center gap-3">
              <button className="relative rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white transition">
                <Bell className="h-5 w-5" />
                <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-red-500" />
              </button>
              <Link
                href="/dashboard/upload"
                className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium hover:bg-primary-700 transition"
              >
                <Upload className="h-4 w-4" />
                Upload
              </Link>
            </div>
          </header>

          {/* Body */}
          <main className="flex-1 overflow-y-auto p-8">
            {/* Welcome */}
            <div className="mb-8">
              <h1 className="text-2xl font-bold">
                Selamat datang, {user?.full_name?.split(" ")[0] ?? "User"} 👋
              </h1>
              <p className="mt-1 text-slate-400">
                Berikut ringkasan aktivitas dokumen hari ini.
              </p>
            </div>

            {/* Stats */}
            <div className="mb-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {stats.map((stat, i) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.08 }}
                  className="rounded-xl border border-slate-800 bg-slate-900 p-5"
                >
                  <div className="mb-3 flex items-center justify-between">
                    <span className="text-sm text-slate-400">{stat.label}</span>
                    <stat.icon className={`h-5 w-5 ${stat.color}`} />
                  </div>
                  <div className="flex items-end justify-between">
                    <span className="text-3xl font-bold">{stat.value}</span>
                    <span className={`text-sm font-medium ${stat.change.startsWith("+") ? "text-emerald-400" : "text-red-400"}`}>
                      {stat.change}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Recent Documents */}
            <div className="rounded-xl border border-slate-800 bg-slate-900">
              <div className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
                <h2 className="font-semibold">Dokumen Terbaru</h2>
                <Link href="/dashboard/documents" className="text-sm text-primary-400 hover:text-primary-300">
                  Lihat semua →
                </Link>
              </div>
              <div className="divide-y divide-slate-800">
                {isLoading ? (
                  <div className="py-12 text-center text-slate-500">Memuat...</div>
                ) : documents?.items?.length === 0 ? (
                  <div className="py-12 text-center text-slate-500">
                    Belum ada dokumen. <Link href="/dashboard/upload" className="text-primary-400">Upload sekarang</Link>
                  </div>
                ) : (
                  documents?.items?.map((doc) => (
                    <div key={doc.id} className="flex items-center gap-4 px-6 py-4 hover:bg-slate-800/50 transition">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-800">
                        <File className="h-5 w-5 text-primary-400" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="truncate font-medium">{doc.title}</p>
                        <p className="text-sm text-slate-500">
                          {(doc.file_size / 1024).toFixed(1)} KB • {doc.mime_type}
                        </p>
                      </div>
                      <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        doc.status === "approved" ? "bg-emerald-500/20 text-emerald-300" :
                        doc.status === "pending_review" ? "bg-amber-500/20 text-amber-300" :
                        "bg-slate-700 text-slate-400"
                      }`}>
                        {doc.status}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </main>
        </div>
      </div>
    </>
  );
};

export default DashboardPage;
