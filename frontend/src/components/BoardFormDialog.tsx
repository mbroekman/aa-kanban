import { useEffect, useState } from "react";
import { Archive, Loader2, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import {
  archiveBoard,
  createBoard,
  deleteBoard,
  editBoard,
} from "@/lib/api";
import { cn } from "@/lib/utils";
import type { BoardDetail, GroupRef } from "@/types";

interface BoardFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  allGroups: GroupRef[];
  board?: BoardDetail["board"] | null;
  onSaved: (slug: string) => void;
  onArchivedOrDeleted?: () => void;
}

export function BoardFormDialog({
  open,
  onOpenChange,
  allGroups,
  board,
  onSaved,
  onArchivedOrDeleted,
}: BoardFormDialogProps) {
  const isEdit = Boolean(board);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [viewGroupIds, setViewGroupIds] = useState<number[]>([]);
  const [writeGroupIds, setWriteGroupIds] = useState<number[]>([]);
  const [isTicketBoard, setIsTicketBoard] = useState(false);
  const [isMembersBoard, setIsMembersBoard] = useState(false);
  const [ownCardsOnly, setOwnCardsOnly] = useState(false);
  const [discordTicketChannelId, setDiscordTicketChannelId] = useState("");
  const [discordAlertChannelId, setDiscordAlertChannelId] = useState("");
  const [discordWebhookCards, setDiscordWebhookCards] = useState("");
  const [discordAlertWebhook, setDiscordAlertWebhook] = useState("");
  const [staleHours, setStaleHours] = useState("0");
  const [repeatHours, setRepeatHours] = useState("24");
  const [archiveDays, setArchiveDays] = useState("0");

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);

  useEffect(() => {
    if (!open) return;
    setError(null);
    setConfirmDelete(false);
    if (board) {
      setName(board.name);
      setDescription(board.description || "");
      setViewGroupIds(board.view_group_ids || []);
      setWriteGroupIds(board.write_group_ids || []);
      setIsTicketBoard(board.is_ticket_board);
      setIsMembersBoard(board.is_members_board);
      setOwnCardsOnly(board.own_cards_only);
      setDiscordTicketChannelId(
        board.discord_ticket_channel_id ? String(board.discord_ticket_channel_id) : ""
      );
      setDiscordAlertChannelId(
        board.discord_alert_channel_id ? String(board.discord_alert_channel_id) : ""
      );
      setDiscordWebhookCards(board.discord_webhook_cards || "");
      setDiscordAlertWebhook(board.discord_alert_webhook || "");
      setStaleHours(String(board.stale_card_alert_hours ?? 0));
      setRepeatHours(String(board.stale_card_repeat_hours ?? 24));
      setArchiveDays(String(board.archive_after_days ?? 0));
    } else {
      setName("");
      setDescription("");
      setViewGroupIds([]);
      setWriteGroupIds([]);
      setIsTicketBoard(false);
      setIsMembersBoard(false);
      setOwnCardsOnly(false);
      setDiscordTicketChannelId("");
      setDiscordAlertChannelId("");
      setDiscordWebhookCards("");
      setDiscordAlertWebhook("");
      setStaleHours("0");
      setRepeatHours("24");
      setArchiveDays("0");
    }
  }, [open, board]);

  const toggleId = (arr: number[], id: number) =>
    arr.includes(id) ? arr.filter((x) => x !== id) : [...arr, id];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Board name is required.");
      return;
    }
    setSaving(true);
    setError(null);
    const payload = {
      name: name.trim(),
      description: description.trim(),
      view_group_ids: viewGroupIds,
      write_group_ids: writeGroupIds,
      is_ticket_board: isTicketBoard,
      is_members_board: isMembersBoard,
      own_cards_only: ownCardsOnly,
      discord_ticket_channel_id: discordTicketChannelId.trim() || null,
      discord_alert_channel_id: discordAlertChannelId.trim() || null,
      discord_webhook_cards: discordWebhookCards.trim(),
      discord_alert_webhook: discordAlertWebhook.trim(),
      stale_card_alert_hours: Number(staleHours) || 0,
      stale_card_repeat_hours: Number(repeatHours) || 0,
      archive_after_days: Number(archiveDays) || 0,
    };
    try {
      if (isEdit && board) {
        await editBoard(board.slug, payload);
        onOpenChange(false);
        onSaved(board.slug);
      } else {
        const res = await createBoard(payload);
        onOpenChange(false);
        onSaved(res.board.slug);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to save board.");
    } finally {
      setSaving(false);
    }
  };

  const handleArchive = async () => {
    if (!board) return;
    setSaving(true);
    try {
      await archiveBoard(board.slug);
      onOpenChange(false);
      onArchivedOrDeleted?.();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to archive board.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!board) return;
    if (!confirmDelete) {
      setConfirmDelete(true);
      return;
    }
    setSaving(true);
    try {
      await deleteBoard(board.slug);
      onOpenChange(false);
      onArchivedOrDeleted?.();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to delete board.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{isEdit ? `Edit Board: ${board?.name}` : "Create New Board"}</DialogTitle>
        </DialogHeader>

        {error && (
          <div className="rounded-md border border-destructive/50 bg-destructive/15 px-3 py-2 text-xs text-red-700 dark:text-red-200">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Tabs defaultValue="general">
            <TabsList>
              <TabsTrigger value="general">General</TabsTrigger>
              <TabsTrigger value="access">Access &amp; Modes</TabsTrigger>
              <TabsTrigger value="automation">Discord &amp; Alerts</TabsTrigger>
            </TabsList>

            <TabsContent value="general" className="space-y-3 pt-2">
              <div>
                <label className="text-xs font-medium text-muted-foreground block mb-1">
                  Board Name
                </label>
                <Input
                  autoFocus
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Corp Logistics"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground block mb-1">
                  Description
                </label>
                <Textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  placeholder="Optional board summary..."
                />
              </div>
            </TabsContent>

            <TabsContent value="access" className="space-y-4 pt-2">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-1.5">
                    Read Groups
                  </label>
                  <div className="flex flex-wrap gap-1.5 rounded-lg border border-border p-2.5 min-h-[60px]">
                    {allGroups.length === 0 ? (
                      <span className="text-xs text-muted-foreground">No groups</span>
                    ) : (
                      allGroups.map((g) => {
                        const active = viewGroupIds.includes(g.id);
                        return (
                          <button
                            key={g.id}
                            type="button"
                            onClick={() =>
                              setViewGroupIds((prev) => toggleId(prev, g.id))
                            }
                            className={cn(
                              "rounded-md px-2 py-0.5 text-xs border cursor-pointer",
                              active
                                ? "bg-primary/20 border-primary text-foreground"
                                : "bg-transparent border-border text-muted-foreground"
                            )}
                          >
                            {g.name}
                          </button>
                        );
                      })
                    )}
                  </div>
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-1.5">
                    Write Groups
                  </label>
                  <div className="flex flex-wrap gap-1.5 rounded-lg border border-border p-2.5 min-h-[60px]">
                    {allGroups.length === 0 ? (
                      <span className="text-xs text-muted-foreground">No groups</span>
                    ) : (
                      allGroups.map((g) => {
                        const active = writeGroupIds.includes(g.id);
                        return (
                          <button
                            key={g.id}
                            type="button"
                            onClick={() =>
                              setWriteGroupIds((prev) => toggleId(prev, g.id))
                            }
                            className={cn(
                              "rounded-md px-2 py-0.5 text-xs border cursor-pointer",
                              active
                                ? "bg-primary/20 border-primary text-foreground"
                                : "bg-transparent border-border text-muted-foreground"
                            )}
                          >
                            {g.name}
                          </button>
                        );
                      })
                    )}
                  </div>
                </div>
              </div>

              <div className="space-y-2 rounded-lg border border-border p-3 text-sm">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isTicketBoard}
                    onChange={(e) => setIsTicketBoard(e.target.checked)}
                  />
                  <span>Ticket Board (allow members to submit tickets here)</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isMembersBoard}
                    onChange={(e) => setIsMembersBoard(e.target.checked)}
                  />
                  <span>Member Board (visible on Member Boards page)</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={ownCardsOnly}
                    onChange={(e) => setOwnCardsOnly(e.target.checked)}
                  />
                  <span>Readers see only their own cards</span>
                </label>
              </div>
            </TabsContent>

            <TabsContent value="automation" className="space-y-3 pt-2">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-muted-foreground block mb-1">
                    Discord Ticket Channel ID
                  </label>
                  <Input
                    value={discordTicketChannelId}
                    onChange={(e) => setDiscordTicketChannelId(e.target.value)}
                    placeholder="e.g. 123456789012345678"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground block mb-1">
                    Discord Alert Channel ID
                  </label>
                  <Input
                    value={discordAlertChannelId}
                    onChange={(e) => setDiscordAlertChannelId(e.target.value)}
                    placeholder="Fallback: ticket channel"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground block mb-1">
                  Card Movement Webhook URL
                </label>
                <Input
                  value={discordWebhookCards}
                  onChange={(e) => setDiscordWebhookCards(e.target.value)}
                  placeholder="https://discord.com/api/webhooks/..."
                />
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground block mb-1">
                  Stale Alert Webhook URL
                </label>
                <Input
                  value={discordAlertWebhook}
                  onChange={(e) => setDiscordAlertWebhook(e.target.value)}
                  placeholder="Fallback: card movement webhook"
                />
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="text-xs font-medium text-muted-foreground block mb-1">
                    Stale Alert (hours)
                  </label>
                  <Input
                    type="number"
                    min={0}
                    value={staleHours}
                    onChange={(e) => setStaleHours(e.target.value)}
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground block mb-1">
                    Alert Repeat (hours)
                  </label>
                  <Input
                    type="number"
                    min={0}
                    value={repeatHours}
                    onChange={(e) => setRepeatHours(e.target.value)}
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground block mb-1">
                    Auto-Archive (days)
                  </label>
                  <Input
                    type="number"
                    min={0}
                    value={archiveDays}
                    onChange={(e) => setArchiveDays(e.target.value)}
                  />
                </div>
              </div>
            </TabsContent>
          </Tabs>

          <div className="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-border">
            {isEdit ? (
              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleArchive}
                  disabled={saving}
                >
                  <Archive className="h-3.5 w-3.5" />
                  Archive
                </Button>
                <Button
                  type="button"
                  variant={confirmDelete ? "destructive" : "outline"}
                  size="sm"
                  onClick={handleDelete}
                  disabled={saving}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  {confirmDelete ? "Confirm Delete" : "Delete"}
                </Button>
              </div>
            ) : (
              <div />
            )}

            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant="ghost"
                onClick={() => onOpenChange(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={saving}>
                {saving ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : isEdit ? (
                  "Save Board"
                ) : (
                  "Create Board"
                )}
              </Button>
            </div>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
