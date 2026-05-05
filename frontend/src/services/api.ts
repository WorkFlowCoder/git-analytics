export const API_BASE_URL = "http://localhost:8000";


async function handleResponse(response: Response) {
  if (!response.ok) {
    const errorText = await response.text();
    return {error: errorText};
  }
  return response.json();
}


/**
 * Lance l'analyse d'un repository
 * Retourne un job_id (async system)
 */
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

/**
 * Récupère le détail d'un repository analysé
 */
export async function getRepository(repoId: number) {
  const response = await fetch(`${API_BASE_URL}/repo/${repoId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return handleResponse(response);
}

/**
 * Récupère la timeline d'un repository analysé
 */
export async function getRepositoryTimeline(repoId: number, page: number = 1) {
  const response = await fetch(`${API_BASE_URL}/repo/timeline/${repoId}/${page}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return handleResponse(response);
}

/**
 * Récupère le graph de dépendances d'un repository analysé
 */
export async function getRepositoryGraph(repoId: number) {
  const response = await fetch(`${API_BASE_URL}/repo/${repoId}/dependency-graph`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return handleResponse(response);
}

/**
 * Récupère la liste de tous les repositories analysés
 */
export async function getAllRepositories() {
  const response = await fetch(`${API_BASE_URL}/repo`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return handleResponse(response);
}

/**
 * Suppression d'un répertoire
 */
export async function deleteRepository(id: number) {
  const res = await fetch(`${API_BASE_URL}/repo/${id}`, {
    method: "DELETE",
  });
  return handleResponse(res);
}


/**
 * Relance d'une analyse
 */
export async function reanalyzeRepository(id: number) {
  const res = await fetch(`${API_BASE_URL}/repo/${id}/reanalyze`, {
    method: "POST",
  });
  return handleResponse(res);
}