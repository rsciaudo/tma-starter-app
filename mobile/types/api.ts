/**
 * Type definitions for API responses and requests
 * Based on backend Pydantic schemas
 */

// ============================================================================
// Common Types
// ============================================================================

export interface Role {
    id: number;
    name: string;
    description?: string | null;
}

// ============================================================================
// Auth Types
// ============================================================================

export interface User {
    id: number;
    username: string;
    email: string;
    first_name?: string | null;
    last_name?: string | null;
    child_name?: string | null;
    child_sex_assigned_at_birth?: string | null;
    child_dob?: string | null; // ISO date string
    avatar_url?: string | null;
    role: Role;
    email_verified: boolean;
    is_active: boolean;
    created_at: string; // ISO datetime string
    updated_at: string; // ISO datetime string
}

export interface Token {
    access_token: string;
    token_type: string;
}

export interface UserCreate {
    username: string;
    email: string;
    password: string;
    role?: string;
    first_name?: string | null;
    last_name?: string | null;
    child_name?: string | null;
    child_sex_assigned_at_birth?: string | null;
    child_dob?: string | null;
    avatar_url?: string | null;
}

// ============================================================================
// Course Types
// ============================================================================

export interface Course {
    id: number;
    title: string;
    description?: string | null;
    file_url?: string | null;
    module_count?: number;
    created_at: string;
    updated_at: string;
}

export interface CourseModule {
    module_id: number;
    module_title: string;
    module_description?: string | null;
    module_color?: string | null;
    ordering: number;
}

export interface CourseDetail extends Course {
    modules: CourseModule[];
}

// ============================================================================
// Group Types
// ============================================================================

export interface GroupMember {
    user_id: number;
    username: string;
    email: string;
    first_name?: string | null;
    last_name?: string | null;
    role: Role;
    group_role?: string | null; // "member", "moderator", "owner"
    user_role?: string | null; // User's system role ('admin', 'user', 'manager')
    joined_at: string;
    avatar_url?: string | null;
}

export interface Group {
    id: number;
    name: string;
    description?: string | null;
    created_at: string;
    updated_at: string;
    member_count?: number;
}

export interface GroupDetail extends Group {
    members: GroupMember[];
}

// ============================================================================
// Course Group Types
// ============================================================================

export interface CourseGroup {
    id: number;
    course_id: number;
    group_id: number;
    ordering: number;
    date_assigned: string;
}

// ============================================================================
// Module Types
// ============================================================================

export interface Module {
    id: number;
    title: string;
    description?: string | null;
    created_at: string;
    updated_at: string;
    color?: string | null;
}

export interface ModulePost {
    post_id: number;
    post_title: string;
    post_type?: string | null;
    post_text?: string | null;
    post_image?: string | null;
    post_file_url?: string | null;
    post_file_name?: string | null;
    post_video_url?: string | null;
    post_video_name?: string | null;
    ordering: number;
}

export interface ModuleDetail extends Module {
    posts: ModulePost[];
}

// ============================================================================
// Post Types
// ============================================================================

export interface Post {
    id: number;
    title: string;
    type?: string | null;
    text?: string | null;
}

export interface PostGeneric extends Post {
    image?: string | null;
}

export interface PostAttachment extends Post {
    file_url?: string | null;
    file_name?: string | null;
}

export interface PostVideo extends Post {
    video_url?: string | null;
    video_name?: string | null;
}
