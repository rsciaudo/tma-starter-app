import { View } from 'react-native';
import { Text } from 'react-native-paper';
import type { PostVideo } from '../../types/api.ts';

interface PostVideoProps {
    post: PostVideo;
}

export default function PostVideo({ post }: PostVideoProps) {
    return (
        <>
            <View>
                <Text>{post.title}</Text>
            </View>
        </>
    );
}
