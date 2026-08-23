/**
 * components/PdfModal.tsx — Modal preview PDF menggunakan iframe streaming
 */
import { Dialog, Transition } from "@headlessui/react";
import { Fragment } from "react";
import { X, Download, ExternalLink } from "lucide-react";

interface PdfModalProps {
  isOpen: boolean;
  onClose: () => void;
  previewUrl: string;
  title?: string;
  onDownload?: () => void;
}

export default function PdfModal({
  isOpen,
  onClose,
  previewUrl,
  title = "Preview Dokumen",
  onDownload,
}: PdfModalProps) {
  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        {/* Backdrop */}
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-150"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-200"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-150"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-4xl bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden flex flex-col"
                style={{ height: "90vh" }}>
                {/* Header */}
                <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                  <div>
                    <Dialog.Title className="font-semibold text-slate-800 dark:text-white text-sm">
                      {title}
                    </Dialog.Title>
                    <p className="text-xs text-slate-400 mt-0.5">Mode Preview — Buka di tab baru untuk tampilan penuh</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <a
                      href={previewUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 rounded-lg text-slate-500 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                      title="Buka di tab baru"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                    {onDownload && (
                      <button
                        onClick={onDownload}
                        className="flex items-center gap-2 px-3 py-2 bg-[#208C68] text-white text-sm rounded-lg hover:bg-[#14503C] transition-colors"
                      >
                        <Download className="w-4 h-4" />
                        Unduh
                      </button>
                    )}
                    <button
                      onClick={onClose}
                      className="p-2 rounded-lg text-slate-500 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* PDF Viewer via iframe */}
                <div className="flex-1 bg-slate-100 dark:bg-slate-950">
                  <iframe
                    src={`${previewUrl}#toolbar=0&navpanes=0`}
                    className="w-full h-full border-0"
                    title={title}
                  />
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
