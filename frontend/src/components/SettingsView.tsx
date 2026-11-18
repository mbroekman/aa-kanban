import { useEffect, useState } from "react";
import { Loader2, Pencil, Plus, Settings, Tag, Trash2, Users } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  deleteGroup,
  deleteLabel,
  deleteTeam,
  fetchSettings,
  saveGroup,
  saveLabel,
  saveTeam,
  updateGlobalSettings,
} from "@/lib/api";
import { cn } from "@/lib/utils";
import type {
  LabelItem,
  SettingsGroup,
  SettingsPayload,
  SettingsTeam,
} from "@/types";

const LABEL_COLORS = [
  "primary",
  "secondary",
  "success",
  "danger",
  "warning",
  "info",
  "dark",
];

export function SettingsView() {
  const [data, setData] = useState<SettingsPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Global settings
  const [webhook, setWebhook] = useState("");
  const [membersPageName, setMembersPageName] = useState("Member Boards");

  // Group modal
  const [groupOpen, setGroupOpen] = useState(false);
  const [editGroupId, setEditGroupId] = useState<number | undefined>();
  const [groupName, setGroupName] = useState("");
  const [groupManageBoards, setGroupManageBoards] = useState(false);
  const [groupMemberIds, setGroupMemberIds] = useState<number[]>([]);
  const [groupAuthIds, setGroupAuthIds] = useState<number[]>([]);

  // Team modal
  const [teamOpen, setTeamOpen] = useState(false);
  const [editTeamId, setEditTeamId] = useState<number | undefined>();
  const [teamName, setTeamName] = useState("");
  const [teamDiscordRole, setTeamDiscordRole] = useState("");
  const [teamTicketBoardId, setTeamTicketBoardId] = useState<string>("");
  const [teamMemberIds, setTeamMemberIds] = useState<number[]>([]);
  const [teamAuthIds, setTeamAuthIds] = useState<number[]>([]);

  // Label modal
  const [labelOpen, setLabelOpen] = useState(false);
  const [editLabelId, setEditLabelId] = useState<number | undefined>();
  const [labelName, setLabelName] = useState("");
  const [labelColor, setLabelColor] = useState("primary");
  const [labelIsTicket, setLabelIsTicket] = useState(false);

  const applyPayload = (payload: SettingsPayload) => {
    setData(payload);
    setWebhook(payload.global_settings.board_creation_webhook);
    setMembersPageName(payload.global_settings.members_page_name);
  };

  useEffect(() => {
    fetchSettings()
      .then(applyPayload)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Failed to load settings.")
      )
      .finally(() => setLoading(false));
  }, []);

  const toggleId = (arr: number[], id: number) =>
    arr.includes(id) ? arr.filter((x) => x !== id) : [...arr, id];

  const openGroupModal = (g?: SettingsGroup) => {
    setEditGroupId(g?.id);
    setGroupName(g?.name || "");
    setGroupManageBoards(g?.can_manage_boards || false);
    setGroupMemberIds(g?.members.map((m) => m.id) || []);
    setGroupAuthIds(g?.auth_groups.map((ag) => ag.id) || []);
    setGroupOpen(true);
  };

  const openTeamModal = (t?: SettingsTeam) => {
    setEditTeamId(t?.id);
    setTeamName(t?.name || "");
    setTeamDiscordRole(t?.discord_role_id || "");
    setTeamTicketBoardId(t?.ticket_board_id ? String(t.ticket_board_id) : "");
    setTeamMemberIds(t?.members.map((m) => m.id) || []);
    setTeamAuthIds(t?.auth_groups.map((ag) => ag.id) || []);
    setTeamOpen(true);
  };

  const openLabelModal = (l?: LabelItem) => {
    setEditLabelId(l?.id);
    setLabelName(l?.name || "");
    setLabelColor(l?.color || "primary");
    setLabelIsTicket(l?.is_ticket_label || false);
    setLabelOpen(true);
  };

  const handleSaveGlobal = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      applyPayload(
        await updateGlobalSettings({
          board_creation_webhook: webhook,
          members_page_name: membersPageName,
        })
      );
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to save settings.");
    } finally {
      setSaving(false);
    }
  };

  const handleSaveGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      applyPayload(
        await saveGroup({
          id: editGroupId,
          name: groupName.trim(),
          can_manage_boards: groupManageBoards,
          member_ids: groupMemberIds,
          auth_group_ids: groupAuthIds,
        })
      );
      setGroupOpen(false);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to save group.");
    } finally {
      setSaving(false);
    }
  };

  const handleSaveTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      applyPayload(
        await saveTeam({
          id: editTeamId,
          name: teamName.trim(),
          discord_role_id: teamDiscordRole.trim(),
          ticket_board_id: teamTicketBoardId ? Number(teamTicketBoardId) : null,
          member_ids: teamMemberIds,
          auth_group_ids: teamAuthIds,
        })
      );
      setTeamOpen(false);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to save team.");
    } finally {
      setSaving(false);
    }
  };

  const handleSaveLabel = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      applyPayload(
        await saveLabel({
          id: editLabelId,
          name: labelName.trim(),
          color: labelColor,
          is_ticket_label: labelIsTicket,
        })
      );
      setLabelOpen(false);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to save label.");
    } finally {
      setSaving(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center py-20 gap-2 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        <span className="text-sm">Loading settings...</span>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold m-0 flex items-center gap-2">
          <Settings className="h-5 w-5 text-primary" />
          Kanban Settings
        </h1>
        <p className="text-xs text-muted-foreground m-0 mt-0.5">
          Manage access groups, ticket teams, global labels, and workspace configuration.
        </p>
      </div>

      {error && (
        <div className="rounded-md border border-destructive/50 bg-destructive/15 px-3 py-2 text-xs text-red-700 dark:text-red-200">
          {error}
        </div>
      )}

      <Tabs defaultValue="groups">
        <TabsList>
          <TabsTrigger value="groups">Groups ({data.groups.length})</TabsTrigger>
          <TabsTrigger value="teams">Teams ({data.teams.length})</TabsTrigger>
          <TabsTrigger value="labels">Labels ({data.labels.length})</TabsTrigger>
          <TabsTrigger value="global">Global</TabsTrigger>
        </TabsList>

        {/* Groups Tab */}
        <TabsContent value="groups" className="space-y-3 pt-2">
          <div className="flex justify-end">
            <Button size="sm" onClick={() => openGroupModal()}>
              <Plus className="h-3.5 w-3.5" />
              New Group
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {data.groups.map((g) => (
              <Card key={g.id}>
                <CardHeader className="pb-2 flex-row items-center justify-between space-y-0">
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-sm">{g.name}</CardTitle>
                    {g.can_manage_boards && (
                      <Badge variant="default" className="text-[10px]">
                        Board Manager
                      </Badge>
                    )}
                  </div>
                  <div className="flex gap-1">
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => openGroupModal(g)}
                    >
                      <Pencil className="h-3.5 w-3.5" />
                    </Button>
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={async () => applyPayload(await deleteGroup(g.id))}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="text-xs text-muted-foreground space-y-1">
                  <div>
                    Users: {g.members.length > 0 ? g.members.map((m) => m.username).join(", ") : "None"}
                  </div>
                  <div>
                    Auth Groups:{" "}
                    {g.auth_groups.length > 0
                      ? g.auth_groups.map((ag) => ag.name).join(", ")
                      : "None"}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Teams Tab */}
        <TabsContent value="teams" className="space-y-3 pt-2">
          <div className="flex justify-end">
            <Button size="sm" onClick={() => openTeamModal()}>
              <Plus className="h-3.5 w-3.5" />
              New Team
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {data.teams.map((t) => (
              <Card key={t.id}>
                <CardHeader className="pb-2 flex-row items-center justify-between space-y-0">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-sky-600 dark:text-sky-400" />
                    <CardTitle className="text-sm">{t.name}</CardTitle>
                  </div>
                  <div className="flex gap-1">
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => openTeamModal(t)}
                    >
                      <Pencil className="h-3.5 w-3.5" />
                    </Button>
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={async () => applyPayload(await deleteTeam(t.id))}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="text-xs text-muted-foreground space-y-1">
                  <div>
                    Ticket Board: {t.ticket_board_name || "Not configured"}
                  </div>
                  <div>
                    Users: {t.members.length > 0 ? t.members.map((m) => m.username).join(", ") : "None"}
                  </div>
                  <div>
                    Auth Groups:{" "}
                    {t.auth_groups.length > 0
                      ? t.auth_groups.map((ag) => ag.name).join(", ")
                      : "None"}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Labels Tab */}
        <TabsContent value="labels" className="space-y-3 pt-2">
          <div className="flex justify-end">
            <Button size="sm" onClick={() => openLabelModal()}>
              <Plus className="h-3.5 w-3.5" />
              New Label
            </Button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {data.labels.map((lbl) => (
              <Card key={lbl.id}>
                <CardHeader className="py-3 flex-row items-center justify-between space-y-0">
                  <div className="flex items-center gap-2">
                    <Tag className="h-3.5 w-3.5 text-primary" />
                    <span className="text-sm font-medium">{lbl.name}</span>
                    <Badge variant="outline" className="text-[10px]">
                      {lbl.color}
                    </Badge>
                    {lbl.is_ticket_label && (
                      <Badge variant="secondary" className="text-[10px]">
                        Ticket
                      </Badge>
                    )}
                  </div>
                  <div className="flex gap-1">
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => openLabelModal(lbl)}
                    >
                      <Pencil className="h-3.5 w-3.5" />
                    </Button>
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={async () => applyPayload(await deleteLabel(lbl.id))}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </CardHeader>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Global Tab */}
        <TabsContent value="global" className="pt-2">
          <Card className="max-w-xl">
            <CardHeader>
              <CardTitle className="text-base">Global Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSaveGlobal} className="space-y-4">
                <div>
                  <label className="text-xs font-medium text-muted-foreground block mb-1">
                    Members Page Menu Name
                  </label>
                  <Input
                    value={membersPageName}
                    onChange={(e) => setMembersPageName(e.target.value)}
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground block mb-1">
                    Board Creation Discord Webhook URL
                  </label>
                  <Input
                    value={webhook}
                    onChange={(e) => setWebhook(e.target.value)}
                    placeholder="https://discord.com/api/webhooks/..."
                  />
                </div>
                <Button type="submit" disabled={saving}>
                  {saving ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    "Save Global Settings"
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Group Dialog */}
      <Dialog open={groupOpen} onOpenChange={setGroupOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editGroupId ? "Edit Group" : "New Group"}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSaveGroup} className="space-y-4">
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                Group Name
              </label>
              <Input
                autoFocus
                value={groupName}
                onChange={(e) => setGroupName(e.target.value)}
              />
            </div>
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={groupManageBoards}
                onChange={(e) => setGroupManageBoards(e.target.checked)}
              />
              <span>Members can manage boards &amp; settings</span>
            </label>
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                Users
              </label>
              <div className="flex flex-wrap gap-1 max-h-28 overflow-y-auto rounded-md border border-border p-2">
                {data.all_users.map((u) => (
                  <button
                    key={u.id}
                    type="button"
                    onClick={() =>
                      setGroupMemberIds((prev) => toggleId(prev, u.id))
                    }
                    className={cn(
                      "rounded px-2 py-0.5 text-xs border cursor-pointer",
                      groupMemberIds.includes(u.id)
                        ? "bg-primary/20 border-primary text-foreground"
                        : "bg-transparent border-border text-muted-foreground"
                    )}
                  >
                    {u.username}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                Alliance Auth Groups
              </label>
              <div className="flex flex-wrap gap-1 max-h-28 overflow-y-auto rounded-md border border-border p-2">
                {data.all_auth_groups.map((ag) => (
                  <button
                    key={ag.id}
                    type="button"
                    onClick={() =>
                      setGroupAuthIds((prev) => toggleId(prev, ag.id))
                    }
                    className={cn(
                      "rounded px-2 py-0.5 text-xs border cursor-pointer",
                      groupAuthIds.includes(ag.id)
                        ? "bg-primary/20 border-primary text-foreground"
                        : "bg-transparent border-border text-muted-foreground"
                    )}
                  >
                    {ag.name}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="ghost"
                onClick={() => setGroupOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={saving || !groupName.trim()}>
                Save Group
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Team Dialog */}
      <Dialog open={teamOpen} onOpenChange={setTeamOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editTeamId ? "Edit Team" : "New Team"}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSaveTeam} className="space-y-4">
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                Team Name
              </label>
              <Input
                autoFocus
                value={teamName}
                onChange={(e) => setTeamName(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-muted-foreground block mb-1">
                  Ticket Board
                </label>
                <select
                  value={teamTicketBoardId}
                  onChange={(e) => setTeamTicketBoardId(e.target.value)}
                  className="flex h-9 w-full rounded-md border border-input bg-background px-2 text-xs text-foreground"
                >
                  <option value="">None</option>
                  {data.boards
                    .filter((b) => b.is_ticket_board)
                    .map((b) => (
                      <option key={b.id} value={b.id}>
                        {b.name}
                      </option>
                    ))}
                </select>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground block mb-1">
                  Discord Role ID
                </label>
                <Input
                  value={teamDiscordRole}
                  onChange={(e) => setTeamDiscordRole(e.target.value)}
                  placeholder="Optional role ID"
                />
              </div>
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                Users
              </label>
              <div className="flex flex-wrap gap-1 max-h-28 overflow-y-auto rounded-md border border-border p-2">
                {data.all_users.map((u) => (
                  <button
                    key={u.id}
                    type="button"
                    onClick={() =>
                      setTeamMemberIds((prev) => toggleId(prev, u.id))
                    }
                    className={cn(
                      "rounded px-2 py-0.5 text-xs border cursor-pointer",
                      teamMemberIds.includes(u.id)
                        ? "bg-primary/20 border-primary text-foreground"
                        : "bg-transparent border-border text-muted-foreground"
                    )}
                  >
                    {u.username}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                Alliance Auth Groups
              </label>
              <div className="flex flex-wrap gap-1 max-h-28 overflow-y-auto rounded-md border border-border p-2">
                {data.all_auth_groups.map((ag) => (
                  <button
                    key={ag.id}
                    type="button"
                    onClick={() =>
                      setTeamAuthIds((prev) => toggleId(prev, ag.id))
                    }
                    className={cn(
                      "rounded px-2 py-0.5 text-xs border cursor-pointer",
                      teamAuthIds.includes(ag.id)
                        ? "bg-primary/20 border-primary text-foreground"
                        : "bg-transparent border-border text-muted-foreground"
                    )}
                  >
                    {ag.name}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="ghost"
                onClick={() => setTeamOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={saving || !teamName.trim()}>
                Save Team
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Label Dialog */}
      <Dialog open={labelOpen} onOpenChange={setLabelOpen}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>{editLabelId ? "Edit Label" : "New Label"}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSaveLabel} className="space-y-4">
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                Label Name
              </label>
              <Input
                autoFocus
                value={labelName}
                onChange={(e) => setLabelName(e.target.value)}
              />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                Color Style
              </label>
              <select
                value={labelColor}
                onChange={(e) => setLabelColor(e.target.value)}
                className="flex h-9 w-full rounded-md border border-input bg-background px-2 text-sm text-foreground"
              >
                {LABEL_COLORS.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={labelIsTicket}
                onChange={(e) => setLabelIsTicket(e.target.checked)}
              />
              <span>Available on Ticket Submission</span>
            </label>
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="ghost"
                onClick={() => setLabelOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={saving || !labelName.trim()}>
                Save Label
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
