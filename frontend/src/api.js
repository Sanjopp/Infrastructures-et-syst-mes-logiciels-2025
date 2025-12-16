export const API_BASE = "/api";

async function handleResponse(res) {
  let data;
  try {
    data = await res.json();
  } catch {
    throw new Error(`HTTP ${res.status}`);
  }

  if (!res.ok) {
    throw new Error(data.error || `HTTP ${res.status}`);
  }
  return data;
}

export async function fetchTricounts() {
  const res = await fetch(`${API_BASE}/api/tricounts`);
  return handleResponse(res);
}

export async function fetchTricountDetail(id) {
  const res = await fetch(`${API_BASE}/api/tricounts/${id}`);
  return handleResponse(res);
}

export async function createTricount(name) {
  const res = await fetch(`${API_BASE}/api/tricounts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  return handleResponse(res);
}

export async function addUser(tricountId, { name, email }) {
  const res = await fetch(`${API_BASE}/api/tricounts/${tricountId}/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email }),
  });
  return handleResponse(res);
}

export async function addExpense(tricountId, payload) {
  const res = await fetch(`${API_BASE}/api/tricounts/${tricountId}/expenses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}
