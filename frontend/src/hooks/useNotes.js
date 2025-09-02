import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getNotes, createNote, updateNote, deleteNote } from "../api/notes";

export const useNotes = () => {
  return useQuery({
    queryKey: ['notes'],
    queryFn: async () => {
      const response = await getNotes();
      return response.data;
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
    },
  });
};

export const useDeleteNote = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: deleteNote,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
    },
  });
};
