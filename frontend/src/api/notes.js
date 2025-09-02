import api from "./client";

// Notes APIs
export const getNotes = () => api.get("/notes/");
export const getNote = (noteId) => api.get(`/notes/${noteId}`);
export const createNote = (data) => api.post("/notes/", data);
export const updateNote = (noteId, data) => api.put(`/notes/${noteId}`, data);
export const deleteNote = (noteId) => api.delete(`/notes/${noteId}`);
