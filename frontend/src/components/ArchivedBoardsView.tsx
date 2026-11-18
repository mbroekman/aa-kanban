import { useCallback, useEffect, useState } from "react";
import { ArchiveRestore, ArrowLeft, Loader2, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  deleteBoard,
  fetchArchivedBoards,
  restoreBoard,
} from "@/lib/api";
import type { ArchivedBoardSummary } from "@/types";

interface ArchivedBoardsViewProps {
  onBack: () => void;
  onRestored: (slug: string) => void;
}

export function ArchivedBoardsView({
  onBack,
  onRestored,
}: ArchivedBoardsViewProps) {
  const [boards, setBoards] = useState<ArchivedBoardSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [confirmSlug, setConfirmSlug] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchArchivedBoards();
      setBoards(res.boards);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load archived boards.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const handleRestore = async (slug: string) => {
    await restoreBoard(slug);
    onRestored(slug);
  };

  const handleDelete = async (slug: string) => {
    if (confirmSlug !== slug) {
      setConfirmSlug(slug);
      return;
    }
    await deleteBoard(slug);
    setConfirmSlug(null);
    await load();
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <Button variant="outline" size="sm" onClick={onBack}>
          <ArrowLeft className="h-4 w-4" />
          Back to Boards
        </Button>
        <div>
          <h1 className="text-xl font-semibold m-0">Archived Boards</h1>
          <p className="text-xs text-muted-foreground m-0">
            Restore archived boards back to active dashboards or permanently delete them.
          </p>
        </div>
      </div>

      {error && (
        <div className="rounded-md border border-destructive/50 bg-destructive/15 px-3 py-2 text-xs text-red-700 dark:text-red-200">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-16 gap-2 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span className="text-sm">Loading archived boards...</span>
        </div>
      ) : boards.length === 0 ? (
        <Card className="p-10 text-center">
          <p className="text-sm text-muted-foreground m-0">
            No archived boards.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {boards.map((b) => (
            <Card key={b.id} className="flex flex-col justify-between">
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base">{b.name}</CardTitle>
                  <Badge variant="secondary">{b.card_count} cards</Badge>
                </div>
                {b.description && (
                  <p className="text-xs text-muted-foreground m-0 mt-1">
                    {b.description}
                  </p>
                )}
              </CardHeader>
              <CardContent className="pt-2 space-y-3">
                <div className="text-xs text-muted-foreground">
                  Archived:{" "}
                  {b.archived_at
                    ? new Date(b.archived_at).toLocaleString()
                    : "Unknown"}
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    onClick={() => void handleRestore(b.slug)}
                    className="flex-1"
                  >
                    <ArchiveRestore className="h-3.5 w-3.5" />
                    Restore
                  </Button>
                  <Button
                    size="sm"
                    variant={confirmSlug === b.slug ? "destructive" : "outline"}
                    onClick={() => void handleDelete(b.slug)}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                    {confirmSlug === b.slug ? "Confirm" : "Delete"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
