import { StyleSheet, View } from 'react-native';
import { Card, Text } from 'react-native-paper';
import type { CourseModule, Course } from '../../types/api.ts';
import { designTokens } from '../../theme';
import { useRouter } from 'expo-router';

interface ModuleCardProps {
    module: CourseModule;
}

interface CourseProps {
    course: Course;
}

export default function ModuleCard({
    module,
    course,
}: ModuleCardProps & CourseProps) {
    const router = useRouter();

    return (
        <Card
            key={module.module_id}
            style={styles.card}
            mode="elevated"
            onPress={() =>
                router.push({
                    pathname: `/(tabs)/modules/${module.module_id}`,
                    params: { courseId: course.id },
                })
            }
        >
            <Card.Content
                style={{
                    padding: designTokens.spacing.xl,
                }}
            >
                <View style={styles.moduleHeader}>
                    <View
                        style={{
                            flexDirection: 'row',
                            alignItems: 'center',
                            flex: 1,
                        }}
                    >
                        {module.module_color && (
                            <View
                                style={[
                                    styles.colorIndicator,
                                    {
                                        backgroundColor: module.module_color,
                                    },
                                ]}
                            />
                        )}
                        <Text
                            variant="titleMedium"
                            style={{
                                fontWeight: '600',
                                flex: 1,
                            }}
                        >
                            {module.module_title}
                        </Text>
                    </View>
                </View>
                {module.module_description && (
                    <Text
                        variant="bodyMedium"
                        style={styles.description}
                        numberOfLines={2}
                    >
                        {module.module_description}
                    </Text>
                )}
            </Card.Content>
        </Card>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    content: {
        padding: designTokens.spacing.xl,
        paddingBottom: designTokens.spacing.xxxl,
    },
    center: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    card: {
        marginBottom: designTokens.spacing.lg,
        borderRadius: designTokens.borderRadius.lg,
    },
    sectionTitle: {
        marginBottom: designTokens.spacing.lg,
        marginTop: designTokens.spacing.sm,
        fontWeight: '600',
    },
    moduleHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: designTokens.spacing.sm,
    },
    colorIndicator: {
        width: 20,
        height: 20,
        borderRadius: 10,
        marginRight: designTokens.spacing.md,
    },
    description: {
        marginTop: designTokens.spacing.sm,
        opacity: 0.7,
        lineHeight: 20,
    },
});
