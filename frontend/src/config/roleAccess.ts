import type { UserRole } from "@/types";

/**
 * Per the SIH problem statement's role table:
 *   Admin: everything
 *   Transport Authority: fleet + GIS + analytics + reports
 *   Traffic Officer: traffic + incidents
 *   Maintenance Officer: road defects + infrastructure
 *   Analyst: analytics + reports
 *
 * Dashboard and Settings are available to every authenticated role — they're
 * the shared overview/account pages, not a role-specific capability.
 * AI Detection Lab / Video Analysis / Model Management are technical AI-ops
 * tools; scoped to Admin and Maintenance Officer (who own road-defect quality).
 *
 * This is enforced in two places: Sidebar.tsx hides links the role can't use,
 * and RoleRoute below redirects away if someone navigates to a hidden path
 * directly — RBAC should never rely on hiding a button alone.
 */
const ROLE_PAGES: Record<UserRole, string[]> = {
  ADMIN: [
    "/dashboard",
    "/fleet",
    "/gis",
    "/road-conditions",
    "/traffic",
    "/incidents",
    "/infrastructure",
    "/detection-lab",
    "/video-analysis",
    "/models",
    "/routes",
    "/reports",
    "/settings",
  ],
  TRANSPORT_AUTHORITY: [
    "/dashboard",
    "/fleet",
    "/gis",
    "/road-conditions",
    "/traffic",
    "/routes",
    "/reports",
    "/settings",
  ],
  TRAFFIC_OFFICER: ["/dashboard", "/traffic", "/incidents", "/settings"],
  MAINTENANCE_OFFICER: [
    "/dashboard",
    "/road-conditions",
    "/infrastructure",
    "/detection-lab",
    "/video-analysis",
    "/settings",
  ],
  ANALYST: ["/dashboard", "/traffic", "/routes", "/reports", "/settings"],
};

export function canAccess(role: UserRole | undefined, path: string): boolean {
  if (!role) return false;
  return ROLE_PAGES[role]?.includes(path) ?? false;
}

export function pagesFor(role: UserRole | undefined): string[] {
  if (!role) return [];
  return ROLE_PAGES[role] ?? [];
}
