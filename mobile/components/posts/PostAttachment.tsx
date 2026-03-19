import { useState } from 'react';
import { StyleSheet, TouchableOpacity, View } from 'react-native';
import { Card, Text, Button } from 'react-native-paper';
import type { PostAttachment } from '../../types/api.ts';
import { MaterialCommunityIcons } from '@expo/vector-icons';

interface PostAttachmentProps {
    post: PostAttachment;
}

export default function PostAttachment({ post }: PostAttachmentProps) {
    const [expanded, setExpanded] = useState(false);
    const [downloading, setDownloading] = useState(false);
    const hasAttachment = post.file_url && post.file_name;

    const handleDownload = () => {
        setDownloading(true);
        console.log('Download PDF:', post.file_url);
        setTimeout(() => setDownloading(false), 1000);
    };

    return (
        <View>
            {/* PDF icon */}
            <Card style={styles.card} mode="elevated">
                {hasAttachment && (
                    <Card.Content style={styles.attachmentRow}>
                        <View style={styles.iconContainer}>
                            <MaterialCommunityIcons
                                name="file-pdf-box"
                                size={36}
                                color="#B00020"
                            />
                        </View>

                        <View style={styles.container}>
                            {/* Title */}
                            <Text variant="bodyLarge" numberOfLines={1}>
                                {post.title}
                            </Text>
                        </View>

                        <View style={styles.container}>
                            {/* Content and file */}
                            <Text
                                variant="bodyMedium"
                                style={styles.text}
                                numberOfLines={expanded ? undefined : 5}
                                ellipsizeMode="tail"
                            >
                                {post.text}
                                {post.file_name}
                            </Text>
                        </View>

                        {/* Download button */}
                        <Button
                            onPress={handleDownload}
                            loading={downloading}
                            disabled={downloading}
                        >
                            Download
                        </Button>

                        {post.text && post.text.length > 200 && (
                            <TouchableOpacity
                                onPress={() => setExpanded(!expanded)}
                            >
                                <Text style={styles.toggle}>
                                    {expanded ? 'Read less' : 'Read more'}
                                </Text>
                            </TouchableOpacity>
                        )}
                    </Card.Content>
                )}
            </Card>
        </View>
    );
}

const styles = StyleSheet.create({
    card: {
        margin: 12,
        borderRadius: 12,
    },
    fileContainer: {
        justifyContent: 'center',
        alignItems: 'center',
        position: 'relative',
    },
    iconContainer: {
        justifyContent: 'center',
        alignItems: 'center',
    },
    attachmentRow: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 8,
        gap: 12,
    },
    container: {
        flex: 1,
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
