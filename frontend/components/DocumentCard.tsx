/**
 * DocumentCard component
 */
import { motion } from "framer-motion";
import { File, Download, Trash2, Clock, CheckCircle, XCircle, Eye } from "lucide-react";
import { Document } from "@/hooks/useDocuments";

interface DocumentCardProps {
  doc: Document;
  onDelete?: (id: number) => void;
  onDownload?: (id: number) => void;
  delay?: number;
}

const statusConfig = {
  approved: { icon: CheckCircle, color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/20", label: "Disetujui" },
  pending_review: { icon: Clock, color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/20", label: "Review" },
  rejected: { icon: XCircle, color: "text-red-400", bg: "bg-red-500/10 border-red-500/20", label: "Ditolak" },
  draft: { icon: File, color: "text-slate-400", bg: "bg-slate-700/50 border-slate-700", label: "Draft" },
  archived: { icon: File, color: "text-slate-500", bg: "bg-slate-800 border-slate-700", label: "Arsip" },
} as const;

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("id-ID", {
    day: "numeric", month: "short", year: "numeric",
  });
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentCard({ doc, onDelete, onDownload, delay = 0 }: DocumentCardProps) {
  const status = statusConfig[doc.status as keyof typeof statusConfig] ?? statusConfig.draft;
  const StatusIcon = status.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="group rounded-xl border border-slate-800 bg-slate-900 p-5 transition hover:border-slate-700 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-black/20"
    >
      <div className="mb-4 flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-600/20">
            <File className="h-5 w-5 text-primary-400" />
          </div>
          <div className="min-w-0">
            <h3 className="truncate font-semibold text-white">{doc.title}</h3>
            <p className="text-xs text-slate-500">{doc.original_filename}</p>
          </div>
        </div>
        <span className={`flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium ${status.bg} ${status.color}`}>
          <StatusIcon className="h-3 w-3" />
          {status.label}
        </span>
      </div>

      {doc.description && (
        <p className="mb-3 line-clamp-2 text-sm text-slate-400">{doc.description}</p>
      )}

      {/* Tags */}
      {doc.tags?.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-1.5">
          {doc.tags.slice(0, 4).map((tag) => (
            <span key={tag} className="rounded-full bg-slate-800 px-2.5 py-0.5 text-xs text-slate-400">
              #{tag}
            </span>
          ))}
        </div>
      )}

      {/* Meta */}
      <div className="mb-4 flex items-center gap-3 text-xs text-slate-600">
        <span>{formatSize(doc.file_size)}</span>
        <span>•</span>
        <span>{formatDate(doc.created_at)}</span>
        <span>•</span>
        <span className="font-mono">v{doc.version}</span>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => onDownload?.(doc.id)}
          className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-slate-700 py-2 text-sm text-slate-400 transition hover:border-primary-500 hover:text-primary-300"
        >
          <Download className="h-4 w-4" />
          Download
        </button>
        {onDelete && (
          <button
            onClick={() => onDelete(doc.id)}
            className="rounded-lg border border-slate-700 p-2 text-slate-500 transition hover:border-red-500/50 hover:text-red-400"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        )}
      </div>
    </motion.div>
  );
}
