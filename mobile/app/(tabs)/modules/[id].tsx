import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import {
    Card,
    Snackbar,
    Text,
    ActivityIndicator,
    Appbar,
} from 'react-native-paper';
import { useLocalSearchParams, useRouter } from 'expo-router';
import ProtectedRoute from '../../../components/ProtectedRoute';
import { designTokens } from '../../../theme';
import { getModuleDetail } from '../../../services/modules';
import { ModuleDetail, ModulePost } from '../../../types';
import PostAttachment from '../../../components/posts/PostAttachment';
import PostGeneric from '../../../components/posts/PostGeneric';
import PostVideo from '../../../components/posts/PostVideo';

export default function ModuleDetailScreen() {
    const { id } = useLocalSearchParams<{ id: string }>();
    const router = useRouter();
    const moduleId = parseInt(id || '0', 10);
    const courseId = parseInt(
        useLocalSearchParams<{ courseId: string }>().courseId || '0',
        10
    );

    const {
        data: module,
        isLoading,
        error,
        refetch,
        isRefetching,
    } = useQuery<ModuleDetail>({
        queryKey: ['moduleDetail', moduleId],
        queryFn: () => getModuleDetail(moduleId),
        enabled: Boolean(moduleId && moduleId > 0),
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
                    <Appbar.BackAction
                        onPress={() =>
                            router.push(`/(tabs)/courses/${courseId}`)
                        }
                    />
                    <Appbar.Content title={module?.title || 'Module'} />
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
                                Error loading module. Please try again.
                            </Snackbar>
                        )}

                        {module && (
                            <>
                                {module.description && (
                                    <Card style={styles.card}>
                                        <Card.Content>
                                            <Text variant="bodyLarge">
                                                {module.description}
                                            </Text>
                                        </Card.Content>
                                    </Card>
                                )}
                                <Text
                                    variant="titleLarge"
                                    style={styles.sectionTitle}
                                >
                                    Posts
                                </Text>

                                {!module.posts || module.posts.length === 0 ? (
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
                                                No posts in this module.
                                            </Text>
                                        </Card.Content>
                                    </Card>
                                ) : (
                                    module.posts
                                        .sort(
                                            (a: ModulePost, b: ModulePost) =>
                                                a.ordering - b.ordering
                                        )
                                        .map((mp: ModulePost) =>
                                            // check if PostGeneric, PostAttachment, or PostVideo type and render accordingly

                                            mp.post_type === 'attachment' ? (
                                                <PostAttachment
                                                    key={mp.post_id}
                                                    post={{
                                                        id: mp.post_id,
                                                        title: mp.post_title,
                                                        type: 'attachment',
                                                        text:
                                                            mp.post_text ??
                                                            null,
                                                        file_url:
                                                            mp.post_file_url ??
                                                            null,
                                                        file_name:
                                                            mp.post_file_name ??
                                                            null,
                                                    }}
                                                />
                                            ) : mp.post_type === 'video' ? (
                                                <PostVideo
                                                    key={mp.post_id}
                                                    post={{
                                                        id: mp.post_id,
                                                        title: mp.post_title,
                                                        type: 'video',
                                                        text:
                                                            mp.post_text ??
                                                            null,
                                                        video_url:
                                                            mp.post_video_url ??
                                                            null,
                                                        video_name:
                                                            mp.post_video_name ??
                                                            null,
                                                    }}
                                                />
                                            ) : (
                                                <PostGeneric
                                                    key={mp.post_id}
                                                    post={{
                                                        id: mp.post_id,
                                                        title: mp.post_title,
                                                        type: 'generic',
                                                        text:
                                                            mp.post_text ??
                                                            null,
                                                        image:
                                                            mp.post_image ??
                                                            null,
                                                    }}
                                                />
                                            )
                                        )
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
