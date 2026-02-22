import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDisclosure } from '@mantine/hooks';
import { IconEdit, IconBook } from '@tabler/icons-react';
import { useAuth } from '../../contexts/AuthContext';
import { getCourse, patchCourse } from '../../utils/api';
import AdminPageLayout from '../../components/layout/AdminPageLayout';
import EditCourseModal from '../../components/courses/EditCourseModal';
import { usePageState } from '../../hooks/usePageState';
import type { CourseUpdate, CourseDetail, CourseModule } from '../../types/api';
import { designTokens } from '../../designTokens';
import { Stack, Text, Group, Button, Title, Card, Box } from '@mantine/core';

export default function CourseDetailPage() {
    const { courseId } = useParams<{ courseId: string }>();
    const navigate = useNavigate();
    const { API_URL, userInfo } = useAuth();
    const [editModalOpened, { open: openEditModal, close: closeEditModal }] =
        useDisclosure(false);

    // Form state for course edit
    const [courseTitle, setCourseTitle] = useState('');
    const [courseDescription, setCourseDescription] = useState('');
    const [course, setCourse] = useState<CourseDetail | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Form state variables for modules
    const [modules, setModules] = useState<CourseModule[]>([]);
    const [modulesLoading, setModulesLoading] = useState(false);
    // Check if user can edit (admin only)
    const canEdit = userInfo?.role?.name === 'admin';

    async function fetchCourse() {
        if (!courseId) return;
        setLoading(true);
        setError(null);
        try {
            const courseData = await getCourse(Number(courseId), API_URL);
            setCourse(courseData);
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        if (courseId) {
            fetchCourse();
            fetchCourseModules();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [courseId]);

    // Initialize form state when course loads
    useEffect(() => {
        if (course) {
            setCourseTitle(course.title);
            setCourseDescription(course.description || '');
        }
    }, [course]);

    async function fetchCourseModules() {
        if (!courseId) return;
        setModulesLoading(true);
        try {
            const data = await getCourse(Number(courseId), API_URL);
            setModules(data.modules);
        } catch (err) {
            console.error('Error fetching course modules:', err);
        } finally {
            setModulesLoading(false);
        }
    }
    function handleEditCourse() {
        if (course) {
            setCourseTitle(course.title);
            setCourseDescription(course.description || '');
            openEditModal();
        }
    }

    async function handleUpdateCourse(e: React.FormEvent) {
        e.preventDefault();
        if (!courseId) return;
        setLoading(true);
        setError(null);

        try {
            const updateData: CourseUpdate = {
                title: courseTitle.trim(),
                description: courseDescription.trim() || null,
            };

            await patchCourse(Number(courseId), updateData, API_URL);
            closeEditModal();
            await fetchCourse();
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    }

    const pageState = usePageState({
        data: course,
        loading,
        error,
        notFoundMessage: 'Course Not Found',
    });

    if (!pageState.shouldRenderContent) {
        return pageState.component;
    }

    if (!course) {
        return null;
    }

    const breadcrumbs = [
        { title: 'Dashboard', href: '/dashboard/courses' },
        { title: 'Courses', href: '/dashboard/courses' },
        { title: course.title, href: '#' },
    ];

    // Prepare menu items for PageHeader
    const menuItems = canEdit
        ? [
              {
                  label: 'Edit Course',
                  icon: <IconEdit size={16} />,
                  onClick: handleEditCourse,
              },
          ]
        : undefined;

    return (
        <AdminPageLayout
            breadcrumbs={breadcrumbs}
            title={course.title}
            description={course.description || undefined}
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
                                            `/dashboard/courses/${course.id}/modules/new`
                                        )
                                    }
                                    style={{
                                        backgroundColor:
                                            designTokens.app.primary,
                                        color: designTokens.surface.white,
                                    }}
                                >
                                    Create Module
                                </Button>
                            )}
                        </Group>

                        {modulesLoading ? (
                            <Text>Loading modules...</Text>
                        ) : modules.length === 0 ? (
                            <Text c="dimmed" mb="md">
                                There are no modules in this course.
                            </Text>
                        ) : (
                            <Stack gap="sm">
                                {modules.map((module) => (
                                    <Card
                                        key={module.module_id}
                                        shadow="sm"
                                        padding={0}
                                        radius="md"
                                        withBorder
                                        style={{
                                            cursor: 'pointer',
                                            overflow: 'hidden',
                                        }}
                                        onClick={() =>
                                            navigate(
                                                `/dashboard/courses/${course.id}/modules/${module.module_id}`
                                            )
                                        }
                                        onKeyDown={(e) => {
                                            if (
                                                e.key === 'Enter' ||
                                                e.key === ' '
                                            ) {
                                                e.preventDefault();
                                                navigate(
                                                    `/dashboard/courses/${course.id}/modules/${module.module_id}`
                                                );
                                            }
                                        }}
                                        tabIndex={0}
                                        role="button"
                                    >
                                        <Group
                                            gap={0}
                                            align="stretch"
                                            style={{ minHeight: '100%' }}
                                        >
                                            <Box
                                                style={{
                                                    width: '120px',
                                                    minHeight: '100%',
                                                    backgroundColor:
                                                        designTokens
                                                            .moduleColors
                                                            .darkBlue,
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    flexShrink: 0,
                                                }}
                                            >
                                                <IconBook
                                                    size={48}
                                                    style={{
                                                        color: designTokens
                                                            .surface.white,
                                                    }}
                                                />
                                            </Box>
                                            <Stack
                                                gap="sm"
                                                p="md"
                                                style={{
                                                    flex: 1,
                                                    minHeight: '100%',
                                                }}
                                            >
                                                <Text fw={600} size="md">
                                                    {module.module_title}
                                                </Text>
                                                {module.module_description && (
                                                    <Text c="dimmed" size="sm">
                                                        {
                                                            module.module_description
                                                        }
                                                    </Text>
                                                )}
                                            </Stack>
                                        </Group>
                                    </Card>
                                ))}
                            </Stack>
                        )}
                    </div>

                    {/* Edit Course Modal */}
                    {canEdit && (
                        <EditCourseModal
                            opened={editModalOpened}
                            onClose={closeEditModal}
                            courseTitle={courseTitle}
                            courseDescription={courseDescription}
                            onTitleChange={(
                                e: React.ChangeEvent<HTMLInputElement>
                            ) => setCourseTitle(e.currentTarget.value)}
                            onDescriptionChange={(
                                e: React.ChangeEvent<HTMLTextAreaElement>
                            ) => setCourseDescription(e.currentTarget.value)}
                            onSubmit={handleUpdateCourse}
                            loading={loading}
                        />
                    )}
                </>
            }
        />
    );
}
