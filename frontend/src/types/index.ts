export type UserRole = "admin" | "rrhh" | "lider_solicitante";

export interface UserMe {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
}

export interface DashboardMetrics {
  total_vacancies: number;
  open_vacancies: number;
  total_applications: number;
  recommended_applications: number;
}

export interface JobProfile {
  id: number;
  nombre_puesto: string;
  seniority: string;
  modalidad: string;
  ubicacion: string;
  estado: string;
  version: number;
}

export interface Vacancy {
  id: number;
  job_profile_id?: number;
  company_id?: number;
  branch_id?: number;
  area_id?: number;
  empresa?: string;
  localidad?: string;
  area?: string;
  titulo_publicacion: string;
  descripcion_publicacion?: string;
  estado: string;
  fecha_apertura: string;
  fecha_cierre: string;
  public_url: string;
  qr_token?: string;
  descriptivo_archivo_nombre?: string | null;
  descriptivo_documento_cargado?: boolean;
}

export interface ApplicationSummary {
  id: number;
  estado: string;
  fecha_postulacion: string;
  candidate: {
    nombre: string;
    apellido: string;
    email: string;
  };
}
