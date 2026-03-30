import { Navigate, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "../components/ProtectedRoute";
import { useAuth, AuthProvider } from "../hooks/useAuth";
import { BackofficeLayout } from "../layouts/BackofficeLayout";
import { ApplicationDetailPage as CandidateDetail } from "../pages/admin/CandidateDetail";
import { DashboardPage as Dashboard } from "../pages/admin/Dashboard";
import { LoginPage as Login } from "../pages/admin/Login";
import { NotesPage as Notes } from "../pages/admin/Notes";
import { ScoreViewPage as ScoreView } from "../pages/admin/ScoreView";
import { StatusManagementPage as StatusManagement } from "../pages/admin/StatusManagement";
import { VacanciesListPage as Vacancies } from "../pages/admin/Vacancies";
import { VacancyApplicationsPage as VacancyApplications } from "../pages/admin/VacancyApplications";
import { VacancyDetailPage as VacancyDetail } from "../pages/admin/VacancyDetail";
import { VacancyFormPage as VacancyForm } from "../pages/admin/VacancyForm";
import { NotFoundPage } from "../pages/NotFoundPage";
import { PublicApplicationPage as ApplyForm } from "../pages/public/ApplyForm";
import { PublicConfirmationPage as ApplySuccess } from "../pages/public/ApplySuccess";
import { PublicVacancyPage as VacancyLanding } from "../pages/public/VacancyLanding";

const RootRedirect = () => {
  const { user, loading } = useAuth();
  if (loading) return <div className="public-wrap">Cargando...</div>;
  return <Navigate to={user ? "/" : "/login"} replace />;
};

const ProtectedShell = () => (
  <ProtectedRoute>
    <BackofficeLayout />
  </ProtectedRoute>
);

export const App = () => (
  <AuthProvider>
    <Routes>
      <Route path="/redirect" element={<RootRedirect />} />
      <Route path="/login" element={<Login />} />

      <Route element={<ProtectedShell />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/vacancies" element={<Vacancies />} />
        <Route path="/vacancies/new" element={<VacancyForm />} />
        <Route path="/vacancies/:id" element={<VacancyDetail />} />
        <Route path="/vacancies/:id/applications" element={<VacancyApplications />} />
        <Route path="/applications/:id" element={<CandidateDetail />} />
        <Route path="/applications/:id/score" element={<ScoreView />} />
        <Route path="/status" element={<StatusManagement />} />
        <Route path="/notes" element={<Notes />} />
      </Route>

      <Route path="/public/vacancy/:token" element={<VacancyLanding />} />
      <Route path="/public/apply/:token" element={<ApplyForm />} />
      <Route path="/public/confirmation" element={<ApplySuccess />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  </AuthProvider>
);
