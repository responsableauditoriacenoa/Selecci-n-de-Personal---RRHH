import { api } from "./api";
import type { DashboardMetrics } from "../types";

export const dashboardService = {
  getMetrics: async () => (await api.get<DashboardMetrics>("/reports/dashboard")).data
};
