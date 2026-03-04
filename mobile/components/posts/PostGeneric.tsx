import { View } from 'react-native';
import { Text } from 'react-native-paper';
import type { PostGeneric } from '../../types/api.ts';

interface PostGenericProps {
    post: PostGeneric;
}

export default function PostGeneric({ post }: PostGenericProps) {
    return (
        <>
            <View>
                <Text>{post.title}</Text>
            </View>
        </>
    );
}
