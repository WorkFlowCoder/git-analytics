export const API_BASE_URL = "http://localhost:8000";

export async function loadRepository(repoUrl: string) {
  const response = await fetch(`${API_BASE_URL}/repo/load`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      repo_url: repoUrl,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to load repository");
  }

  return response.json();
}