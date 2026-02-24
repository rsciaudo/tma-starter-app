import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDisclosure } from '@mantine/hooks';
import { getModule, patchModule } from '../../utils/api';
import AdminPageLayout from '../../components/layout/AdminPageLayout';
import { IconEdit } from '@tabler/icons-react';
import { Group, Button, Title } from '@mantine/core';
import { designTokens } from '../../designTokens';
import EditModuleModal from '../../components/courses/EditModuleModal';
import type { ModuleUpdate, ModuleDetail } from '../../types/api';
import { usePageState } from '../../hooks/usePageState';
import { useAuth } from '../../contexts/AuthContext';

export default function ModuleDetailPage() {
    const { moduleId } = useParams<{ moduleId: string }>();
    const { API_URL, userInfo } = useAuth();
    const navigate = useNavigate();
    const { courseId } = useParams<{ courseId: string }>();
    const [editModalOpened, { open: openEditModal, close: closeEditModal }] =
        useDisclosure(false);

    // Form state for module edit
    const [moduleTitle, setModuleTitle] = useState('');
    const [moduleDescription, setModuleDescription] = useState('');
    const [module, setModule] = useState<ModuleDetail | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Check if user can edit (admin only)
    const canEdit = userInfo?.role?.name === 'admin';

    async function fetchModule() {
        if (!moduleId) return;
        setLoading(true);
        setError(null);
        try {
            const moduleData = await getModule(Number(moduleId), API_URL);
            setModule(moduleData);
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        if (moduleId) {
            fetchModule();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [moduleId]);

    // Initialize form state when module loads
    useEffect(() => {
        if (module) {
            setModuleTitle(module.title);
            setModuleDescription(module.description || '');
        }
    }, [module]);

    function handleEditModule() {
        if (module) {
            setModuleTitle(module.title);
            setModuleDescription(module.description || '');
            openEditModal();
        }
    }

    async function handleUpdateModule(e: React.FormEvent) {
        e.preventDefault();
        if (!moduleId) return;
        setLoading(true);
        setError(null);

        try {
            const updateData: ModuleUpdate = {
                title: moduleTitle.trim(),
                description: moduleDescription.trim() || null,
            };

            await patchModule(Number(moduleId), updateData, API_URL);
            closeEditModal();
            await fetchModule();
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    }

    const pageState = usePageState({
        data: module,
        loading,
        error,
        notFoundMessage: 'Module Not Found',
    });

    if (!pageState.shouldRenderContent) {
        return pageState.component;
    }

    if (!module) {
        return null;
    }

    //dashboard/courses/:courseId/modules/:moduleId
    const breadcrumbs = [
        { title: 'Dashboard', href: '/dashboard/courses' },
        { title: 'Courses', href: '/dashboard/courses' },
        {
            title: 'Modules',
            href: '/dashboard/courses/${courseId}/modules/${moduleId}',
        },
        { title: module.title, href: '#' },
    ];

    const menuItems = canEdit
        ? [
              {
                  label: 'Edit Module',
                  icon: <IconEdit size={16} />,
                  onClick: handleEditModule,
              },
          ]
        : undefined;

    return (
        <AdminPageLayout
            breadcrumbs={breadcrumbs}
            title={module.title}
            description={module.description || undefined}
            menuItems={menuItems}
            content={
                <>
                    {/* Modules Section */}
                    <div>
                        <Group justify="space-between" gap="sm" align="center">
                            <Title order={2} mb="md">
                                Modules
                            </Title>
                            {canEdit && (
                                <Button
                                    variant="filled"
                                    color="teal"
                                    onClick={() =>
                                        navigate(
                                            `/dashboard/courses/${courseId}/modules/${moduleId}`
                                        )
                                    }
                                    style={{
                                        backgroundColor:
                                            designTokens.app.primary,
                                        color: designTokens.surface.white,
                                    }}
                                >
                                    Update Module
                                </Button>
                            )}
                        </Group>
                    </div>
                    {/* Edit Course Modal */}
                    {canEdit && (
                        <EditModuleModal
                            opened={editModalOpened}
                            onClose={closeEditModal}
                            moduleTitle={moduleTitle}
                            moduleDescription={moduleDescription}
                            onTitleChange={(
                                e: React.ChangeEvent<HTMLInputElement>
                            ) => setModuleTitle(e.currentTarget.value)}
                            onDescriptionChange={(
                                e: React.ChangeEvent<HTMLTextAreaElement>
                            ) => setModuleDescription(e.currentTarget.value)}
                            onSubmit={handleUpdateModule}
                            loading={loading}
                        />
                    )}
                </>
            }
        />
    );
}
