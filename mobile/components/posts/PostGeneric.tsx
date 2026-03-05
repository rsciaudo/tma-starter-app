import { useState } from 'react';
import { StyleSheet, TouchableOpacity, View } from 'react-native';
import { Card, Text, ActivityIndicator } from 'react-native-paper';
import type { PostGeneric } from '../../types/api.ts';

interface PostGenericProps {
    post: PostGeneric;
}

export default function PostGeneric({ post }: PostGenericProps) {
    const [expanded, setExpanded] = useState(false);
    const [imageLoading, setImageLoading] = useState(true);
    const text = post.text ?? '';

    return (
        <Card style={styles.card} mode="elevated">
            {post.image && (
                <View style={styles.imageContainer}>
                    {imageLoading && (
                        <ActivityIndicator
                            style={styles.loader}
                            animating={true}
                            size="large"
                            color="#6200ee"
                        />
                    )}

                    <Card.Cover
                        source={{ uri: post.image }}
                        style={styles.image}
                        onLoadEnd={() => setImageLoading(false)}
                    />
                </View>
            )}

            <Card.Content style={styles.content}>
                <Text variant="titleLarge" style={styles.title}>
                    {post.title}
                </Text>

                <Text
                    variant="bodyMedium"
                    style={styles.text}
                    numberOfLines={expanded ? undefined : 5}
                    ellipsizeMode="tail"
                >
                    {text}
                </Text>

                {text.length > 200 && (
                    <TouchableOpacity onPress={() => setExpanded(!expanded)}>
                        <Text style={styles.toggle}>
                            {expanded ? 'Read less' : 'Read more'}
                        </Text>
                    </TouchableOpacity>
                )}
            </Card.Content>
        </Card>
    );
}

const styles = StyleSheet.create({
    card: {
        margin: 12,
        borderRadius: 12,
    },
    imageContainer: {
        justifyContent: 'center',
        alignItems: 'center',
        position: 'relative',
    },
    loader: {
        position: 'absolute',
        zIndex: 1,
    },
    image: {
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
    toggle: {
        marginTop: 6,
        fontWeight: 'bold',
    },
});
