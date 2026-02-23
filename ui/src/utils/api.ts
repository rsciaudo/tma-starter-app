/**
 * API utility functions for making authenticated requests
 */

import type {
    User,
    UserCreate,
    UserProfileUpdate,
    Group,
    GroupDetail,
    GroupCreate,
    GroupUpdate,
    Course,
    CourseDetail,
    CourseCreate,
    CourseUpdate,
    Module,
    ModuleCreate,
    ModuleUpdate,
    ModuleDetail,
} from '../types/api.js';

/**
 * Get authentication headers for API requests
 * @param includeContentType - Whether to include Content-Type header (default: true)
 * @returns Headers object with Content-Type (if requested) and Authorization
 */
export function getAuthHeaders(
    includeContentType = true
): Record<string, string> {
    const token = localStorage.getItem('auth_token');
    const headers: Record<string, string> = {
        ...(includeContentType && { 'Content-Type': 'application/json' }),
        ...(token && { Authorization: `Bearer ${token}` }),
    };

    return headers;
}

/**
 * Get the API base URL from environment or default to localhost
 * Includes /api prefix for all API routes
 */
export function getApiUrl(): string {
    const baseUrl =
        (import.meta.env.VITE_API_URL as string | undefined) !== undefined
            ? (import.meta.env.VITE_API_URL as string)
            : 'http://localhost:8000';
    // Ensure /api is appended to the base URL
    return baseUrl.endsWith('/api') ? baseUrl : `${baseUrl}/api`;
}

interface ErrorResponse {
    detail?: string;
}

/**
 * Handle API response errors consistently
 * @param response - Fetch response object
 * @returns Parsed JSON response
 * @throws {Error} If response is not ok
 */
async function handleResponse<T = unknown>(
    response: Response
): Promise<T | null> {
    if (!response.ok) {
        let errorMessage = `Server error: ${response.status} ${response.statusText}`;
        try {
            const errorData = (await response.json()) as ErrorResponse;
            errorMessage = errorData.detail || errorMessage;
        } catch {
            // If response is not JSON, use status text
        }

        // Log more details for debugging
        if (response.status === 401 || response.status === 403) {
            console.error('Authentication error:', {
                status: response.status,
                statusText: response.statusText,
                message: errorMessage,
                hasToken: !!localStorage.getItem('auth_token'),
            });
        }

        // Check for authentication errors and redirect to login
        if (
            response.status === 401 ||
            response.status === 403 ||
            errorMessage.includes('Could not validate credentials') ||
            errorMessage.includes('Not authenticated')
        ) {
            // Clear auth token
            localStorage.removeItem('auth_token');
            localStorage.removeItem('token_type');

            // Redirect to login page
            // Only redirect if we're not already on the login page
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }

        throw new Error(errorMessage);
    }

    // Handle 204 No Content responses (common for DELETE requests)
    if (response.status === 204) {
        return null;
    }

    return response.json() as Promise<T>;
}

// ============================================================================
// USER API Functions
// ============================================================================

/**
 * Create a new user (admin only)
 * @param userData - User data including username, email, password, role, and optional profile fields
 * @param apiUrl - Base API URL
 * @returns Created user object
 */
export async function createUser(
    userData: UserCreate,
    apiUrl = getApiUrl()
): Promise<User> {
    const response = await fetch(`${apiUrl}/auth/register`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(userData),
    });
    return handleResponse<User>(response) as Promise<User>;
}

// ============================================================================
// GROUP API Functions
// ============================================================================

/**
 * Get all groups
 * @param apiUrl - Base API URL
 * @returns Array of groups
 */
export async function getGroups(apiUrl = getApiUrl()): Promise<Group[]> {
    const response = await fetch(`${apiUrl}/groups`, {
        headers: getAuthHeaders(),
    });
    return handleResponse<Group[]>(response) as Promise<Group[]>;
}

/**
 * Get a single group by ID with members
 * @param groupId - Group ID
 * @param apiUrl - Base API URL
 * @returns Group object with members
 */
export async function getGroup(
    groupId: number,
    apiUrl = getApiUrl()
): Promise<GroupDetail> {
    const response = await fetch(`${apiUrl}/groups/${groupId}`, {
        headers: getAuthHeaders(),
    });
    return handleResponse<GroupDetail>(response) as Promise<GroupDetail>;
}

/**
 * Create a new group
 * @param groupData - Group data (name, description)
 * @param apiUrl - Base API URL
 * @returns Created group object
 */
export async function createGroup(
    groupData: GroupCreate,
    apiUrl = getApiUrl()
): Promise<Group> {
    const response = await fetch(`${apiUrl}/groups`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(groupData),
    });
    return handleResponse<Group>(response) as Promise<Group>;
}

/**
 * Update a group
 * @param groupId - Group ID
 * @param groupData - Partial group data to update
 * @param apiUrl - Base API URL
 * @returns Updated group object
 */
export async function patchGroup(
    groupId: number,
    groupData: GroupUpdate,
    apiUrl = getApiUrl()
): Promise<Group> {
    const response = await fetch(`${apiUrl}/groups/${groupId}`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify(groupData),
    });
    return handleResponse<Group>(response) as Promise<Group>;
}

/**
 * Delete a group
 * @param groupId - Group ID
 * @param apiUrl - Base API URL
 * @returns Promise<void>
 */
export async function deleteGroup(
    groupId: number,
    apiUrl = getApiUrl()
): Promise<void> {
    const response = await fetch(`${apiUrl}/groups/${groupId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
    });
    if (!response.ok) {
        throw new Error(`Failed to delete group: ${response.statusText}`);
    }
}

/**
 * Add a user to a group
 * @param groupId - Group ID
 * @param userId - User ID
 * @param role - Role (member, moderator, owner)
 * @param apiUrl - Base API URL
 * @returns Response object
 */
export async function addMemberToGroup(
    groupId: number,
    userId: number,
    role = 'member',
    apiUrl = getApiUrl()
): Promise<unknown> {
    const response = await fetch(
        `${apiUrl}/groups/${groupId}/members/${userId}`,
        {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ role }),
        }
    );
    return handleResponse(response);
}

/**
 * Remove a user from a group
 * @param groupId - Group ID
 * @param userId - User ID
 * @param apiUrl - Base API URL
 * @returns Promise<void>
 */
export async function removeMemberFromGroup(
    groupId: number,
    userId: number,
    apiUrl = getApiUrl()
): Promise<void> {
    const response = await fetch(
        `${apiUrl}/groups/${groupId}/members/${userId}`,
        {
            method: 'DELETE',
            headers: getAuthHeaders(),
        }
    );
    await handleResponse(response);
}

/**
 * Update a member's role in a group
 * @param groupId - Group ID
 * @param userId - User ID
 * @param role - New role (member, moderator, owner)
 * @param apiUrl - Base API URL
 * @returns Response object
 */
export async function updateMemberRole(
    groupId: number,
    userId: number,
    role: string,
    apiUrl = getApiUrl()
): Promise<unknown> {
    const response = await fetch(
        `${apiUrl}/groups/${groupId}/members/${userId}/role`,
        {
            method: 'PATCH',
            headers: getAuthHeaders(),
            body: JSON.stringify({ role }),
        }
    );
    return handleResponse(response);
}

/**
 * Get all users (for admin/manager use)
 * @param apiUrl - Base API URL
 * @returns Array of users
 */
export async function getAllUsers(apiUrl = getApiUrl()): Promise<User[]> {
    const response = await fetch(`${apiUrl}/auth/users`, {
        headers: getAuthHeaders(),
    });
    return handleResponse<User[]>(response) as Promise<User[]>;
}

/**
 * Disable or enable a user
 * @param userId - User ID
 * @param isActive - Whether user should be active
 * @param apiUrl - Base API URL
 * @returns Updated user object
 */
export async function updateUserStatus(
    userId: number,
    isActive: boolean,
    apiUrl = getApiUrl()
): Promise<User> {
    const response = await fetch(`${apiUrl}/auth/users/disable`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify({ user_id: userId, is_active: isActive }),
    });
    return handleResponse<User>(response) as Promise<User>;
}

/**
 * Change a user's role
 * @param userId - User ID
 * @param role - New role (admin, manager, user)
 * @param apiUrl - Base API URL
 * @returns Updated user object
 */
export async function updateUserRole(
    userId: number,
    role: string,
    apiUrl = getApiUrl()
): Promise<User> {
    const response = await fetch(`${apiUrl}/auth/users/role`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify({ user_id: userId, role }),
    });
    return handleResponse<User>(response) as Promise<User>;
}

/**
 * Update a user's profile fields
 * @param userId - User ID
 * @param profileData - Profile data (first_name, last_name, child_name, child_sex_assigned_at_birth, child_dob, avatar_url)
 * @param apiUrl - Base API URL
 * @returns Updated user object
 */
export async function updateUserProfile(
    userId: number,
    profileData: UserProfileUpdate,
    apiUrl = getApiUrl()
): Promise<User> {
    const response = await fetch(`${apiUrl}/auth/users/${userId}/profile`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify(profileData),
    });
    return handleResponse<User>(response) as Promise<User>;
}

// ============================================================================
// COURSE API Functions
// ============================================================================

/**
 * Get all courses
 * @param apiUrl - Base API URL
 * @returns Array of courses
 */
export async function getCourses(apiUrl = getApiUrl()): Promise<Course[]> {
    const response = await fetch(`${apiUrl}/courses`, {
        headers: getAuthHeaders(),
    });
    return handleResponse<Course[]>(response) as Promise<Course[]>;
}

/**
 * Get a single course by ID
 * @param courseId - Course ID
 * @param apiUrl - Base API URL
 * @returns Course object with modules
 */
export async function getCourse(
    courseId: number,
    apiUrl = getApiUrl()
): Promise<CourseDetail> {
    const response = await fetch(`${apiUrl}/courses/${courseId}`, {
        headers: getAuthHeaders(),
    });
    return handleResponse<CourseDetail>(response) as Promise<CourseDetail>;
}

/**
 * Create a new course
 * @param courseData - Course data (title, description)
 * @param apiUrl - Base API URL
 * @returns Created course object
 */
export async function createCourse(
    courseData: CourseCreate,
    apiUrl = getApiUrl()
): Promise<Course> {
    const response = await fetch(`${apiUrl}/courses`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(courseData),
    });
    return handleResponse<Course>(response) as Promise<Course>;
}

/**
 * Update a course
 * @param courseId - Course ID
 * @param courseData - Partial course data to update
 * @param apiUrl - Base API URL
 * @returns Updated course object
 */
export async function patchCourse(
    courseId: number,
    courseData: CourseUpdate,
    apiUrl = getApiUrl()
): Promise<Course> {
    const response = await fetch(`${apiUrl}/courses/${courseId}`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify(courseData),
    });
    return handleResponse<Course>(response) as Promise<Course>;
}

/**
 * Delete a course
 * @param courseId - Course ID
 * @param apiUrl - Base API URL
 * @returns Promise<void>
 */
export async function deleteCourse(
    courseId: number,
    apiUrl = getApiUrl()
): Promise<void> {
    const response = await fetch(`${apiUrl}/courses/${courseId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
    });
    if (!response.ok) {
        throw new Error(`Failed to delete course: ${response.statusText}`);
    }
}

/**
 * Get all courses assigned to a specific group
 * @param groupId - Group ID
 * @param apiUrl - Base API URL
 * @returns Array of courses
 */
export async function getGroupCourses(
    groupId: number,
    apiUrl = getApiUrl()
): Promise<Course[]> {
    const response = await fetch(`${apiUrl}/groups/${groupId}/courses`, {
        headers: getAuthHeaders(),
    });
    return handleResponse<Course[]>(response) as Promise<Course[]>;
}

/**
 * Get all modules in a course
 * @param courseId - Course ID
 * @param apiUrl - Base API URL
 * @returns Array of modules
 */
export async function getCourseModules(
    courseId: number,
    apiUrl = getApiUrl()
): Promise<Module[]> {
    const response = await fetch(`${apiUrl}/courses/${courseId}/modules`, {
        headers: getAuthHeaders(),
    });
    return handleResponse<Module[]>(response) as Promise<Module[]>;
}

// ============================================================================
// MODULE API Functions
// ============================================================================

/**
 * Get all modules
 * @param apiUrl - Base API URL
 * @returns Array of modules
 */
export async function getModules(apiUrl = getApiUrl()): Promise<Module[]> {
    const response = await fetch(`${apiUrl}/modules`, {
        headers: getAuthHeaders(),
    });
    return handleResponse<Module[]>(response) as Promise<Module[]>;
}

/**
 * Get a single module by ID
 * @param moduleId - Module ID
 * @param apiUrl - Base API URL
 * @returns Module object WITHOUT posts
 */
export async function getModule(
    moduleId: number,
    apiUrl = getApiUrl()
): Promise<ModuleDetail> {
    const response = await fetch(`${apiUrl}/modules/${moduleId}`, {
        headers: getAuthHeaders(),
    });
    return handleResponse<ModuleDetail>(response) as Promise<ModuleDetail>;
}

/**
 * Create a new module
 * @param moduleData - Module data (title, description, color)
 * @param apiUrl - Base API URL
 * @returns Created module object
 */
export async function createModule(
    moduleData: ModuleCreate,
    apiUrl = getApiUrl()
): Promise<Module> {
    const response = await fetch(`${apiUrl}/modules`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(moduleData),
    });
    return handleResponse<Module>(response) as Promise<Module>;
}

/**
 * Update a module
 * @param moduleId - Module ID
 * @param moduleData - Partial module data to update
 * @param apiUrl - Base API URL
 * @returns Updated module object
 */
export async function patchModule(
    moduleId: number,
    moduleData: ModuleUpdate,
    apiUrl = getApiUrl()
): Promise<Module> {
    const response = await fetch(`${apiUrl}/modules/${moduleId}`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify(moduleData),
    });
    return handleResponse<Module>(response) as Promise<Module>;
}

/**
 * Delete a module
 * @param moduleId - Module ID
 * @param apiUrl - Base API URL
 * @returns Promise<void>
 */
export async function deleteModule(
    moduleId: number,
    apiUrl = getApiUrl()
): Promise<void> {
    const response = await fetch(`${apiUrl}/modules/${moduleId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
    });
    if (!response.ok) {
        throw new Error(`Failed to delete module: ${response.statusText}`);
    }
}
