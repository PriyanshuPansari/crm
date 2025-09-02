import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  getMyOrganization, 
  createOrganization, 
  inviteUser, 
  updateUserRole, 
  removeMember,
  deleteOrganization,
  getOrganizationMembers
} from "../api/organizations";

export const useMyOrganization = () => {
  return useQuery({
    queryKey: ['myOrganization'],
    queryFn: async () => {
      const response = await getMyOrganization();
      return response.data;
    },
    retry: false, // Don't retry if user doesn't have an organization
  });
};

export const useCreateOrganization = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createOrganization,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myOrganization'] });
    },
  });
};

export const useInviteUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: inviteUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myOrganization'] });
      queryClient.invalidateQueries({ queryKey: ['organizationMembers'] });
    },
  });
};

export const useUpdateUserRole = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ userId, role }) => updateUserRole(userId, { role }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myOrganization'] });
      queryClient.invalidateQueries({ queryKey: ['organizationMembers'] });
    },
  });
};

export const useRemoveMember = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: removeMember,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myOrganization'] });
      queryClient.invalidateQueries({ queryKey: ['organizationMembers'] });
    },
  });
};
