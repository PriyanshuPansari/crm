import api from "./client";

export const signup = (data) => api.post("/auth/signup", data);

export const login = (data) => {
  // OAuth2PasswordRequestForm expects form data, not JSON
  const formData = new FormData();
  formData.append('username', data.username);
  formData.append('password', data.password);
  
  return api.post("/auth/login", formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
};

export const me = () => api.get("/auth/me");
