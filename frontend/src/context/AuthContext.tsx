import React, { createContext, useContext, useState } from "react";

interface User {
  username: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem("nirikshan_demo_user");
    return saved ? JSON.parse(saved) : { username: "demo_authority", role: "Authority Reviewer" };
  });

  const login = (username: string) => {
    const newUser = { username: username || "demo_authority", role: "Authority Reviewer" };
    setUser(newUser);
    localStorage.setItem("nirikshan_demo_user", JSON.stringify(newUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("nirikshan_demo_user");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    return {
      user: { username: "demo_authority", role: "Authority Reviewer" },
      login: () => {},
      logout: () => {},
    };
  }
  return context;
};
