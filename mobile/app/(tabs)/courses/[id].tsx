import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import {
    Card,
    Text,
    ActivityIndicator,
    Snackbar,
    Appbar,
} from 'react-native-paper';
import { useLocalSearchParams, useRouter } from 'expo-router';
import ProtectedRoute from '../../../components/ProtectedRoute';
import { getCourseDetail } from '../../../services/courses';
import { CourseDetail, CourseModule } from '../../../types';
import { designTokens } from '../../../theme';

export default function CourseDetailScreen() {
    const { id } = useLocalSearchParams<{ id: string }>();
    const router = useRouter();
    const courseId = parseInt(id || '0', 10);

    const {
        data: course,
        isLoading,
        error,
        refetch,
        isRefetching,
    } = useQuery<CourseDetail>({
        queryKey: ['courseDetail', courseId],
        queryFn: () => getCourseDetail(courseId),
        enabled: Boolean(courseId && courseId > 0),
    });

    if (isLoading) {
        return (
            <View style={styles.center}>
                <ActivityIndicator size="large" />
            </View>
        );
    }

    return (
        <ProtectedRoute>
            <View style={styles.container}>
                <Appbar.Header>
                    <Appbar.BackAction onPress={() => router.back()} />
                    <Appbar.Content title={course?.title || 'Course'} />
                </Appbar.Header>

                <ScrollView
                    refreshControl={
                        <RefreshControl
                            refreshing={isRefetching}
                            onRefresh={() => refetch()}
                        />
                    }
                >
                    <View style={styles.content}>
                        {error && (
                            <Snackbar
                                visible={Boolean(error)}
                                onDismiss={() => {}}
                                duration={4000}
                            >
                                Error loading course. Please try again.
                            </Snackbar>
                        )}

                        {course && (
                            <>
                                {course.description && (
                                    <Card style={styles.card}>
                                        <Card.Content>
                                            <Text variant="bodyLarge">
                                                {course.description}
                                            </Text>
                                        </Card.Content>
                                    </Card>
                                )}

                                <Text
                                    variant="titleLarge"
                                    style={styles.sectionTitle}
                                >
                                    Modules
                                </Text>

                                {!course.modules ||
                                course.modules.length === 0 ? (
                                    <Card style={styles.card} mode="outlined">
                                        <Card.Content
                                            style={{
                                                padding:
                                                    designTokens.spacing.xxl,
                                                alignItems: 'center',
                                            }}
                                        >
                                            <Text
                                                variant="bodyMedium"
                                                style={{ opacity: 0.7 }}
                                            >
                                                No modules in this course.
                                            </Text>
                                        </Card.Content>
                                    </Card>
                                ) : (
                                    course.modules
                                        .sort(
                                            (
                                                a: CourseModule,
                                                b: CourseModule
                                            ) => a.ordering - b.ordering
                                        )
                                        .map((module: CourseModule) => (
                                            <Card
                                                key={module.module_id}
                                                style={styles.card}
                                                mode="elevated"
                                                onPress={() =>
                                                    router.push(
                                                        `/(tabs)/modules/${module.module_id}`
                                                    )
                                                }
                                            >
                                                <Card.Content
                                                    style={{
                                                        padding:
                                                            designTokens.spacing
                                                                .xl,
                                                    }}
                                                >
                                                    <View
                                                        style={
                                                            styles.moduleHeader
                                                        }
                                                    >
                                                        <View
                                                            style={{
                                                                flexDirection:
                                                                    'row',
                                                                alignItems:
                                                                    'center',
                                                                flex: 1,
                                                            }}
                                                        >
                                                            {module.module_color && (
                                                                <View
                                                                    style={[
                                                                        styles.colorIndicator,
                                                                        {
                                                                            backgroundColor:
                                                                                module.module_color,
                                                                        },
                                                                    ]}
                                                                />
                                                            )}
                                                            <Text
                                                                variant="titleMedium"
                                                                style={{
                                                                    fontWeight:
                                                                        '600',
                                                                    flex: 1,
                                                                }}
                                                            >
                                                                {
                                                                    module.module_title
                                                                }
                                                            </Text>
                                                        </View>
                                                    </View>
                                                    {module.module_description && (
                                                        <Text
                                                            variant="bodyMedium"
                                                            style={
                                                                styles.description
                                                            }
                                                            numberOfLines={2}
                                                        >
                                                            {
                                                                module.module_description
                                                            }
                                                        </Text>
                                                    )}
                                                </Card.Content>
                                            </Card>
                                        ))
                                )}
                            </>
                        )}
                    </View>
                </ScrollView>
            </View>
        </ProtectedRoute>
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
