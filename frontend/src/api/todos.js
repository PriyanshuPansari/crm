import api from "./client";

// Todo APIs
export const getTodos = () => api.get("/todos/");
export const getTodo = (todoId) => api.get(`/todos/${todoId}`);
export const createTodo = (data) => api.post("/todos/", data);
export const updateTodo = (todoId, data) => api.put(`/todos/${todoId}`, data);
export const deleteTodo = (todoId) => api.delete(`/todos/${todoId}`);
