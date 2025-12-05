import { apiClient } from "./client";
import {
  PetType,
  CreatePetTypeRequest,
  UpdatePetTypeRequest,
  DeletePetTypeResponse,
} from "@/types";

export async function getPetTypes(includeInactive = true): Promise<PetType[]> {
  const response = await apiClient.get<PetType[]>("/admin/pet-types", {
    params: { include_inactive: includeInactive },
  });
  return response.data;
}

export async function createPetType(data: CreatePetTypeRequest): Promise<PetType> {
  const response = await apiClient.post<PetType>("/admin/pet-types", data);
  return response.data;
}

export async function updatePetType(
  petTypeId: number,
  data: UpdatePetTypeRequest
): Promise<PetType> {
  const response = await apiClient.patch<PetType>(
    `/admin/pet-types/${petTypeId}`,
    data
  );
  return response.data;
}

export async function deletePetType(
  petTypeId: number,
  hardDelete = false
): Promise<DeletePetTypeResponse> {
  const response = await apiClient.delete<DeletePetTypeResponse>(
    `/admin/pet-types/${petTypeId}`,
    { params: { hard_delete: hardDelete } }
  );
  return response.data;
}
