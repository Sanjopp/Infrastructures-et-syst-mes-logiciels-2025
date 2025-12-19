export const API_BASE = "/api";

function getAuthHeaders() {
  const token = localStorage.getItem("access_token");
  return token
    ? { Authorization: `Bearer ${token}` }
    : {};
}

async function handleResponse(res, messageOnError = "Une erreur est survenue") {
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.error || messageOnError);
  }

  return data;
}

export async function login(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await handleResponse(res, "Échec de la connexion");

  localStorage.setItem("access_token", data.access_token);

  return data;
}

export function logout() {
  localStorage.removeItem("access_token");
}

export async function register({ name, email, password }) {
  const res = await fetch("/api/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name,
      email,
      password,
    }),
  });

  return handleResponse(res, "Échec de l'inscription");
}

export async function fetchTricounts() {
  const res = await fetch(`${API_BASE}/tricounts`, {
    headers: {
      ...getAuthHeaders(),
    },
  });
  return handleResponse(res);
}

export async function fetchTricountDetail(id) {
  const res = await fetch(`${API_BASE}/tricounts/${id}`, {
    headers: {
      ...getAuthHeaders(),
    },
  });
  return handleResponse(res, "Échec de la récupération des détails du 3Compte");
}

export async function createTricount(name) {
  const res = await fetch(`${API_BASE}/tricounts`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ name }),
  });
  return handleResponse(res, "Échec de la création du 3Compte");
}

export async function deleteTricount(id) {
  const res = await fetch(`${API_BASE}/tricounts/${id}`, {
    method: "DELETE",
    headers: {
      ...getAuthHeaders(),
    },
  });
  return handleResponse(res, "Échec de la suppression du 3Compte");
}

export async function addUser(tricountId, payload) {
  const res = await fetch(`${API_BASE}/tricounts/${tricountId}/users`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(payload),
  });
  return handleResponse(res, "Impossible d'ajouter l'utilisateur");
}

export async function deleteUser(tricountId, userId) {
  const res = await fetch(
    `${API_BASE}/tricounts/${tricountId}/users/${userId}`,
    {
      method: "DELETE",
      headers: {
        ...getAuthHeaders(),
      },
    }
  );
  return handleResponse(res, "Impossible de supprimer l'utilisateur");
}

export async function addExpense(tricountId, payload) {
  const res = await fetch(`${API_BASE}/tricounts/${tricountId}/expenses`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(payload),
  });

  return handleResponse(res, "Impossible d'ajouter la dépense");
}

export async function deleteExpense(tricountId, expenseId) {
  const res = await fetch(
    `${API_BASE}/tricounts/${tricountId}/expenses/${expenseId}`,
    {
      method: "DELETE",
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  return handleResponse(res, "Impossible de supprimer la dépense");
}

export async function exportExcel(tricountId) {
  const res = await fetch(
    `${API_BASE}/tricounts/${tricountId}/export/excel`,
    {
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  return handleResponse(res, "Export impossible");
}

export async function inviteTricount(tricountId) {
  const res = await fetch(
    `${API_BASE}/tricounts/${tricountId}/invite`,
    {
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
      },
    }
  );

  return handleResponse(res, "Invitation impossible");
}

export async function getUsers(tricountId) {
  const res = await fetch(
    `${API_BASE}/tricounts/${tricountId}/users`,
    {
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
      },
    }
  );

  return handleResponse(res, "Impossible de récupérer les utilisateurs");
}

export async function joinTricount(tricountId, payload) {
  const res = await fetch(
    `${API_BASE}/tricounts/${tricountId}/join`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
      },
      body: JSON.stringify(payload),
    }
  );

  return handleResponse(res, "Impossible de rejoindre le 3Compte");
}
