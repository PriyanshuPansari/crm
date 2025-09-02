import api from "./client";

// Organization-scoped Todo APIs
export const getTodosByOrg = (orgId) => api.get(`/todos/org/${orgId}`);
export const createTodoInOrg = (orgId, data) => api.post(`/todos/org/${orgId}`, data);
export const updateTodoInOrg = (orgId, todoId, data) => api.put(`/todos/org/${orgId}/${todoId}`, data);
export const deleteTodoInOrg = (orgId, todoId) => api.delete(`/todos/org/${orgId}/${todoId}`);

// Legacy Todo APIs (use first organization)
export const getTodos = () => api.get("/todos/");
export const getTodo = (todoId) => api.get(`/todos/${todoId}`);
export const createTodo = (data) => api.post("/todos/", data);
export const updateTodo = (todoId, data) => api.put(`/todos/${todoId}`, data);
export const deleteTodo = (todoId) => api.delete(`/todos/${todoId}`);
