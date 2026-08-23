/**
 * components/Skeleton.tsx — Reusable loading skeleton components
 */
import { clsx } from "clsx";

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div className={clsx("animate-pulse bg-slate-200 dark:bg-slate-700 rounded-lg", className)} />
  );
}

export function StatCardSkeleton() {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <Skeleton className="w-10 h-10 rounded-xl" />
        <Skeleton className="w-16 h-5 rounded-full" />
      </div>
      <Skeleton className="w-20 h-8 mb-2" />
      <Skeleton className="w-32 h-4" />
    </div>
  );
}

export function DocumentRowSkeleton() {
  return (
    <tr className="border-b border-slate-100 dark:border-slate-700">
      {[...Array(5)].map((_, i) => (
        <td key={i} className="px-4 py-4">
          <Skeleton className="h-4 w-full" />
        </td>
      ))}
    </tr>
  );
}

export function ProfileSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Skeleton className="w-20 h-20 rounded-full" />
        <div className="space-y-2">
          <Skeleton className="w-48 h-6" />
          <Skeleton className="w-32 h-4" />
        </div>
      </div>
      {[...Array(6)].map((_, i) => (
        <div key={i} className="space-y-1">
          <Skeleton className="w-24 h-4" />
          <Skeleton className="w-full h-10 rounded-xl" />
        </div>
      ))}
    </div>
  );
}
