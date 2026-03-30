import { api } from "./api";

export const applicationService = {
  detail: async (id: string) => (await api.get(`/applications/${id}`)).data,
  recalculate: async (id: string) => (await api.post(`/applications/${id}/recalculate-score`)).data,
  changeStatus: async (id: string, estado: string) =>
    (await api.post(`/applications/${id}/change-status`, { estado })).data,
  addNote: async (id: string, comentario: string) =>
    (await api.post(`/applications/${id}/notes`, { comentario })).data,
  viewCv: async (id: string) => {
    const response = await api.get(`/applications/${id}/cv?disposition=inline`, { responseType: "blob" });
    const url = window.URL.createObjectURL(response.data);
    window.open(url, "_blank", "noopener,noreferrer");
    setTimeout(() => window.URL.revokeObjectURL(url), 30000);
  },
  downloadCv: async (id: string) => {
    const response = await api.get(`/applications/${id}/cv?disposition=attachment`, { responseType: "blob" });
    const contentDisposition = response.headers["content-disposition"] as string | undefined;
    const defaultName = `cv_postulacion_${id}`;
    const filenameMatch = contentDisposition?.match(/filename="?([^";]+)"?/i);
    const filename = filenameMatch?.[1] || defaultName;

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
