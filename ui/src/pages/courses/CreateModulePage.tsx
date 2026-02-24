import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
    Button,
    TextInput,
    Textarea,
    Stack,
    Group,
    Alert,
    ColorInput,
} from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';
import { useAuth } from '../../contexts/AuthContext';
import { createModule, addModuleToCourse } from '../../utils/api';
import AdminPageLayout from '../../components/layout/AdminPageLayout';
import type { ModuleCreate } from '../../types/api';

export default function CreateModulePage() {
    const { API_URL } = useAuth();
    const navigate = useNavigate();
    const { courseId } = useParams<{ courseId: string }>();

    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [color, setColor] = useState<string | undefined>(undefined);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();

        if (!title.trim()) {
            setError('Title is required.');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const moduleData: ModuleCreate = {
                title: title.trim(),
                description: description.trim() || null,
                color: color ?? null,
            };

            const newModule = await createModule(
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                {
                    module_data: moduleData,
                    module_posts: [],
                } as unknown as ModuleCreate,
                API_URL
            );

            const courseModule = await addModuleToCourse(
                Number(courseId),
                newModule.id,
                API_URL
            );
            console.log(courseModule);

            navigate(`/dashboard/courses/${courseId}`);
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : 'Failed to create module.';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    }

    const breadcrumbs = [
        { title: 'Dashboard', href: '/dashboard' },
        { title: 'Courses', href: '/dashboard/courses' },
        {
            title: 'Course',
            href: `/dashboard/courses/${courseId}`,
        },
        {
            title: 'Create Module',
            href: `/dashboard/courses/${courseId}/modules/new`,
        },
    ];

    return (
        <AdminPageLayout
            title="Create Module"
            description="Add a new module."
            breadcrumbs={breadcrumbs}
            content={
                <form onSubmit={handleSubmit}>
                    <Stack gap="md">
                        <TextInput
                            label="Title"
                            value={title}
                            onChange={(e) => setTitle(e.currentTarget.value)}
                            required
                            disabled={loading}
                            autoFocus
                        />

                        <Textarea
                            label="Description"
                            value={description}
                            onChange={(e) =>
                                setDescription(e.currentTarget.value)
                            }
                            disabled={loading}
                            rows={3}
                        />
                        <ColorInput
                            value={color}
                            onChange={setColor}
                            label="Pick a color. Leave as is or delete text for no color"
                        />
                        {error && (
                            <Alert
                                icon={<IconAlertCircle size={16} />}
                                title="Error"
                                color="red"
                            >
                                {error}
                            </Alert>
                        )}

                        <Group justify="flex-end">
                            <Button
                                variant="subtle"
                                onClick={() =>
                                    navigate(`/dashboard/courses/${courseId}`)
                                }
                                disabled={loading}
                            >
                                Cancel
                            </Button>

                            <Button type="submit" loading={loading}>
                                Create Module
                            </Button>
                        </Group>
                    </Stack>
                </form>
            }
        />
    );
}
