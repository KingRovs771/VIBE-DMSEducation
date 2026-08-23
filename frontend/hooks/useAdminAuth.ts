/**
 * hooks/useAdminAuth.ts — Custom hook untuk guard autentikasi halaman admin
 */
import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { useAdminAuthStore } from "@/store/adminAuthStore";

export function useRequireAdmin() {
  const router = useRouter();
  const { isAdminAuthenticated } = useAdminAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted && !isAdminAuthenticated) {
      router.replace("/admin/login");
    }
  }, [mounted, isAdminAuthenticated, router]);

  return { isAdminAuthenticated, mounted };
}

export function useRedirectIfAdmin() {
  const router = useRouter();
  const { isAdminAuthenticated } = useAdminAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted && isAdminAuthenticated) {
      router.replace("/admin/dashboard");
    }
  }, [mounted, isAdminAuthenticated, router]);
}
