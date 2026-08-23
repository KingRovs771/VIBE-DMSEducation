/**
 * components/StatusBadge.tsx — Badge status dokumen dengan warna semantik
 */
import { clsx } from "clsx";

const statusConfig: Record<string, { label: string; className: string; dot: string }> = {
  approved: {
    label: "Disetujui",
    className: "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-400 dark:border-emerald-700",
    dot: "bg-emerald-500",
  },
  pending_review: {
    label: "Menunggu",
    className: "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/20 dark:text-amber-400 dark:border-amber-700",
    dot: "bg-amber-500",
  },
  draft: {
    label: "Draft",
    className: "bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700",
    dot: "bg-slate-400",
  },
  rejected: {
    label: "Ditolak",
    className: "bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-700",
    dot: "bg-red-500",
  },
  archived: {
    label: "Diarsipkan",
    className: "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400 dark:border-blue-700",
    dot: "bg-blue-500",
  },
  expired: {
    label: "Kadaluarsa",
    className: "bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-900/20 dark:text-orange-400 dark:border-orange-700",
    dot: "bg-orange-500",
  },
};

export default function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] || statusConfig.draft;
  return (
    <span className={clsx(
      "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border",
      config.className
    )}>
      <span className={clsx("w-1.5 h-1.5 rounded-full flex-shrink-0", config.dot)} />
      {config.label}
    </span>
  );
}
