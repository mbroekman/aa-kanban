import { useMemo, useState } from "react";
import {
  DndContext,
  DragOverlay,
  MouseSensor,
  TouchSensor,
  closestCorners,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import {
  Archive,
  ArrowLeft,
  Calendar,
  Loader2,
  MessageSquare,
  Pencil,
  Plus,
  Search,
  Settings,
  Trash2,
  UserCheck,
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
import {
  closeCardThread,
  createCard,
  createList,
  deleteList,
  editList,
  moveCard,
} from "@/lib/api";
import { cn } from "@/lib/utils";
import type { BoardDetail, KanbanCard, KanbanList, UserRef } from "@/types";
import { BoardFormDialog } from "./BoardFormDialog";
import { CardDetailDialog } from "./CardDetailDialog";

interface BoardViewProps {
  detail: BoardDetail;
  currentUser: UserRef | null;
  onBack: () => void;
  onOpenArchivedCards: () => void;
  onBoardArchivedOrDeleted: () => void;
  onReload: () => Promise<void>;
  onDetailChange: (next: BoardDetail) => void;
}

const ACCENT_BORDER: Record<string, string> = {
  primary: "border-l-4 border-l-blue-500",
  secondary: "border-l-4 border-l-slate-400",
  success: "border-l-4 border-l-emerald-500",
  danger: "border-l-4 border-l-red-500",
  warning: "border-l-4 border-l-amber-400",
  info: "border-l-4 border-l-cyan-400",
};

function CardItem({
  card,
  onClick,
  isOverlay = false,
}: {
  card: KanbanCard;
  onClick?: () => void;
  isOverlay?: boolean;
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: `card-${card.id}`, data: { type: "card", card } });

  const style = isOverlay
    ? undefined
    : {
        transform: CSS.Transform.toString(transform),
        transition,
      };

  const accent = card.color ? ACCENT_BORDER[card.color] || "" : "";

  return (
    <div
      ref={isOverlay ? undefined : setNodeRef}
      style={style}
      {...(isOverlay ? {} : attributes)}
      {...(isOverlay ? {} : listeners)}
      onClick={onClick}
      className={cn(
        "group rounded-lg border border-border bg-card p-3 shadow-xs transition-all hover:border-primary/60 hover:bg-accent/50 cursor-pointer select-none touch-manipulation [-webkit-touch-callout:none]",
        accent,
        isDragging && "opacity-35",
        isOverlay && "shadow-2xl ring-2 ring-primary/60 rotate-1"
      )}
    >
      {card.labels.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {card.labels.map((lbl) => (
            <span
              key={lbl.id}
              className="rounded px-1.5 py-0.5 text-[10px] font-medium bg-primary/20 text-primary-foreground border border-primary/30"
            >
              {lbl.name}
            </span>
          ))}
        </div>
      )}

      <div className="text-sm font-medium text-foreground leading-snug">
        {card.title}
      </div>

      <div className="mt-2.5 flex flex-wrap items-center justify-between gap-2 text-[11px] text-muted-foreground">
        <div className="flex items-center gap-2">
          {card.due_date && (
            <span className="inline-flex items-center gap-1 text-amber-700 dark:text-amber-300">
              <Calendar className="h-3 w-3" />
              {new Date(card.due_date).toLocaleDateString()}
            </span>
          )}
          {card.comment_count > 0 && (
            <span className="inline-flex items-center gap-1">
              <MessageSquare className="h-3 w-3" />
              {card.comment_count}
            </span>
          )}
          {card.assigned_team && (
            <span className="inline-flex items-center gap-1 text-sky-700 dark:text-sky-300">
              <Users className="h-3 w-3" />
              {card.assigned_team.name}
            </span>
          )}
        </div>

        {card.assignees.length > 0 && (
          <div className="flex -space-x-1">
            {card.assignees.slice(0, 3).map((u) => (
              <span
                key={u.id}
                title={u.username}
                className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-secondary border border-border text-[10px] font-semibold text-foreground uppercase"
              >
                {u.username.slice(0, 2)}
              </span>
            ))}
            {card.assignees.length > 3 && (
              <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-muted border border-border text-[10px]">
                +{card.assignees.length - 3}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function KanbanColumn({
  list,
  cards,
  canWrite,
  onOpenCard,
  onCardCreated,
  onEditList,
}: {
  list: KanbanList;
  cards: KanbanCard[];
  canWrite: boolean;
  onOpenCard: (cardId: number) => void;
  onCardCreated: (card: KanbanCard) => void;
  onEditList: (list: KanbanList) => void;
}) {
  const { setNodeRef } = useSortable({
    id: `list-${list.id}`,
    data: { type: "list", list },
  });

  const [adding, setAdding] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const atLimit = list.wip_limit > 0 && cards.length >= list.wip_limit;

  const handleAddCard = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    setSubmitting(true);
    try {
      const { card } = await createCard(list.id, { title: newTitle.trim() });
      onCardCreated(card);
      setNewTitle("");
      setAdding(false);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      ref={setNodeRef}
      className="flex w-80 shrink-0 flex-col rounded-xl border border-border bg-background/50 max-h-[calc(100vh-230px)]"
    >
      {/* Column header */}
      <div className="flex items-center justify-between gap-2 p-3 border-b border-border/70">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold truncate m-0">{list.name}</h3>
            <Badge
              variant={atLimit ? "destructive" : "secondary"}
              className="text-[11px] px-1.5"
            >
              {cards.length}
              {list.wip_limit > 0 ? ` / ${list.wip_limit}` : ""}
            </Badge>
          </div>
          {list.description && (
            <p className="text-[11px] text-muted-foreground truncate m-0 mt-0.5">
              {list.description}
            </p>
          )}
        </div>
        {canWrite && (
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={() => onEditList(list)}
            title="Edit column"
            className="h-7 w-7 shrink-0 text-muted-foreground hover:text-foreground"
          >
            <Pencil className="h-3.5 w-3.5" />
          </Button>
        )}
      </div>

      {/* Cards container */}
      <div className="flex-1 overflow-y-auto p-2.5 space-y-2.5 min-h-[80px]">
        <SortableContext
          items={cards.map((c) => `card-${c.id}`)}
          strategy={verticalListSortingStrategy}
        >
          {cards.map((card) => (
            <CardItem
              key={card.id}
              card={card}
              onClick={() => onOpenCard(card.id)}
            />
          ))}
        </SortableContext>
        {cards.length === 0 && (
          <div className="rounded-lg border border-dashed border-border/60 py-6 text-center text-xs text-muted-foreground">
            Drop cards here
          </div>
        )}
      </div>

      {/* Footer / Add Card */}
      {list.can_add_card && (
        <div className="p-2.5 border-t border-border/60">
          {adding ? (
            <form onSubmit={handleAddCard} className="space-y-2">
              <Input
                autoFocus
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="Card title..."
                disabled={submitting}
              />
              <div className="flex items-center gap-1.5">
                <Button
                  type="submit"
                  size="sm"
                  disabled={submitting || !newTitle.trim()}
                >
                  {submitting ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    "Add Card"
                  )}
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant="ghost"
                  onClick={() => {
                    setAdding(false);
                    setNewTitle("");
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          ) : (
            <Button
              variant="ghost"
              size="sm"
              disabled={atLimit}
              onClick={() => setAdding(true)}
              className="w-full justify-start text-muted-foreground hover:text-foreground"
            >
              <Plus className="h-4 w-4" />
              {atLimit ? "WIP limit reached" : "Add card"}
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

export function BoardView({
  detail,
  currentUser,
  onBack,
  onOpenArchivedCards,
  onBoardArchivedOrDeleted,
  onReload,
  onDetailChange,
}: BoardViewProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [labelFilter, setLabelFilter] = useState<number | null>(null);
  const [onlyMine, setOnlyMine] = useState(false);

  const [activeCardId, setActiveCardId] = useState<number | null>(null);
  const [draggingCard, setDraggingCard] = useState<KanbanCard | null>(null);

  const [addListOpen, setAddListOpen] = useState(false);
  const [newListName, setNewListName] = useState("");
  const [newListWip, setNewListWip] = useState("0");
  const [creatingList, setCreatingList] = useState(false);
  const [moveError, setMoveError] = useState<string | null>(null);
  const [closeThreadCardId, setCloseThreadCardId] = useState<number | null>(
    null
  );
  const [closingThread, setClosingThread] = useState(false);

  const [editingList, setEditingList] = useState<KanbanList | null>(null);
  const [editListName, setEditListName] = useState("");
  const [editListDesc, setEditListDesc] = useState("");
  const [editListWip, setEditListWip] = useState("0");
  const [savingList, setSavingList] = useState(false);
  const [confirmDeleteList, setConfirmDeleteList] = useState(false);

  const [boardSettingsOpen, setBoardSettingsOpen] = useState(false);

  // Separate mouse and touch sensors: a PointerSensor with only a distance
  // constraint loses the gesture on iPad/iOS Safari, because the browser
  // claims the touch for scrolling and fires pointercancel before the drag
  // activates. The TouchSensor starts a drag after a short long-press, so a
  // normal swipe still scrolls the board and a tap still opens the card.
  const sensors = useSensors(
    useSensor(MouseSensor, {
      activationConstraint: { distance: 6 },
    }),
    useSensor(TouchSensor, {
      activationConstraint: { delay: 200, tolerance: 8 },
    })
  );

  const filteredCards = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    return detail.cards.filter((c) => {
      if (
        q &&
        !c.title.toLowerCase().includes(q) &&
        !c.description.toLowerCase().includes(q)
      ) {
        return false;
      }
      if (labelFilter && !c.labels.some((l) => l.id === labelFilter)) {
        return false;
      }
      if (onlyMine && currentUser) {
        const isCreator = c.created_by?.id === currentUser.id;
        const isAssignee = c.assignees.some((a) => a.id === currentUser.id);
        if (!isCreator && !isAssignee) return false;
      }
      return true;
    });
  }, [detail.cards, searchQuery, labelFilter, onlyMine, currentUser]);

  const cardsByList = useMemo(() => {
    const map = new Map<number, KanbanCard[]>();
    for (const lst of detail.lists) {
      map.set(lst.id, []);
    }
    for (const c of filteredCards) {
      const arr = map.get(c.list_id);
      if (arr) arr.push(c);
    }
    return map;
  }, [detail.lists, filteredCards]);

  const handleDragStart = (event: DragStartEvent) => {
    const data = event.active.data.current;
    if (data?.type === "card") {
      setDraggingCard(data.card as KanbanCard);
    }
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    setDraggingCard(null);
    if (!detail.board.can_write) return;
    const { active, over } = event;
    if (!over) return;

    const activeData = active.data.current;
    const overData = over.data.current;
    if (activeData?.type !== "card") return;

    const movedCard = activeData.card as KanbanCard;
    let targetListId = movedCard.list_id;
    let newPosition = 0;

    if (overData?.type === "card") {
      const overCard = overData.card as KanbanCard;
      targetListId = overCard.list_id;
      const targetCards = (cardsByList.get(targetListId) || []).filter(
        (c) => c.id !== movedCard.id
      );
      const idx = targetCards.findIndex((c) => c.id === overCard.id);
      newPosition = idx >= 0 ? idx : targetCards.length;
    } else if (overData?.type === "list") {
      targetListId = (overData.list as KanbanList).id;
      newPosition = (cardsByList.get(targetListId) || []).length;
    } else {
      return;
    }

    if (movedCard.list_id === targetListId && movedCard.order === newPosition) {
      return;
    }

    // Optimistic update
    const nextCards = detail.cards.map((c) =>
      c.id === movedCard.id
        ? { ...c, list_id: targetListId, order: newPosition }
        : c
    );
    onDetailChange({ ...detail, cards: nextCards });
    setMoveError(null);

    try {
      const res = await moveCard(movedCard.id, targetListId, newPosition);
      await onReload();
      if (res.prompt_close_thread) {
        setCloseThreadCardId(movedCard.id);
      }
    } catch (err: unknown) {
      setMoveError(err instanceof Error ? err.message : "Failed to move card.");
      await onReload();
    }
  };

  const handleCreateList = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newListName.trim()) return;
    setCreatingList(true);
    try {
      const { list } = await createList(detail.board.slug, {
        name: newListName.trim(),
        wip_limit: Number(newListWip) || 0,
      });
      onDetailChange({ ...detail, lists: [...detail.lists, list] });
      setNewListName("");
      setNewListWip("0");
      setAddListOpen(false);
    } finally {
      setCreatingList(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Board Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 pb-3 border-b border-border/70">
        <div className="flex items-center gap-3 min-w-0">
          <Button variant="outline" size="sm" onClick={onBack}>
            <ArrowLeft className="h-4 w-4" />
            Boards
          </Button>
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-lg font-semibold truncate m-0">
                {detail.board.name}
              </h1>
              {!detail.board.can_write && (
                <Badge variant="outline" className="text-[11px]">
                  Read-only
                </Badge>
              )}
            </div>
            {detail.board.description && (
              <p className="text-xs text-muted-foreground truncate m-0">
                {detail.board.description}
              </p>
            )}
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative w-52">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter cards..."
              className="pl-8 h-8 text-xs"
            />
          </div>

          <Button
            size="sm"
            variant={onlyMine ? "default" : "outline"}
            onClick={() => setOnlyMine((v) => !v)}
          >
            <UserCheck className="h-3.5 w-3.5" />
            My Cards
          </Button>

          {detail.board.can_write && (
            <Button size="sm" onClick={() => setAddListOpen(true)}>
              <Plus className="h-3.5 w-3.5" />
              Add Column
            </Button>
          )}
          <Button size="sm" variant="outline" onClick={onOpenArchivedCards}>
            <Archive className="h-3.5 w-3.5" />
            Archived
          </Button>
          {detail.board.can_manage && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => setBoardSettingsOpen(true)}
            >
              <Settings className="h-3.5 w-3.5" />
              Board Settings
            </Button>
          )}
        </div>
      </div>

      {/* Label filter bar */}
      {detail.labels.length > 0 && (
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-xs text-muted-foreground mr-1">Labels:</span>
          <button
            type="button"
            onClick={() => setLabelFilter(null)}
            className={cn(
              "rounded-md px-2 py-0.5 text-xs border cursor-pointer",
              labelFilter === null
                ? "bg-primary/20 border-primary text-foreground"
                : "bg-transparent border-border text-muted-foreground"
            )}
          >
            All
          </button>
          {detail.labels.map((lbl) => (
            <button
              key={lbl.id}
              type="button"
              onClick={() =>
                setLabelFilter((cur) => (cur === lbl.id ? null : lbl.id))
              }
              className={cn(
                "rounded-md px-2 py-0.5 text-xs border cursor-pointer",
                labelFilter === lbl.id
                  ? "bg-primary/20 border-primary text-foreground"
                  : "bg-transparent border-border text-muted-foreground hover:text-foreground"
              )}
            >
              {lbl.name}
            </button>
          ))}
        </div>
      )}

      {moveError && (
        <div className="rounded-md border border-destructive/50 bg-destructive/15 px-3 py-2 text-xs text-red-700 dark:text-red-200">
          {moveError}
        </div>
      )}

      {/* Horizontal Columns */}
      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="flex gap-4 overflow-x-auto pb-4 items-start">
          {detail.lists.map((lst) => (
            <KanbanColumn
              key={lst.id}
              list={lst}
              cards={cardsByList.get(lst.id) || []}
              canWrite={detail.board.can_write}
              onOpenCard={(id) => setActiveCardId(id)}
              onCardCreated={(card) =>
                onDetailChange({
                  ...detail,
                  cards: [...detail.cards, card],
                })
              }
              onEditList={(target) => {
                setEditingList(target);
                setEditListName(target.name);
                setEditListDesc(target.description);
                setEditListWip(String(target.wip_limit));
                setConfirmDeleteList(false);
              }}
            />
          ))}
        </div>

        <DragOverlay>
          {draggingCard ? <CardItem card={draggingCard} isOverlay /> : null}
        </DragOverlay>
      </DndContext>

      {/* Card Detail Dialog */}
      <CardDetailDialog
        cardId={activeCardId}
        open={activeCardId !== null}
        onOpenChange={(open) => {
          if (!open) setActiveCardId(null);
        }}
        canWrite={detail.board.can_write}
        availableLabels={detail.labels}
        availableTeams={detail.teams}
        availableUsers={detail.users}
        onCardUpdated={(updated) =>
          onDetailChange({
            ...detail,
            cards: detail.cards.map((c) => (c.id === updated.id ? updated : c)),
          })
        }
        onCardDeleted={(deletedId) =>
          onDetailChange({
            ...detail,
            cards: detail.cards.filter((c) => c.id !== deletedId),
          })
        }
      />

      {/* Close Discord Thread Prompt */}
      <Dialog
        open={closeThreadCardId !== null}
        onOpenChange={(open) => {
          if (!open) setCloseThreadCardId(null);
        }}
      >
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Close Discord thread?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            This card reached the last column and has a linked Discord
            thread. Archive and lock it now?
          </p>
          <div className="flex justify-end gap-2 mt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setCloseThreadCardId(null)}
              disabled={closingThread}
            >
              Keep Open
            </Button>
            <Button
              type="button"
              onClick={async () => {
                if (closeThreadCardId === null) return;
                setClosingThread(true);
                try {
                  await closeCardThread(closeThreadCardId);
                } finally {
                  setClosingThread(false);
                  setCloseThreadCardId(null);
                }
              }}
              disabled={closingThread}
            >
              {closingThread ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                "Close Thread"
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Add Column Dialog */}
      <Dialog open={addListOpen} onOpenChange={setAddListOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Add Column</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreateList} className="space-y-4">
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                Column Name
              </label>
              <Input
                autoFocus
                value={newListName}
                onChange={(e) => setNewListName(e.target.value)}
                placeholder="e.g. In Review"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                WIP Limit (0 = unlimited)
              </label>
              <Input
                type="number"
                min={0}
                value={newListWip}
                onChange={(e) => setNewListWip(e.target.value)}
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setAddListOpen(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={creatingList || !newListName.trim()}
              >
                {creatingList ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  "Create Column"
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit Column Dialog */}
      <Dialog
        open={editingList !== null}
        onOpenChange={(open) => {
          if (!open) setEditingList(null);
        }}
      >
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Column</DialogTitle>
          </DialogHeader>
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              if (!editingList || !editListName.trim()) return;
              setSavingList(true);
              try {
                const { list } = await editList(editingList.id, {
                  name: editListName.trim(),
                  description: editListDesc.trim(),
                  wip_limit: Number(editListWip) || 0,
                });
                onDetailChange({
                  ...detail,
                  lists: detail.lists.map((l) => (l.id === list.id ? list : l)),
                });
                setEditingList(null);
              } finally {
                setSavingList(false);
              }
            }}
            className="space-y-4"
          >
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                Column Name
              </label>
              <Input
                autoFocus
                value={editListName}
                onChange={(e) => setEditListName(e.target.value)}
              />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                Description
              </label>
              <Input
                value={editListDesc}
                onChange={(e) => setEditListDesc(e.target.value)}
              />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                WIP Limit (0 = unlimited)
              </label>
              <Input
                type="number"
                min={0}
                value={editListWip}
                onChange={(e) => setEditListWip(e.target.value)}
              />
            </div>
            <div className="flex justify-between gap-2">
              <Button
                type="button"
                variant={confirmDeleteList ? "destructive" : "outline"}
                size="sm"
                disabled={savingList}
                onClick={async () => {
                  if (!editingList) return;
                  if (!confirmDeleteList) {
                    setConfirmDeleteList(true);
                    return;
                  }
                  setSavingList(true);
                  try {
                    await deleteList(editingList.id);
                    onDetailChange({
                      ...detail,
                      lists: detail.lists.filter((l) => l.id !== editingList.id),
                      cards: detail.cards.filter(
                        (c) => c.list_id !== editingList.id
                      ),
                    });
                    setEditingList(null);
                  } finally {
                    setSavingList(false);
                  }
                }}
              >
                <Trash2 className="h-3.5 w-3.5" />
                {confirmDeleteList ? "Confirm Delete" : "Delete"}
              </Button>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setEditingList(null)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={savingList || !editListName.trim()}
                >
                  Save
                </Button>
              </div>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit Board Dialog */}
      <BoardFormDialog
        open={boardSettingsOpen}
        onOpenChange={setBoardSettingsOpen}
        allGroups={detail.all_groups || []}
        board={detail.board}
        onSaved={() => void onReload()}
        onArchivedOrDeleted={onBoardArchivedOrDeleted}
      />
    </div>
  );
}
