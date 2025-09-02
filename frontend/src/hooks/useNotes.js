import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getNotes, getNotesByOrg, createNote, createNoteInOrg, updateNote, deleteNote } from "../api/notes";

// Organization-scoped notes hook
export const useNotesByOrg = (orgId) => {
  return useQuery({
    queryKey: ['notes', 'org', orgId],
    queryFn: async () => {
      const response = await getNotesByOrg(orgId);
      return response.data;
    },
    enabled: !!orgId,
  });
};

// Legacy notes hook (uses first organization)
export const useNotes = () => {
  return useQuery({
    queryKey: ['notes'],
    queryFn: async () => {
      const response = await getNotes();
      return response.data;
    },
  });
};

export const useCreateNoteInOrg = (orgId) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data) => createNoteInOrg(orgId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes', 'org', orgId] });
      queryClient.invalidateQueries({ queryKey: ['notes'] }); // Also invalidate legacy
    },
  });
};

export const useCreateNote = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createNote,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
    },
  });
};

export const useUpdateNote = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ noteId, data }) => updateNote(noteId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
      // Invalidate all organization-scoped note queries
      queryClient.invalidateQueries({ queryKey: ['notes', 'org'] });
    },
  });
};

export const useDeleteNote = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: deleteNote,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
      // Invalidate all organization-scoped note queries
      queryClient.invalidateQueries({ queryKey: ['notes', 'org'] });
    },
  });
};
