export const API_BASE_URL = "http://localhost:8000";


async function handleResponse(response: Response) {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "API request failed");
  }

  return response.json();
}


/**
 * Lance l'analyse d'un repository
 * Retourne un job_id (async system)
 */
export async function loadRepository(repoUrl: string) {
  const response = await fetch(`${API_BASE_URL}/repo/loadTest`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      repo_url: repoUrl,
    }),
  });

  return handleResponse(response);
}


/**
 * Récupère le statut d'un job d'analyse
 */
export async function getJobStatus(jobId: string) {
  const response = await fetch(`${API_BASE_URL}/job/${jobId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  return handleResponse(response);
}

export async function getRepository(repoId: number) {
  const response = await fetch(`http://localhost:8000/repo/${repoId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return handleResponse(response);
}