import type { NextPage } from "next";
import Head from "next/head";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  FileText, Shield, Search, Upload, Users, BarChart3,
  ArrowRight, CheckCircle,
} from "lucide-react";

const features = [
  {
    icon: Upload,
    title: "Upload & Kelola Dokumen",
    desc: "Upload PDF, Word, Excel dengan mudah. Dokumen tersimpan aman di MinIO.",
    color: "from-blue-500 to-cyan-500",
  },
  {
    icon: Shield,
    title: "NeuralKeyGen Security",
    desc: "Setiap dokumen memiliki kunci unik yang dihasilkan neural network.",
    color: "from-violet-500 to-purple-500",
  },
  {
    icon: Search,
    title: "Pencarian Cerdas",
    desc: "Full-text search dengan OCR. Cari isi dokumen PDF & gambar.",
    color: "from-orange-500 to-amber-500",
  },
  {
    icon: Users,
    title: "Manajemen Peran",
    desc: "Admin, Guru, Staf, Siswa — setiap peran memiliki akses yang tepat.",
    color: "from-emerald-500 to-green-500",
  },
  {
    icon: BarChart3,
    title: "Dashboard Analitik",
    desc: "Pantau statistik dokumen, aktivitas pengguna, dan audit log.",
    color: "from-pink-500 to-rose-500",
  },
  {
    icon: CheckCircle,
    title: "Alur Persetujuan",
    desc: "Dokumen melalui alur review dan persetujuan sebelum dipublikasikan.",
    color: "from-teal-500 to-cyan-500",
  },
];

const Home: NextPage = () => {
  return (
    <>
      <Head>
        <title>DMS Sekolah — Sistem Manajemen Dokumen Pendidikan</title>
        <meta
          name="description"
          content="Platform digital untuk pengelolaan dokumen sekolah yang aman, terorganisir, dan mudah diakses oleh seluruh civitas sekolah."
        />
        <link rel="icon" href="/favicon.ico" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      </Head>

      <div className="min-h-screen bg-slate-950 text-white font-sans">
        {/* ── Navbar ── */}
        <nav className="fixed top-0 z-50 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600">
                <FileText className="h-4 w-4" />
              </div>
              <span className="text-lg font-bold">DMS Sekolah</span>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/login" className="text-sm text-slate-400 hover:text-white transition-colors">
                Masuk
              </Link>
              <Link
                href="/register"
                className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium hover:bg-primary-700 transition-colors"
              >
                Mulai Sekarang
              </Link>
            </div>
          </div>
        </nav>

        {/* ── Hero ── */}
        <section className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-6 pt-20">
          {/* Background gradient orbs */}
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-primary-600/30 blur-3xl" />
            <div className="absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-violet-600/20 blur-3xl" />
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="relative text-center"
          >
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary-500/30 bg-primary-500/10 px-4 py-2 text-sm text-primary-300">
              <span className="h-2 w-2 rounded-full bg-primary-400 animate-pulse" />
              Platform DMS Modern untuk Sekolah Indonesia
            </div>

            <h1 className="mb-6 text-5xl font-bold leading-tight md:text-7xl">
              Dokumen Sekolah{" "}
              <span className="bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent">
                Lebih Teratur
              </span>
            </h1>

            <p className="mx-auto mb-10 max-w-2xl text-lg text-slate-400">
              Kelola semua dokumen sekolah — SK, surat, laporan, dan lebih banyak lagi —
              dalam satu platform yang aman, cerdas, dan mudah digunakan.
            </p>

            <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <Link
                href="/dashboard"
                className="flex items-center gap-2 rounded-xl bg-primary-600 px-8 py-4 font-semibold hover:bg-primary-700 transition-all hover:scale-105"
              >
                Buka Dashboard
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/login"
                className="flex items-center gap-2 rounded-xl border border-slate-700 px-8 py-4 font-semibold text-slate-300 hover:border-slate-600 hover:text-white transition-all"
              >
                Login
              </Link>
            </div>
          </motion.div>
        </section>

        {/* ── Features ── */}
        <section className="mx-auto max-w-7xl px-6 py-24">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-4xl font-bold">Fitur Unggulan</h2>
            <p className="text-slate-400">Semua yang dibutuhkan untuk manajemen dokumen modern</p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                viewport={{ once: true }}
                className="group rounded-2xl border border-slate-800 bg-slate-900/50 p-6 hover:border-slate-700 transition-all hover:-translate-y-1"
              >
                <div className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${f.color}`}>
                  <f.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="mb-2 text-lg font-semibold">{f.title}</h3>
                <p className="text-sm text-slate-400">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* ── Footer ── */}
        <footer className="border-t border-slate-800 py-8 text-center text-sm text-slate-500">
          <p>© 2024 DMS Sekolah. Dibangun dengan FastAPI + Next.js + PyTorch</p>
        </footer>
      </div>
    </>
  );
};

export default Home;
