import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  getMyOrganizations,
  getMyOrganization, 
  getOrganization,
  createOrganization, 
  inviteUser, 
  updateUserRole, 
  removeMember,
  deleteOrganization,
  getOrganizationMembers
} from "../api/organizations";

// Get all organizations the user belongs to
export const useMyOrganizations = () => {
  return useQuery({
    queryKey: ['myOrganizations'],
    queryFn: async () => {
      const response = await getMyOrganizations();
      return response.data;
    },
    retry: false,
  });
};

// Legacy hook - returns first organization for backward compatibility
export const useMyOrganization = () => {
  return useQuery({
    queryKey: ['myOrganization'],
    queryFn: async () => {
      const response = await getMyOrganizations();
      const organizations = response.data;
      // Return first organization for backward compatibility
      return organizations && organizations.length > 0 ? organizations[0] : null;
    },
    retry: false, // Don't retry if user doesn't have an organization
  });
};

// Get specific organization details
export const useOrganization = (orgId) => {
  return useQuery({
    queryKey: ['organization', orgId],
    queryFn: async () => {
      const response = await getOrganization(orgId);
      return response.data;
    },
    enabled: !!orgId,
  });
};

export const useCreateOrganization = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createOrganization,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myOrganizations'] });
      queryClient.invalidateQueries({ queryKey: ['myOrganization'] });
    },
  });
};

export const useInviteUser = (orgId) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data) => inviteUser(orgId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myOrganizations'] });
      queryClient.invalidateQueries({ queryKey: ['myOrganization'] });
      queryClient.invalidateQueries({ queryKey: ['organizationMembers', orgId] });
      queryClient.invalidateQueries({ queryKey: ['organization', orgId] });
    },
  });
};

export const useUpdateUserRole = (orgId) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ userId, role }) => updateUserRole(orgId, userId, { role }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myOrganizations'] });
      queryClient.invalidateQueries({ queryKey: ['myOrganization'] });
      queryClient.invalidateQueries({ queryKey: ['organizationMembers', orgId] });
      queryClient.invalidateQueries({ queryKey: ['organization', orgId] });
    },
  });
};

export const useRemoveMember = (orgId) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (userId) => removeMember(orgId, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myOrganizations'] });
      queryClient.invalidateQueries({ queryKey: ['myOrganization'] });
      queryClient.invalidateQueries({ queryKey: ['organizationMembers', orgId] });
      queryClient.invalidateQueries({ queryKey: ['organization', orgId] });
    },
  });
};

export const useDeleteOrganization = (orgId) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () => deleteOrganization(orgId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myOrganizations'] });
      queryClient.invalidateQueries({ queryKey: ['myOrganization'] });
      queryClient.removeQueries({ queryKey: ['organization', orgId] });
      queryClient.removeQueries({ queryKey: ['organizationMembers', orgId] });
    },
  });
};

export const useOrganizationMembers = (orgId) => {
  return useQuery({
    queryKey: ['organizationMembers', orgId],
    queryFn: async () => {
      const response = await getOrganizationMembers(orgId);
      return response.data;
    },
    enabled: !!orgId,
  });
};
