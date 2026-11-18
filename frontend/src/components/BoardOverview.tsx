import { useState } from "react";
import {
  AlertCircle,
  Columns3,
  Eye,
  LayoutGrid,
  Lock,
  Pencil,
  Plus,
  Search,
  Ticket,
  Users,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import type { BoardSummary } from "@/types";

interface BoardOverviewProps {
  boards: BoardSummary[];
  membersOnly?: boolean;
  canManage?: boolean;
  onCreateBoard?: () => void;
  onSelectBoard: (slug: string) => void;
}

export function BoardOverview({
  boards,
  membersOnly = false,
  canManage = false,
  onCreateBoard,
  onSelectBoard,
}: BoardOverviewProps) {
  const [filter, setFilter] = useState("");

  const query = filter.trim().toLowerCase();
  const filtered = boards.filter(
    (b) =>
      (!membersOnly || b.is_members_board) &&
      (!query ||
        b.name.toLowerCase().includes(query) ||
        b.description.toLowerCase().includes(query))
  );

  const managementBoards = filtered.filter((b) => !b.is_members_board);
  const memberBoards = filtered.filter((b) => b.is_members_board);

  const renderGrid = (items: BoardSummary[]) => (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {items.map((board) => (
        <Card
          key={board.id}
          onClick={() => onSelectBoard(board.slug)}
          className="group cursor-pointer transition-all hover:border-primary/60 hover:bg-accent/50 hover:-translate-y-0.5 flex flex-col justify-between"
        >
          <CardHeader className="pb-2">
            <div className="flex items-start justify-between gap-2">
              <CardTitle className="text-base group-hover:text-primary transition-colors">
                {board.name}
              </CardTitle>
              {board.attention_count > 0 && (
                <Badge variant="destructive" className="shrink-0 gap-1">
                  <AlertCircle className="h-3 w-3" />
                  {board.attention_count}
                </Badge>
              )}
            </div>
            {board.description ? (
              <p className="text-xs text-muted-foreground line-clamp-2 m-0 mt-1">
                {board.description}
              </p>
            ) : (
              <p className="text-xs text-muted-foreground/50 italic m-0 mt-1">
                No description
              </p>
            )}
          </CardHeader>
          <CardContent className="pt-2">
            <div className="flex flex-wrap items-center gap-1.5 mb-3">
              {board.is_ticket_board && (
                <Badge variant="secondary" className="gap-1 text-[11px]">
                  <Ticket className="h-3 w-3 text-amber-600 dark:text-amber-400" />
                  Tickets
                </Badge>
              )}
              {board.is_members_board && (
                <Badge variant="secondary" className="gap-1 text-[11px]">
                  <Users className="h-3 w-3 text-sky-600 dark:text-sky-400" />
                  Members
                </Badge>
              )}
              {board.own_cards_only && (
                <Badge variant="outline" className="gap-1 text-[11px]">
                  <Lock className="h-3 w-3" />
                  Own cards
                </Badge>
              )}
            </div>
            <div className="flex items-center justify-between text-xs text-muted-foreground border-t border-border/60 pt-2.5">
              <div className="flex items-center gap-3">
                <span className="inline-flex items-center gap-1">
                  <Columns3 className="h-3.5 w-3.5" />
                  {board.list_count} lists
                </span>
                <span className="inline-flex items-center gap-1">
                  <LayoutGrid className="h-3.5 w-3.5" />
                  {board.card_count} cards
                </span>
              </div>
              <span
                className="inline-flex items-center gap-1 text-[11px]"
                title={board.can_write ? "Write access" : "Read-only"}
              >
                {board.can_write ? (
                  <>
                    <Pencil className="h-3 w-3 text-emerald-600 dark:text-emerald-400" />
                    <span className="text-emerald-600 dark:text-emerald-400">Edit</span>
                  </>
                ) : (
                  <>
                    <Eye className="h-3 w-3" />
                    <span>View</span>
                  </>
                )}
              </span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold tracking-tight m-0">
            {membersOnly ? "Member Boards" : "Boards Overview"}
          </h1>
          <p className="text-sm text-muted-foreground m-0 mt-0.5">
            {membersOnly
              ? "Public member boards across your organization."
              : "Select a board to manage tasks, tickets, and workflows."}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="Filter boards..."
              className="pl-8"
            />
          </div>
          {canManage && !membersOnly && onCreateBoard && (
            <Button size="sm" onClick={onCreateBoard}>
              <Plus className="h-4 w-4" />
              New Board
            </Button>
          )}
        </div>
      </div>

      {filtered.length === 0 ? (
        <Card className="p-10 text-center">
          <p className="text-sm text-muted-foreground m-0">
            No boards match your filter.
          </p>
        </Card>
      ) : (
        <div className="space-y-6">
          {managementBoards.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground m-0">
                Project &amp; Operations Boards ({managementBoards.length})
              </h2>
              {renderGrid(managementBoards)}
            </section>
          )}
          {memberBoards.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground m-0">
                Member Boards ({memberBoards.length})
              </h2>
              {renderGrid(memberBoards)}
            </section>
          )}
        </div>
      )}
    </div>
  );
}
