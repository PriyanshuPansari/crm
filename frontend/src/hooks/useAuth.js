import { useMutation } from "@tanstack/react-query";
import { login as loginApi, signup as signupApi } from "../api/auth";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

export const useLogin = () => {
  const { login } = useContext(AuthContext);

  return useMutation({
    mutationFn: async (credentials) => {
      const res = await loginApi(credentials);
      login(res.data.access_token); // store token in context
      return res.data;
    },
  });
};

export const useSignup = () => {
  const { login } = useContext(AuthContext);

  return useMutation({
    mutationFn: async (data) => {
      const res = await signupApi(data);
      // Signup returns user data directly, we need to create a session
      // For now, we'll need to login after signup since signup doesn't return a token
      return res.data;
    },
  });
};
