import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Admin, AdminRole } from "@/types";

interface AuthState {
  admin: Admin | null;
  token: string | null;
  isAuthenticated: boolean;
  _hasHydrated: boolean;
  setHasHydrated: (state: boolean) => void;
  setAuth: (admin: Admin, token: string) => void;
  logout: () => void;
  hasRole: (roles: AdminRole[]) => boolean;
  isSuperAdmin: () => boolean;
  isAdminOrAbove: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      admin: null,
      token: null,
      isAuthenticated: false,
      _hasHydrated: false,

      setHasHydrated: (state: boolean) => {
        set({ _hasHydrated: state });
      },

      setAuth: (admin: Admin, token: string) => {
        localStorage.setItem("admin_token", token);
        set({ admin, token, isAuthenticated: true });
      },

      logout: () => {
        localStorage.removeItem("admin_token");
        set({ admin: null, token: null, isAuthenticated: false });
      },

      hasRole: (roles: AdminRole[]) => {
        const { admin } = get();
        return admin ? roles.includes(admin.role) : false;
      },

      isSuperAdmin: () => {
        const { admin } = get();
        return admin?.role === "super_admin";
      },

      isAdminOrAbove: () => {
        const { admin } = get();
        return admin?.role === "super_admin" || admin?.role === "admin";
      },
    }),
    {
      name: "admin-auth",
      partialize: (state) => ({
        admin: state.admin,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);
