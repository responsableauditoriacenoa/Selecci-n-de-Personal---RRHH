import { api } from "./api";
import type { JobProfile } from "../types";

export const jobProfileService = {
  list: async () => (await api.get<JobProfile[]>("/job-profiles")).data,
  detail: async (id: string) => (await api.get(`/job-profiles/${id}`)).data,
  create: async (payload: unknown) => (await api.post("/job-profiles", payload)).data,
  update: async (id: string, payload: unknown) => (await api.put(`/job-profiles/${id}`, payload)).data,
  analyzeDocument: async (id: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return (
      await api.post(`/job-profiles/${id}/analyze-document`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      })
    ).data;
  }
};
