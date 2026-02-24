import {
    Modal,
    Stack,
    TextInput,
    Textarea,
    Group,
    Button,
} from '@mantine/core';

interface EditModuleModalProps {
    opened: boolean;
    onClose: () => void;
    moduleTitle: string;
    moduleDescription: string;
    onTitleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onDescriptionChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
    onSubmit: (e: React.FormEvent) => void;
    loading: boolean;
    // File upload props (optional - for future implementation by students)
    selectedFile?: File | null;
    onFileChange?: (file: File | null) => void;
    onRemoveImage?: () => void;
    isRemoving?: boolean;
    currentFileUrl?: string | null;
    currentFileName?: string | null;
}

/**
 * Modal for editing module details
 * Note: File upload functionality will be implemented by students
 */
export default function EditModuleModal({
    opened,
    onClose,
    moduleTitle,
    moduleDescription,
    onTitleChange,
    onDescriptionChange,
    onSubmit,
    loading,
}: EditModuleModalProps) {
    return (
        <Modal opened={opened} onClose={onClose} title="Edit Module" centered>
            <form onSubmit={onSubmit}>
                <Stack gap="md">
                    <TextInput
                        label="Module Title"
                        placeholder="Enter module title"
                        value={moduleTitle}
                        onChange={onTitleChange}
                        required
                        disabled={loading}
                        autoFocus
                    />
                    <Textarea
                        label="Description"
                        placeholder="Enter module description (optional)"
                        value={moduleDescription}
                        onChange={onDescriptionChange}
                        disabled={loading}
                        rows={4}
                    />
                    {/* File upload functionality will be implemented by students */}
                    <Group justify="flex-end">
                        <Button
                            variant="subtle"
                            onClick={onClose}
                            disabled={loading}
                        >
                            Cancel
                        </Button>
                        <Button type="submit" loading={loading}>
                            Update Module
                        </Button>
                    </Group>
                </Stack>
            </form>
        </Modal>
    );
}
