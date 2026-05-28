/**
 * Document Upload Component dengan drag-and-drop
 */
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, X, File, CheckCircle, Loader2, AlertCircle } from "lucide-react";
import { useUploadDocument } from "@/hooks/useDocuments";

interface UploadZoneProps {
  onSuccess?: () => void;
}

const ACCEPTED_TYPES = {
  "application/pdf": [".pdf"],
  "application/msword": [".doc"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
  "application/vnd.ms-excel": [".xls"],
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
  "application/vnd.ms-powerpoint": [".ppt"],
  "application/vnd.openxmlformats-officedocument.presentationml.presentation": [".pptx"],
  "image/*": [".jpg", ".jpeg", ".png"],
  "text/plain": [".txt"],
};

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function UploadZone({ onSuccess }: UploadZoneProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [accessLevel, setAccessLevel] = useState("internal");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const { mutate: uploadDocument, isPending, isSuccess } = useUploadDocument();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setSelectedFile(file);
      if (!title) setTitle(file.name.replace(/\.[^.]+$/, ""));
    }
  }, [title]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const handleSubmit = () => {
    if (!selectedFile || !title) return;
    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("title", title);
    formData.append("description", description);
    formData.append("access_level", accessLevel);
    uploadDocument(formData, { onSuccess });
  };

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`relative cursor-pointer rounded-xl border-2 border-dashed p-10 text-center transition-all ${
          isDragActive
            ? "border-primary-500 bg-primary-500/10"
            : selectedFile
            ? "border-emerald-500 bg-emerald-500/10"
            : "border-slate-700 hover:border-slate-600 hover:bg-slate-800/50"
        }`}
      >
        <input {...getInputProps()} />
        <AnimatePresence mode="wait">
          {selectedFile ? (
            <motion.div
              key="file"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center gap-3"
            >
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500/20">
                <File className="h-7 w-7 text-emerald-400" />
              </div>
              <div>
                <p className="font-medium text-emerald-300">{selectedFile.name}</p>
                <p className="text-sm text-slate-500">{formatSize(selectedFile.size)}</p>
              </div>
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
                className="rounded-full p-1 text-slate-500 hover:text-red-400 transition"
              >
                <X className="h-4 w-4" />
              </button>
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center gap-3"
            >
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-800">
                <Upload className={`h-7 w-7 ${isDragActive ? "text-primary-400 animate-bounce" : "text-slate-500"}`} />
              </div>
              <div>
                <p className="font-medium text-slate-300">
                  {isDragActive ? "Lepaskan file di sini" : "Drag & drop file di sini"}
                </p>
                <p className="mt-1 text-sm text-slate-500">atau klik untuk memilih file (maks. 50MB)</p>
              </div>
              <p className="text-xs text-slate-600">PDF, Word, Excel, PowerPoint, Gambar, TXT</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Form fields */}
      {selectedFile && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="space-y-3"
        >
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Judul dokumen *"
            className="w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-3 text-sm text-white placeholder-slate-500 outline-none focus:border-primary-500"
          />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Deskripsi (opsional)"
            rows={2}
            className="w-full resize-none rounded-lg border border-slate-700 bg-slate-800 px-4 py-3 text-sm text-white placeholder-slate-500 outline-none focus:border-primary-500"
          />
          <select
            value={accessLevel}
            onChange={(e) => setAccessLevel(e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-3 text-sm text-white outline-none focus:border-primary-500"
          >
            <option value="public">Public — Semua orang</option>
            <option value="internal">Internal — Staf & Guru</option>
            <option value="confidential">Confidential — Admin</option>
            <option value="secret">Secret — Super Admin</option>
          </select>

          <button
            onClick={handleSubmit}
            disabled={isPending || !title}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary-600 py-3 font-semibold text-white transition hover:bg-primary-700 disabled:opacity-60"
          >
            {isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Mengunggah...
              </>
            ) : isSuccess ? (
              <>
                <CheckCircle className="h-4 w-4 text-emerald-300" />
                Berhasil Diunggah!
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                Upload Dokumen
              </>
            )}
          </button>
        </motion.div>
      )}
    </div>
  );
}
