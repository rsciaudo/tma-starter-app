import { useState } from 'react';
import { StyleSheet, View, Platform } from 'react-native';
import { Card, Text, ActivityIndicator } from 'react-native-paper';
import { WebView } from 'react-native-webview';
import type { PostVideo } from '../../types/api';

interface PostVideoProps {
    post: PostVideo;
}

export default function PostVideo({ post }: PostVideoProps) {
    const [videoLoading, setVideoLoading] = useState(true);

    const text = post.text ?? '';

    // extract youtube id from end of url
    const videoId = post.video_url?.split('v=')[1]?.split('&')[0];

    const embedUrl = videoId
        ? `https://www.youtube.com/embed/${videoId}?modestbranding=1&rel=0&playsinline=1&controls=1`
        : null;
    // video options s.t youtube doesn't inclue all the bloat, just the video
    return (
        <Card style={styles.card} mode="elevated">
            {embedUrl && (
                <View style={styles.videoContainer}>
                    {videoLoading && (
                        <ActivityIndicator
                            style={styles.loader}
                            animating={true}
                            size="large"
                        />
                    )}

                    {Platform.OS === 'web' ? (
                        <iframe
                            src={embedUrl}
                            width="100%"
                            height="315"
                            allow="autoplay; encrypted-media"
                            allowFullScreen
                            style={{ border: 'none' }}
                            onLoad={() => setVideoLoading(false)}
                        />
                    ) : (
                        <WebView
                            style={styles.video}
                            source={{ uri: embedUrl }}
                            onLoadEnd={() => setVideoLoading(false)}
                            allowsFullscreenVideo
                            scrollEnabled={false}
                        />
                    )}
                </View>
            )}

            <Card.Content style={styles.content}>
                <Text variant="titleLarge" style={styles.title}>
                    {post.title}
                </Text>

                <Text variant="bodyMedium" style={styles.text}>
                    {text}
                </Text>
            </Card.Content>
        </Card>
    );
}

const styles = StyleSheet.create({
    card: {
        margin: 12,
        borderRadius: 12,
    },
    videoContainer: {
        justifyContent: 'center',
        alignItems: 'center',
        position: 'relative',
    },
    loader: {
        position: 'absolute',
        zIndex: 1,
    },
    video: {
        width: '100%',
        aspectRatio: 16 / 9,
        borderTopLeftRadius: 12,
        borderTopRightRadius: 12,
    },
    content: {
        paddingVertical: 12,
    },
    title: {
        marginBottom: 6,
    },
    text: {
        lineHeight: 20,
    },
});
