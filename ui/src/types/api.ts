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
    avatar_url?: string | null;
    role: Role;
    email_verified: boolean;
    is_active: boolean;
    created_at: string; // ISO datetime string
    updated_at: string; // ISO datetime string
    child_name?: string | null;
    child_sex_assigned_at_birth?: string | null;
    child_dob?: string | null;
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
}

export interface UserUpdate {
    username?: string | null;
    email?: string | null;
    password?: string | null;
    role?: string | null;
    first_name?: string | null;
    last_name?: string | null;
    is_active?: boolean | null;
}

export interface UserProfileUpdate {
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
    created_at: string;
    updated_at: string;
    module_count?: number; // Optional, may be added by backend in some responses
}

export interface CourseCreate {
    title: string;
    description?: string | null;
}

export interface CourseUpdate {
    title?: string | null;
    description?: string | null;
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
    group_role: string; // "member", "moderator", "owner" (group membership role)
    user_role?: string | null; // "admin", "user", "manager" (user's system role)
    joined_at: string;
}

export interface Group {
    id: number;
    name: string;
    description?: string | null;
    created_at: string;
    updated_at: string;
}

export interface GroupDetail extends Group {
    members: GroupMember[];
}

export interface GroupCreate {
    name: string;
    description?: string | null;
}

export interface GroupUpdate {
    name?: string | null;
    description?: string | null;
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

export interface ModuleCreate {
    title: string;
    description?: string | null;
    color?: string | null;
}

export interface ModuleUpdate {
    title?: string | null;
    description?: string | null;
}

export interface ModuleDetail extends Module {
    // Requires implementation of posts
}
