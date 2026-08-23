import { useState, useEffect } from "react";
import Head from "next/head";
import AdminLayout from "@/components/AdminLayout";
import { adminAnomaliApi } from "@/lib/api";
import { 
  ShieldExclamationIcon, 
  ArrowPathIcon,
  ExclamationTriangleIcon
} from "@heroicons/react/24/outline";
import { ShieldCheckIcon } from "@heroicons/react/24/solid";
import toast from "react-hot-toast";

interface AuditLogResponse {
  id: number;
  admin_id: number | null;
  siswa_id: number | null;
  action: string;
  endpoint: string | null;
  http_method: string | null;
  detail: Record<string, any> | null;
  ip_address: string;
  user_agent: string;
  created_at: string;
}

export default function AnomaliDashboard() {
  const [alerts, setAlerts] = useState<AuditLogResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());

  const fetchAlerts = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    try {
      const response = await adminAnomaliApi.getAlerts();
      setAlerts(response.data);
      setLastRefreshed(new Date());
    } catch (err) {
      toast.error("Gagal mengambil data anomali");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchAlerts(true);
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const getBadgeColor = (action: string) => {
    if (action === "ANOMALY_CRITICAL") return "bg-red-100 text-red-700 border-red-200";
    if (action === "ANOMALY_WARNING") return "bg-yellow-100 text-yellow-700 border-yellow-200";
    return "bg-neutral-100 text-neutral-700 border-neutral-200";
  };

  const getIcon = (action: string) => {
    if (action === "ANOMALY_CRITICAL") return <ShieldExclamationIcon className="w-5 h-5 text-red-500" />;
    return <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />;
  };

  // Stats calculation
  const criticalCount = alerts.filter(a => a.action === "ANOMALY_CRITICAL").length;
  const warningCount = alerts.filter(a => a.action === "ANOMALY_WARNING").length;

  return (
    <AdminLayout title="Deteksi Anomali">
      <Head>
        <title>Deteksi Anomali - Admin Portal</title>
      </Head>

      <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
        
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-display font-extrabold text-[#0A2E1F] tracking-tight flex items-center gap-2">
              <ShieldCheckIcon className="w-8 h-8 text-[#208C68]" />
              Security & Anomaly Dashboard
            </h1>
            <p className="text-[#8FA39B] text-sm mt-1 font-body">
              Monitor aktivitas mencurigakan dan potensi ancaman secara real-time.
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <p className="text-[11px] text-[#8FA39B] font-medium">
              Update terakhir: {lastRefreshed.toLocaleTimeString('id-ID')}
            </p>
            <button 
              onClick={() => fetchAlerts(true)}
              disabled={refreshing}
              className="flex items-center gap-1.5 px-4 py-2 bg-white border border-[#D4DDD9] rounded-xl text-sm font-semibold text-[#14503C] hover:bg-neutral-50 transition-colors shadow-sm disabled:opacity-50"
            >
              <ArrowPathIcon className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-2xl p-5 border border-[#D4DDD9] shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-red-50 flex items-center justify-center border border-red-100">
              <ShieldExclamationIcon className="w-6 h-6 text-red-500" />
            </div>
            <div>
              <p className="text-[11px] font-bold text-[#8FA39B] uppercase tracking-wider">Critical Alerts</p>
              <p className="text-2xl font-display font-bold text-[#0A2E1F]">{criticalCount}</p>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-5 border border-[#D4DDD9] shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-yellow-50 flex items-center justify-center border border-yellow-100">
              <ExclamationTriangleIcon className="w-6 h-6 text-yellow-500" />
            </div>
            <div>
              <p className="text-[11px] font-bold text-[#8FA39B] uppercase tracking-wider">Warning Alerts</p>
              <p className="text-2xl font-display font-bold text-[#0A2E1F]">{warningCount}</p>
            </div>
          </div>

          <div className="bg-gradient-to-br from-[#14503C] to-[#0A2E1F] rounded-2xl p-5 border border-[#0A2E1F] shadow-md flex items-center gap-4 relative overflow-hidden">
             <div className="absolute top-0 right-0 p-4 opacity-10">
               <ShieldCheckIcon className="w-24 h-24 text-white" />
             </div>
            <div>
              <p className="text-[11px] font-bold text-[#7AD4B8] uppercase tracking-wider">Status Proteksi ML</p>
              <p className="text-xl font-display font-bold text-white mt-1">Aktif & Memantau</p>
            </div>
          </div>
        </div>

        {/* Alerts Table */}
        <div className="bg-white rounded-2xl border border-[#D4DDD9] shadow-sm overflow-hidden flex flex-col">
          <div className="px-5 py-4 border-b border-[#D4DDD9] bg-neutral-50/50 flex justify-between items-center">
             <h2 className="text-[13px] font-bold text-[#14503C] uppercase tracking-wide">Log Peringatan Terbaru</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-white border-b border-[#D4DDD9]">
                  <th className="px-5 py-3 text-[11px] font-bold text-[#8FA39B] uppercase tracking-wider">Waktu</th>
                  <th className="px-5 py-3 text-[11px] font-bold text-[#8FA39B] uppercase tracking-wider">Tingkat</th>
                  <th className="px-5 py-3 text-[11px] font-bold text-[#8FA39B] uppercase tracking-wider">Sumber IP</th>
                  <th className="px-5 py-3 text-[11px] font-bold text-[#8FA39B] uppercase tracking-wider">Aktivitas</th>
                  <th className="px-5 py-3 text-[11px] font-bold text-[#8FA39B] uppercase tracking-wider">Detail Skor ML</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100 font-body">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-5 py-8 text-center text-sm text-[#8FA39B]">
                      Memuat data anomali...
                    </td>
                  </tr>
                ) : alerts.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-5 py-12 text-center text-sm text-[#8FA39B]">
                      <ShieldCheckIcon className="w-10 h-10 text-[#3DB891]/30 mx-auto mb-3" />
                      Tidak ada anomali terdeteksi sejauh ini.
                    </td>
                  </tr>
                ) : (
                  alerts.map((alert) => (
                    <tr key={alert.id} className="hover:bg-neutral-50 transition-colors">
                      <td className="px-5 py-3 text-[13px] text-[#4A5D56] whitespace-nowrap">
                        {new Date(alert.created_at).toLocaleString('id-ID')}
                      </td>
                      <td className="px-5 py-3">
                        <div className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md border text-[11px] font-bold ${getBadgeColor(alert.action)}`}>
                          {getIcon(alert.action)}
                          {alert.action === "ANOMALY_CRITICAL" ? "CRITICAL" : "WARNING"}
                        </div>
                      </td>
                      <td className="px-5 py-3 text-[13px] text-[#14503C] font-mono">
                        {alert.ip_address || "N/A"}
                      </td>
                      <td className="px-5 py-3 text-[13px] text-[#4A5D56] font-mono">
                        {alert.http_method ? `[${alert.http_method}] ` : ""}{alert.endpoint || "—"}
                      </td>
                      <td className="px-5 py-3">
                         <div className="text-[12px] text-[#4A5D56]">
                            <span className="font-semibold">Skor: {alert.detail?.score?.toFixed(2) || "N/A"}</span>
                            {alert.detail?.reason && (
                              <span className="ml-2 text-[#8FA39B]">({alert.detail.reason})</span>
                            )}
                         </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </AdminLayout>
  );
}
