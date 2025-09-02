import api from "./client";

// Organization APIs
export const createOrganization = (data) => api.post("/organizations/", data);

// Get all organizations the user belongs to
export const getMyOrganizations = () => api.get("/organizations/my");

// Legacy endpoint for backward compatibility (returns all organizations, but we'll take first)
export const getMyOrganization = () => api.get("/organizations/my");

// Organization-scoped endpoints (new many-to-many structure)
export const inviteUser = (orgId, data) => {
  console.log('Inviting user to org:', orgId, 'with data:', data);
  return api.post(`/organizations/${orgId}/invite`, data);
};

export const updateUserRole = (orgId, userId, data) => 
  api.put(`/organizations/${orgId}/members/${userId}/role`, data);

export const removeMember = (orgId, userId) => 
  api.delete(`/organizations/${orgId}/members/${userId}`);

export const deleteOrganization = (orgId) => 
  api.delete(`/organizations/${orgId}`);

export const getOrganizationMembers = (orgId) => 
  api.get(`/organizations/${orgId}/members`);

// Get specific organization details
export const getOrganization = (orgId) => 
  api.get(`/organizations/${orgId}`);
