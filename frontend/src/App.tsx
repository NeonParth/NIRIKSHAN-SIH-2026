import { Route, Routes } from "react-router-dom";
import { AppShell } from "./components/Navigation/AppShell";
import { AuthProvider } from "./context/AuthContext";
import { DashboardPage } from "./pages/DashboardPage";
import { InvestigationPage } from "./pages/InvestigationPage";
import { LoginPage } from "./pages/LoginPage";
import { ProjectDetailPage } from "./pages/ProjectDetailPage";
import { ProjectsPage } from "./pages/ProjectsPage";
import { RiskAnalysisPage } from "./pages/RiskAnalysisPage";
import { RiskMapPage } from "./pages/RiskMapPage";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<AppShell />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
          <Route path="/risks" element={<RiskAnalysisPage />} />
          <Route path="/map" element={<RiskMapPage />} />
          <Route path="/investigation" element={<InvestigationPage />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}
