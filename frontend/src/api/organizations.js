import api from "./client";

// Organization APIs
export const createOrganization = (data) => api.post("/organizations/", data);
export const getMyOrganization = () => api.get("/organizations/my");

export const inviteUser = (data) => {
  console.log('Inviting user with data:', data);
  return api.post("/organizations/invite", data);
};

export const updateUserRole = (userId, data) => api.put(`/organizations/members/${userId}/role`, data);
export const removeMember = (userId) => api.delete(`/organizations/members/${userId}`);
export const deleteOrganization = () => api.delete("/organizations/");
export const getOrganizationMembers = () => api.get("/organizations/members");
