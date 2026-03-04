import { View } from 'react-native';
import { Text } from 'react-native-paper';
import type { PostAttachment } from '../../types/api.ts';

interface PostAttachmentProps {
    post: PostAttachment;
}

export default function PostAttachment({ post }: PostAttachmentProps) {
    return (
        <>
            <View>
                <Text>{post.title}</Text>
            </View>
        </>
    );
}
