import { useEffect, useState } from "react";
import {
  Calendar,
  Check,
  Loader2,
  MessageSquare,
  Send,
  Tag,
  Trash2,
  Users,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
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
  addComment,
  deleteCard,
  fetchCardDetail,
  updateCard,
  uploadImage,
} from "@/lib/api";
import { cn } from "@/lib/utils";
import type { KanbanCard, LabelItem, TeamItem, UserRef } from "@/types";

interface CardDetailDialogProps {
  cardId: number | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  canWrite: boolean;
  availableLabels: LabelItem[];
  availableTeams: TeamItem[];
  availableUsers: UserRef[];
  onCardUpdated: (card: KanbanCard) => void;
  onCardDeleted: (cardId: number) => void;
}

const CARD_COLORS = [
  { value: "", label: "Default", dot: "bg-zinc-500" },
  { value: "primary", label: "Blue", dot: "bg-blue-500" },
  { value: "secondary", label: "Grey", dot: "bg-slate-400" },
  { value: "success", label: "Green", dot: "bg-emerald-500" },
  { value: "danger", label: "Red", dot: "bg-red-500" },
  { value: "warning", label: "Yellow", dot: "bg-amber-400" },
  { value: "info", label: "Cyan", dot: "bg-cyan-400" },
];

export function CardDetailDialog({
  cardId,
  open,
  onOpenChange,
  canWrite,
  availableLabels,
  availableTeams,
  availableUsers,
  onCardUpdated,
  onCardDeleted,
}: CardDetailDialogProps) {
  const [card, setCard] = useState<KanbanCard | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [color, setColor] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [teamId, setTeamId] = useState<string>("");
  const [selectedLabelIds, setSelectedLabelIds] = useState<number[]>([]);
  const [selectedAssigneeIds, setSelectedAssigneeIds] = useState<number[]>([]);

  const [commentText, setCommentText] = useState("");
  const [postingComment, setPostingComment] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [zoomImage, setZoomImage] = useState<{
    src: string;
    alt: string;
  } | null>(null);
  const [uploadingImage, setUploadingImage] = useState(false);

  const handlePasteImage = async (
    e: React.ClipboardEvent<HTMLTextAreaElement | HTMLInputElement>,
    setter: React.Dispatch<React.SetStateAction<string>>
  ) => {
    const items = Array.from(e.clipboardData?.items || []);
    const imageItem = items.find((item) => item.type.startsWith("image/"));
    const rawFile =
      imageItem?.getAsFile() ||
      Array.from(e.clipboardData?.files || []).find((f) =>
        f.type.startsWith("image/")
      );
    if (!rawFile) return;

    e.preventDefault();
    const ext = (rawFile.type.split("/")[1] || "png").replace("jpeg", "jpg");
    const filename =
      rawFile.name && rawFile.name !== "image.png"
        ? rawFile.name
        : `pasted-${Date.now()}.${ext}`;
    const namedFile = new File([rawFile], filename, { type: rawFile.type });

    const el = e.currentTarget;
    const start = el.selectionStart ?? el.value.length;
    const end = el.selectionEnd ?? el.value.length;
    const placeholder = `![Uploading ${filename}...]()`;

    setter((prev) => `${prev.slice(0, start)}${placeholder}${prev.slice(end)}`);
    setUploadingImage(true);
    setError(null);
    try {
      const uploaded = await uploadImage(namedFile);
      setter((prev) => prev.replace(placeholder, uploaded.markdown));
    } catch (err) {
      setter((prev) => prev.replace(placeholder, ""));
      setError(err instanceof Error ? err.message : "Image upload failed.");
    } finally {
      setUploadingImage(false);
    }
  };

  const handleMarkdownClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const target = e.target as HTMLElement | null;
    if (target && target.tagName === "IMG") {
      const img = target as HTMLImageElement;
      if (img.src) {
        setZoomImage({ src: img.src, alt: img.alt || "Image Preview" });
      }
    }
  };

  useEffect(() => {
    if (!open || !cardId) {
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    setConfirmDelete(false);
    fetchCardDetail(cardId)
      .then(({ card: loaded }) => {
        if (cancelled) return;
        setCard(loaded);
        setTitle(loaded.title);
        setDescription(loaded.description);
        setColor(loaded.color || "");
        setDueDate(loaded.due_date ? loaded.due_date.slice(0, 16) : "");
        setTeamId(loaded.assigned_team ? String(loaded.assigned_team.id) : "");
        setSelectedLabelIds(loaded.labels.map((l) => l.id));
        setSelectedAssigneeIds(loaded.assignees.map((u) => u.id));
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load card.");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [open, cardId]);

  const handleSave = async () => {
    if (!card || !canWrite) return;
    setSaving(true);
    setError(null);
    try {
      const { card: updated } = await updateCard(card.id, {
        title: title.trim() || card.title,
        description,
        color,
        due_date: dueDate ? dueDate : null,
        assigned_team_id: teamId ? Number(teamId) : null,
        label_ids: selectedLabelIds,
        assignee_ids: selectedAssigneeIds,
      });
      setCard(updated);
      onCardUpdated(updated);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to save changes.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!card || !canWrite) return;
    if (!confirmDelete) {
      setConfirmDelete(true);
      return;
    }
    setSaving(true);
    try {
      await deleteCard(card.id);
      onCardDeleted(card.id);
      onOpenChange(false);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to delete card.");
    } finally {
      setSaving(false);
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!card || !commentText.trim() || !canWrite) return;
    setPostingComment(true);
    try {
      const { comment } = await addComment(card.id, commentText.trim());
      const nextCard: KanbanCard = {
        ...card,
        comment_count: card.comment_count + 1,
        comments: [...(card.comments || []), comment],
      };
      setCard(nextCard);
      setCommentText("");
      onCardUpdated(nextCard);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to post comment.");
    } finally {
      setPostingComment(false);
    }
  };

  const toggleId = (list: number[], id: number) =>
    list.includes(id) ? list.filter((x) => x !== id) : [...list, id];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        {loading ? (
          <div className="flex items-center justify-center py-12 gap-2 text-muted-foreground">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span className="text-sm">Loading card...</span>
          </div>
        ) : card ? (
          <div className="space-y-5">
            <DialogHeader>
              {canWrite ? (
                <Input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="text-lg font-semibold h-10 bg-transparent border-transparent hover:border-border focus-visible:border-input px-2 -ml-2"
                />
              ) : (
                <DialogTitle>{card.title}</DialogTitle>
              )}
              <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground pt-1">
                {card.created_by && <span>Created by {card.created_by.username}</span>}
                <span>•</span>
                <span>Updated {new Date(card.updated_at).toLocaleString()}</span>
              </div>
            </DialogHeader>

            {error && (
              <div className="rounded-md border border-destructive/50 bg-destructive/15 px-3 py-2 text-xs text-red-700 dark:text-red-200">
                {error}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {/* Main column */}
              <div className="md:col-span-2 space-y-5">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Description
                    </span>
                  </div>
                  {canWrite ? (
                    <Tabs defaultValue={card.description ? "preview" : "edit"}>
                      <TabsList>
                        <TabsTrigger value="preview">Preview</TabsTrigger>
                        <TabsTrigger value="edit">Edit Markdown</TabsTrigger>
                      </TabsList>
                      <TabsContent value="preview">
                        <div
                          onClick={handleMarkdownClick}
                          className="rounded-lg border border-border bg-background/40 p-3 min-h-[110px] text-sm kanban-markdown"
                        >
                          {card.description_html ? (
                            <div
                              dangerouslySetInnerHTML={{
                                __html: card.description_html,
                              }}
                            />
                          ) : (
                            <span className="text-muted-foreground italic">
                              No description provided.
                            </span>
                          )}
                        </div>
                      </TabsContent>
                      <TabsContent value="edit">
                        <Textarea
                          value={description}
                          onChange={(e) => setDescription(e.target.value)}
                          onPaste={(e) => void handlePasteImage(e, setDescription)}
                          rows={6}
                          placeholder="Write Markdown description..."
                        />
                        <p className="mt-1 text-xs text-muted-foreground">
                          {uploadingImage
                            ? "Uploading pasted image..."
                            : "Tip: paste an image from clipboard directly into the description."}
                        </p>
                      </TabsContent>
                    </Tabs>
                  ) : (
                    <div
                      onClick={handleMarkdownClick}
                      className="rounded-lg border border-border bg-background/40 p-3 min-h-[90px] text-sm kanban-markdown"
                    >
                      {card.description_html ? (
                        <div
                          dangerouslySetInnerHTML={{
                            __html: card.description_html,
                          }}
                        />
                      ) : (
                        <span className="text-muted-foreground italic">
                          No description provided.
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Comments */}
                <div className="space-y-3 border-t border-border pt-4">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    <MessageSquare className="h-3.5 w-3.5" />
                    Comments ({card.comments?.length ?? card.comment_count})
                  </div>

                  <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1">
                    {card.comments && card.comments.length > 0 ? (
                      card.comments.map((c) => (
                        <div
                          key={c.id}
                          className="rounded-lg border border-border/70 bg-background/40 p-3 text-sm"
                        >
                          <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                            <span className="font-medium text-foreground">
                              {c.author?.username || "System"}
                            </span>
                            <span>
                              {new Date(c.created_at).toLocaleString()}
                            </span>
                          </div>
                          <div
                            onClick={handleMarkdownClick}
                            className="kanban-markdown text-sm"
                            dangerouslySetInnerHTML={{ __html: c.text_html }}
                          />
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-muted-foreground italic m-0">
                        No comments yet.
                      </p>
                    )}
                  </div>

                  {canWrite && (
                    <form onSubmit={handleAddComment} className="flex gap-2">
                      <Input
                        value={commentText}
                        onChange={(e) => setCommentText(e.target.value)}
                        onPaste={(e) => void handlePasteImage(e, setCommentText)}
                        placeholder="Write a comment..."
                      />
                      <Button
                        type="submit"
                        size="sm"
                        disabled={postingComment || !commentText.trim()}
                      >
                        {postingComment ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Send className="h-4 w-4" />
                        )}
                      </Button>
                    </form>
                  )}
                </div>
              </div>

              {/* Sidebar metadata */}
              <div className="space-y-4">
                {/* Color */}
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-1.5">
                    Card Accent
                  </label>
                  <div className="flex flex-wrap gap-1.5">
                    {CARD_COLORS.map((c) => (
                      <button
                        key={c.value || "default"}
                        type="button"
                        disabled={!canWrite}
                        onClick={() => setColor(c.value)}
                        title={c.label}
                        className={cn(
                          "h-6 w-6 rounded-full border-2 flex items-center justify-center cursor-pointer transition-transform",
                          c.dot,
                          color === c.value
                            ? "border-white scale-110"
                            : "border-transparent opacity-70 hover:opacity-100"
                        )}
                      >
                        {color === c.value && (
                          <Check className="h-3 w-3 text-white" />
                        )}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Due Date */}
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5 mb-1.5">
                    <Calendar className="h-3.5 w-3.5" />
                    Due Date
                  </label>
                  <Input
                    type="datetime-local"
                    disabled={!canWrite}
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="text-xs"
                  />
                </div>

                {/* Team */}
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5 mb-1.5">
                    <Users className="h-3.5 w-3.5" />
                    Assigned Team
                  </label>
                  <select
                    disabled={!canWrite}
                    value={teamId}
                    onChange={(e) => setTeamId(e.target.value)}
                    className="flex h-9 w-full rounded-md border border-input bg-background/80 px-2.5 text-xs text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  >
                    <option value="">No team</option>
                    {availableTeams.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Labels */}
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5 mb-1.5">
                    <Tag className="h-3.5 w-3.5" />
                    Labels
                  </label>
                  <div className="flex flex-wrap gap-1.5 max-h-28 overflow-y-auto">
                    {availableLabels.map((lbl) => {
                      const active = selectedLabelIds.includes(lbl.id);
                      return (
                        <button
                          key={lbl.id}
                          type="button"
                          disabled={!canWrite}
                          onClick={() =>
                            setSelectedLabelIds((prev) => toggleId(prev, lbl.id))
                          }
                          className={cn(
                            "rounded-md px-2 py-0.5 text-xs border cursor-pointer transition-colors",
                            active
                              ? "bg-primary/25 border-primary text-primary-foreground"
                              : "bg-secondary/60 border-border text-muted-foreground hover:text-foreground"
                          )}
                        >
                          {lbl.name}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Assignees */}
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-1.5">
                    Assignees
                  </label>
                  <div className="flex flex-wrap gap-1 max-h-28 overflow-y-auto">
                    {availableUsers.map((u) => {
                      const active = selectedAssigneeIds.includes(u.id);
                      return (
                        <Badge
                          key={u.id}
                          variant={active ? "default" : "outline"}
                          onClick={() =>
                            canWrite &&
                            setSelectedAssigneeIds((prev) =>
                              toggleId(prev, u.id)
                            )
                          }
                          className={cn(
                            "text-[11px]",
                            canWrite && "cursor-pointer"
                          )}
                        >
                          {u.username}
                        </Badge>
                      );
                    })}
                  </div>
                </div>

                {canWrite && (
                  <div className="pt-2 flex flex-col gap-2 border-t border-border">
                    <Button
                      onClick={handleSave}
                      disabled={saving}
                      className="w-full"
                    >
                      {saving ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        "Save Changes"
                      )}
                    </Button>
                    <Button
                      variant={confirmDelete ? "destructive" : "outline"}
                      size="sm"
                      onClick={handleDelete}
                      disabled={saving}
                      className="w-full"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                      {confirmDelete ? "Click again to confirm delete" : "Delete Card"}
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : null}
      </DialogContent>

      {/* Image Lightbox Dialog */}
      <Dialog
        open={zoomImage !== null}
        onOpenChange={(isOpen) => {
          if (!isOpen) setZoomImage(null);
        }}
      >
        <DialogContent className="max-w-5xl p-3">
          <DialogHeader>
            <DialogTitle className="text-sm truncate">
              {zoomImage?.alt || "Image Preview"}
            </DialogTitle>
          </DialogHeader>
          {zoomImage && (
            <div className="flex items-center justify-center bg-black/40 rounded-lg p-2">
              <img
                src={zoomImage.src}
                alt={zoomImage.alt}
                className="max-h-[80vh] max-w-full object-contain rounded"
              />
            </div>
          )}
        </DialogContent>
      </Dialog>
    </Dialog>
  );
}
