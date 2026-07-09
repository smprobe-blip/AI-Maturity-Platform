import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { KeycloakProvider } from '@/auth/KeycloakProvider';
import { ProtectedRoute } from '@/auth/ProtectedRoute';
import { ToastProvider } from '@/components/ui/Toast';
import { AdminLayout } from '@/components/layout/AdminLayout';

// Public
import Page1 from '@/pages/public/Page1';
import Page2 from '@/pages/public/Page2';
import Page3 from '@/pages/public/Page3';
import LoginPage from '@/pages/LoginPage';

// Admin
import DashboardPage from '@/pages/admin/DashboardPage';
import AuditsListPage from '@/pages/admin/AuditsListPage';
import AuditDetailPage from '@/pages/admin/AuditDetailPage';
import BenchmarksPage from '@/pages/admin/BenchmarksPage';
import ExportsPage from '@/pages/admin/ExportsPage';
import UsersPage from '@/pages/admin/UsersPage';
import SettingsPage from '@/pages/admin/SettingsPage';
import AuditLogPage from '@/pages/admin/AuditLogPage';
import AnalyticsPage from '@/pages/admin/AnalyticsPage';
import LeadsPage from '@/pages/admin/leads/LeadsPage';
import ReportsPage from '@/pages/admin/reports/ReportsPage';
import ProfilePage from '@/pages/admin/profile/ProfilePage';
import MailingsPage from '@/pages/admin/mailings/MailingsPage';
import RadarPage from '@/pages/admin/radar/RadarPage';

function App() {
  return (
    <KeycloakProvider>
      <BrowserRouter>
        <ToastProvider />
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Page1 />} />
          <Route path="/assessment" element={<Page2 />} />
          <Route path="/results/:auditId" element={<Page3 />} />
          <Route path="/login" element={<LoginPage />} />

          {/* Admin routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute requiredRoles={['super_admin', 'facilitator', 'analyst', 'sales', 'auditor']}>
                <AdminLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="audits" element={<AuditsListPage />} />
            <Route path="audits/:auditId" element={<AuditDetailPage />} />
            <Route path="benchmarks" element={<BenchmarksPage />} />
            <Route path="exports" element={<ExportsPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="leads" element={<LeadsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="mailings" element={<MailingsPage />} />
            <Route path="radar" element={<RadarPage />} />
            <Route path="users" element={<ProtectedRoute requiredRoles={['super_admin']}><UsersPage /></ProtectedRoute>} />
            <Route path="settings" element={<ProtectedRoute requiredRoles={['super_admin']}><SettingsPage /></ProtectedRoute>} />
            <Route path="audit-log" element={<ProtectedRoute requiredRoles={['super_admin']}><AuditLogPage /></ProtectedRoute>} />
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </KeycloakProvider>
  );
}

export default App;
