export interface UserRef {
  id: number;
  username: string;
}

export interface GroupRef {
  id: number;
  name: string;
}

export interface LabelItem {
  id: number;
  name: string;
  color: string;
  is_ticket_label: boolean;
}

export interface TeamItem {
  id: number;
  name: string;
}

export interface CardComment {
  id: number;
  author: UserRef | null;
  text: string;
  text_html: string;
  created_at: string;
}

export interface KanbanCard {
  id: number;
  list_id: number;
  title: string;
  description: string;
  description_html: string;
  order: number;
  color: string;
  due_date: string | null;
  is_archived: boolean;
  created_by: UserRef | null;
  created_at: string;
  updated_at: string;
  assigned_team: TeamItem | null;
  labels: LabelItem[];
  assignees: UserRef[];
  comment_count: number;
  discord_thread_id: number | null;
  comments?: CardComment[];
}

export interface ArchivedCard extends KanbanCard {
  list_name: string;
  archived_at: string | null;
}

export interface KanbanList {
  id: number;
  name: string;
  description: string;
  wip_limit: number;
  order: number;
  can_add_card: boolean;
}

export interface BoardSummary {
  id: number;
  name: string;
  slug: string;
  description: string;
  is_members_board: boolean;
  is_ticket_board: boolean;
  own_cards_only: boolean;
  list_count: number;
  card_count: number;
  attention_count: number;
  can_write: boolean;
  updated_at: string;
}

export interface ArchivedBoardSummary {
  id: number;
  name: string;
  slug: string;
  description: string;
  card_count: number;
  archived_at: string | null;
  created_by: UserRef | null;
}

export interface BoardDetail {
  board: {
    id: number;
    name: string;
    slug: string;
    description: string;
    is_archived: boolean;
    is_members_board: boolean;
    is_ticket_board: boolean;
    own_cards_only: boolean;
    discord_ticket_channel_id?: number | null;
    discord_alert_channel_id?: number | null;
    discord_alert_webhook?: string;
    discord_webhook_cards?: string;
    stale_card_alert_hours?: number;
    stale_card_repeat_hours?: number;
    archive_after_days?: number;
    view_group_ids?: number[];
    write_group_ids?: number[];
    can_write: boolean;
    can_manage: boolean;
  };
  lists: KanbanList[];
  cards: KanbanCard[];
  labels: LabelItem[];
  teams: TeamItem[];
  users: UserRef[];
  all_groups?: GroupRef[];
}

export interface SearchResult {
  id: number;
  title: string;
  board_name: string;
  board_slug: string;
  list_name: string;
  is_archived: boolean;
  labels: LabelItem[];
}

export interface SummaryBoard {
  id: number;
  name: string;
  slug: string;
  total_cards: number;
  lists: {
    id: number;
    name: string;
    wip_limit: number;
    cards: {
      id: number;
      title: string;
      due_date: string | null;
      labels: LabelItem[];
      assignees: UserRef[];
    }[];
  }[];
}

export interface SettingsGroup {
  id: number;
  name: string;
  can_manage_boards: boolean;
  members: UserRef[];
  auth_groups: GroupRef[];
}

export interface SettingsTeam {
  id: number;
  name: string;
  discord_role_id: string;
  ticket_board_id: number | null;
  ticket_board_name: string;
  members: UserRef[];
  auth_groups: GroupRef[];
}

export interface SettingsPayload {
  groups: SettingsGroup[];
  teams: SettingsTeam[];
  labels: LabelItem[];
  global_settings: {
    board_creation_webhook: string;
    members_page_name: string;
  };
  boards: { id: number; name: string; is_ticket_board: boolean }[];
  all_users: UserRef[];
  all_auth_groups: GroupRef[];
}
