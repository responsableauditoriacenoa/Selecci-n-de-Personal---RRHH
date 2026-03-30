import { api } from "./api";
import type { ApplicationSummary, Vacancy } from "../types";

export const vacancyService = {
  list: async () => (await api.get<Vacancy[]>("/vacancies")).data,
  detail: async (id: string) => (await api.get(`/vacancies/${id}`)).data,
  create: async (payload: Record<string, unknown>, descriptivoFile?: File | null) => {
    const formData = new FormData();
    Object.entries(payload).forEach(([key, value]) => formData.append(key, String(value)));
    if (descriptivoFile) {
      formData.append("descriptivo_file", descriptivoFile);
    }
    return (await api.post("/vacancies", formData, { headers: { "Content-Type": "multipart/form-data" } })).data;
  },
  update: async (id: string, payload: Record<string, unknown>, descriptivoFile?: File | null) => {
    const formData = new FormData();
    Object.entries(payload).forEach(([key, value]) => formData.append(key, String(value)));
    if (descriptivoFile) {
      formData.append("descriptivo_file", descriptivoFile);
    }
    return (
      await api.put(`/vacancies/${id}`, formData, { headers: { "Content-Type": "multipart/form-data" } })
    ).data;
  },
  applications: async (id: string) => (await api.get<ApplicationSummary[]>(`/vacancies/${id}/applications`)).data,
  qr: async (id: string) => (await api.get(`/vacancies/${id}/qr`)).data,
  viewProfileDocument: async (id: string) => {
    const response = await api.get(`/vacancies/${id}/profile-document?disposition=inline`, { responseType: "blob" });
    const url = window.URL.createObjectURL(response.data);
    window.open(url, "_blank", "noopener,noreferrer");
    setTimeout(() => window.URL.revokeObjectURL(url), 30000);
  },
  downloadProfileDocument: async (id: string) => {
    const response = await api.get(`/vacancies/${id}/profile-document?disposition=attachment`, { responseType: "blob" });
    const contentDisposition = response.headers["content-disposition"] as string | undefined;
    const filenameMatch = contentDisposition?.match(/filename="?([^";]+)"?/i);
    const filename = filenameMatch?.[1] || `descriptivo_vacante_${id}`;
    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
};
