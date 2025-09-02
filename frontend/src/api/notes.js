import api from "./client";

// Organization-scoped Notes APIs
export const getNotesByOrg = (orgId) => api.get(`/notes/org/${orgId}`);
export const createNoteInOrg = (orgId, data) => api.post(`/notes/org/${orgId}`, data);

// Legacy Notes APIs (use first organization)
export const getNotes = () => api.get("/notes/");
export const getNote = (noteId) => api.get(`/notes/${noteId}`);
export const createNote = (data) => api.post("/notes/", data);
export const updateNote = (noteId, data) => api.put(`/notes/${noteId}`, data);
export const deleteNote = (noteId) => api.delete(`/notes/${noteId}`);
