import type {
  ArchivedBoardSummary,
  ArchivedCard,
  BoardDetail,
  BoardSummary,
  CardComment,
  GroupRef,
  KanbanCard,
  KanbanList,
  LabelItem,
  SearchResult,
  SettingsPayload,
  SummaryBoard,
  UserRef,
} from "@/types";

export interface SpaConfig {
  apiBoardsUrl: string;
  apiPrefix: string;
  spaBase: string;
  classicUrl: string;
  settingsUrl: string;
  ticketUrl: string;
  appName: string;
  csrfToken: string;
}

export function getSpaConfig(): SpaConfig {
  const root = document.getElementById("aa-kanban-spa");
  const apiBoardsUrl = root?.dataset.apiBase || "/kanban/api/v1/boards/";
  const apiPrefix = apiBoardsUrl.replace(/boards\/?$/, "");
  return {
    apiBoardsUrl,
    apiPrefix,
    spaBase: root?.dataset.spaBase || "/kanban/",
    classicUrl: root?.dataset.classicUrl || "/kanban/?classic=1",
    settingsUrl: root?.dataset.settingsUrl || "/kanban/settings/",
    ticketUrl: root?.dataset.ticketUrl || "/kanban/tickets/create/",
    appName: root?.dataset.appName || "Kanban",
    csrfToken: root?.dataset.csrfToken || getCsrfFromCookie(),
  };
}

function getCsrfFromCookie(): string {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  const config = getSpaConfig();
  const headers = new Headers(init?.headers);
  if (init?.method && init.method !== "GET") {
    headers.set("X-CSRFToken", config.csrfToken);
    if (!headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
  }
  const resp = await fetch(url, {
    credentials: "same-origin",
    ...init,
    headers,
  });
  const payload = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(payload.error || `Request failed (${resp.status})`);
  }
  return payload as T;
}

export async function uploadImage(
  file: File
): Promise<{ id: number; url: string; filename: string; markdown: string }> {
  const { apiPrefix, csrfToken } = getSpaConfig();
  const uploadUrl = `${apiPrefix.replace(/v1\/$/, "")}upload-image/`;
  const formData = new FormData();
  formData.append("image", file, file.name || "pasted-image.png");
  const resp = await fetch(uploadUrl, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": csrfToken,
    },
    body: formData,
  });
  const payload = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(payload.error || `Image upload failed (${resp.status})`);
  }
  return payload as { id: number; url: string; filename: string; markdown: string };
}

export async function fetchBoards(): Promise<{
  boards: BoardSummary[];
  can_manage: boolean;
  can_create_ticket: boolean;
  archived_count: number;
  all_groups: GroupRef[];
  user: UserRef | null;
}> {
  const { apiBoardsUrl } = getSpaConfig();
  return requestJson(apiBoardsUrl);
}

export async function createBoard(data: Record<string, unknown>): Promise<{
  board: { id: number; name: string; slug: string; description: string };
}> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}boards/create/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function editBoard(
  boardSlug: string,
  data: Record<string, unknown>
): Promise<{ ok: boolean; slug: string }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}boards/${encodeURIComponent(boardSlug)}/edit/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function archiveBoard(boardSlug: string): Promise<{ ok: boolean }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(
    `${apiPrefix}boards/${encodeURIComponent(boardSlug)}/archive/`,
    { method: "POST", body: JSON.stringify({}) }
  );
}

export async function restoreBoard(boardSlug: string): Promise<{ ok: boolean }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(
    `${apiPrefix}boards/${encodeURIComponent(boardSlug)}/restore/`,
    { method: "POST", body: JSON.stringify({}) }
  );
}

export async function deleteBoard(boardSlug: string): Promise<{ ok: boolean }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(
    `${apiPrefix}boards/${encodeURIComponent(boardSlug)}/delete/`,
    { method: "POST", body: JSON.stringify({}) }
  );
}

export async function fetchArchivedBoards(): Promise<{
  boards: ArchivedBoardSummary[];
}> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}boards/archived/`);
}

export async function fetchBoardDetail(slug: string): Promise<BoardDetail> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}boards/${encodeURIComponent(slug)}/`);
}

export async function createList(
  boardSlug: string,
  data: { name: string; description?: string; wip_limit?: number }
): Promise<{ list: KanbanList }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(
    `${apiPrefix}boards/${encodeURIComponent(boardSlug)}/lists/create/`,
    {
      method: "POST",
      body: JSON.stringify(data),
    }
  );
}

export async function editList(
  listId: number,
  data: { name: string; description?: string; wip_limit?: number }
): Promise<{ list: KanbanList }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}lists/${listId}/edit/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteList(listId: number): Promise<{ ok: boolean }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}lists/${listId}/delete/`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export async function createCard(
  listId: number,
  data: { title: string; description?: string }
): Promise<{ card: KanbanCard }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}lists/${listId}/cards/create/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function fetchCardDetail(
  cardId: number
): Promise<{ card: KanbanCard }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}cards/${cardId}/`);
}

export async function updateCard(
  cardId: number,
  data: {
    title?: string;
    description?: string;
    color?: string;
    due_date?: string | null;
    assigned_team_id?: number | null;
    label_ids?: number[];
    assignee_ids?: number[];
  }
): Promise<{ card: KanbanCard }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}cards/${cardId}/update/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function moveCard(
  cardId: number,
  targetListId: number,
  newPosition: number
): Promise<{ ok: boolean; prompt_close_thread?: boolean }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}cards/${cardId}/move/`, {
    method: "POST",
    body: JSON.stringify({
      target_list_id: targetListId,
      new_position: newPosition,
    }),
  });
}

export async function closeCardThread(cardId: number): Promise<{ ok: boolean }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}cards/${cardId}/close-thread/`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export async function deleteCard(cardId: number): Promise<{ ok: boolean }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}cards/${cardId}/delete/`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export async function fetchArchivedCards(boardSlug: string): Promise<{
  board_name: string;
  board_slug: string;
  can_write: boolean;
  cards: ArchivedCard[];
}> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(
    `${apiPrefix}boards/${encodeURIComponent(boardSlug)}/archived-cards/`
  );
}

export async function restoreCard(cardId: number): Promise<{ ok: boolean }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}cards/${cardId}/restore/`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export async function addComment(
  cardId: number,
  text: string
): Promise<{ comment: CardComment }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}cards/${cardId}/comments/add/`, {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export async function searchCards(
  query: string,
  includeArchived = false
): Promise<{ results: SearchResult[]; truncated: boolean }> {
  const { apiPrefix } = getSpaConfig();
  const params = new URLSearchParams({ q: query });
  if (includeArchived) params.set("archived", "1");
  return requestJson(`${apiPrefix}search/?${params.toString()}`);
}

export async function fetchSummary(): Promise<{ boards: SummaryBoard[] }> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}summary/`);
}

export async function fetchTicketOptions(): Promise<{
  teams: { id: number; name: string; board_name: string }[];
  labels: LabelItem[];
}> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}tickets/options/`);
}

export async function createTicket(data: {
  title: string;
  description: string;
  assigned_team_id: number;
  label_id?: number | null;
}): Promise<{
  ok: boolean;
  card_id: number;
  board_slug: string;
  board_name: string;
}> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}tickets/create/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function fetchSettings(): Promise<SettingsPayload> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}settings/`);
}

export async function updateGlobalSettings(data: {
  board_creation_webhook: string;
  members_page_name: string;
}): Promise<SettingsPayload> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}settings/global/update/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function saveGroup(data: {
  id?: number;
  name: string;
  can_manage_boards: boolean;
  member_ids: number[];
  auth_group_ids: number[];
}): Promise<SettingsPayload> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}settings/groups/save/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteGroup(groupId: number): Promise<SettingsPayload> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}settings/groups/${groupId}/delete/`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export async function saveTeam(data: {
  id?: number;
  name: string;
  discord_role_id: string;
  ticket_board_id: number | null;
  member_ids: number[];
  auth_group_ids: number[];
}): Promise<SettingsPayload> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}settings/teams/save/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteTeam(teamId: number): Promise<SettingsPayload> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}settings/teams/${teamId}/delete/`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export async function saveLabel(data: {
  id?: number;
  name: string;
  color: string;
  is_ticket_label: boolean;
}): Promise<SettingsPayload> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}settings/labels/save/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteLabel(labelId: number): Promise<SettingsPayload> {
  const { apiPrefix } = getSpaConfig();
  return requestJson(`${apiPrefix}settings/labels/${labelId}/delete/`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}
