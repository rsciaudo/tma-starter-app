import { apiClient } from './api';
import { ModuleDetail } from '../types/api';

export async function getModuleDetail(moduleId: number): Promise<ModuleDetail> {
    const response = await apiClient.get<ModuleDetail>(
        `/api/modules/${moduleId}`
    );

    return response.data;
}
