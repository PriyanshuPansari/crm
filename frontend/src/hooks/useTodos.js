import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  getTodos, 
  getTodosByOrg, 
  createTodo, 
  createTodoInOrg, 
  updateTodo, 
  updateTodoInOrg,
  deleteTodo, 
  deleteTodoInOrg 
} from "../api/todos";

// Organization-scoped todos hook
export const useTodosByOrg = (orgId) => {
  return useQuery({
    queryKey: ['todos', 'org', orgId],
    queryFn: async () => {
      const response = await getTodosByOrg(orgId);
      return response.data;
    },
    enabled: !!orgId,
  });
};

// Legacy todos hook (uses first organization)
export const useTodos = () => {
  return useQuery({
    queryKey: ['todos'],
    queryFn: async () => {
      const response = await getTodos();
      return response.data;
    },
  });
};

export const useCreateTodoInOrg = (orgId) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data) => createTodoInOrg(orgId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos', 'org', orgId] });
      queryClient.invalidateQueries({ queryKey: ['todos'] }); // Also invalidate legacy
    },
  });
};

export const useCreateTodo = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createTodo,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });
};

export const useUpdateTodo = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ todoId, data }) => updateTodo(todoId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
      // Invalidate all organization-scoped todo queries
      queryClient.invalidateQueries({ queryKey: ['todos', 'org'] });
    },
  });
};

export const useUpdateTodoInOrg = (orgId) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ todoId, data }) => updateTodoInOrg(orgId, todoId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos', 'org', orgId] });
      queryClient.invalidateQueries({ queryKey: ['todos'] }); // Also invalidate legacy
    },
  });
};

export const useDeleteTodo = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: deleteTodo,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
      // Invalidate all organization-scoped todo queries
      queryClient.invalidateQueries({ queryKey: ['todos', 'org'] });
    },
  });
};

export const useDeleteTodoInOrg = (orgId) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (todoId) => deleteTodoInOrg(orgId, todoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos', 'org', orgId] });
      queryClient.invalidateQueries({ queryKey: ['todos'] }); // Also invalidate legacy
    },
  });
};
