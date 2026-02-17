import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { SidebarProvider } from './contexts/SidebarContext.tsx';
import ProtectedRoute from './components/auth/ProtectedRoute.tsx';
import Layout from './components/layout/Layout.tsx';
// Auth pages
import LoginPage from './pages/auth/LoginPage.tsx';

// Course pages
import CoursesPage from './pages/courses/CoursesPage.tsx';
import CourseDetailPage from './pages/courses/CourseDetailPage.tsx';
import CreateModulePage from './pages/courses/CreateModulePage.tsx';
import ModuleDetailPage from './pages/courses/ModuleDetailPage.tsx';

// User pages
import UsersPage from './pages/users/UsersPage.tsx';
import CreateUserPage from './pages/users/CreateUserPage.tsx';
import EditUserPage from './pages/users/EditUserPage.tsx';
import UserGroupsPage from './pages/users/UserGroupsPage.tsx';
import UserGroupDetailPage from './pages/users/UserGroupDetailPage.tsx';
import UserCoursesPage from './pages/users/UserCoursesPage.tsx';
import UserProgressPage from './pages/users/UserProgressPage.tsx';

// Group pages
import GroupsPage from './pages/groups/GroupsPage.tsx';
import GroupDetailPage from './pages/groups/GroupDetailPage.tsx';

// Common pages
import HomePage from './pages/common/HomePage';
import UnauthorizedPage from './pages/common/UnauthorizedPage.tsx';
import './globals.css';

export default function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <SidebarProvider>
                    <Routes>
                        {/* Public routes */}
                        <Route path="/login" element={<LoginPage />} />

                        {/* Protected routes */}
                        <Route
                            path="/"
                            element={
                                <ProtectedRoute>
                                    <Layout>
                                        <HomePage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />

                        {/* Admin routes */}
                        <Route
                            path="/dashboard/courses"
                            element={
                                <ProtectedRoute requiredRole="admin">
                                    <Layout>
                                        <CoursesPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/courses/:courseId"
                            element={
                                <ProtectedRoute requiredRole="admin">
                                    <Layout>
                                        <CourseDetailPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/courses/:courseId/modules/new"
                            element={
                                <ProtectedRoute requiredRole="admin">
                                    <Layout>
                                        <CreateModulePage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/courses/:courseId/modules/:moduleId"
                            element={
                                <ProtectedRoute requiredRole="admin">
                                    <Layout>
                                        <ModuleDetailPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/users"
                            element={
                                <ProtectedRoute requiredRole="admin">
                                    <Layout>
                                        <UsersPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/users/new"
                            element={
                                <ProtectedRoute requiredRole="admin">
                                    <Layout>
                                        <CreateUserPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/users/:userId/edit"
                            element={
                                <ProtectedRoute requiredRole="admin">
                                    <Layout>
                                        <EditUserPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/groups"
                            element={
                                <ProtectedRoute requiredRole="admin">
                                    <Layout>
                                        <GroupsPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/groups/:groupId"
                            element={
                                <ProtectedRoute requiredRole="admin">
                                    <Layout>
                                        <GroupDetailPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />

                        {/* User routes */}
                        <Route
                            path="/dashboard/user/groups"
                            element={
                                <ProtectedRoute>
                                    <Layout>
                                        <UserGroupsPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/user/groups/:groupId"
                            element={
                                <ProtectedRoute>
                                    <Layout>
                                        <UserGroupDetailPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/user/courses"
                            element={
                                <ProtectedRoute>
                                    <Layout>
                                        <UserCoursesPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/user/progress"
                            element={
                                <ProtectedRoute>
                                    <Layout>
                                        <UserProgressPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />

                        {/* Error pages */}
                        <Route
                            path="/unauthorized"
                            element={<UnauthorizedPage />}
                        />

                        {/* Catch all - redirect to login */}
                        <Route
                            path="*"
                            element={<Navigate to="/login" replace />}
                        />
                    </Routes>
                </SidebarProvider>
            </AuthProvider>
        </BrowserRouter>
    );
}
