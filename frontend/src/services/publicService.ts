import { api } from "./api";

export const publicService = {
  vacancy: async (token: string) => (await api.get(`/public/vacancy/${token}`)).data,
  apply: async (formData: FormData) =>
    (await api.post("/public/intake", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    })).data
};
