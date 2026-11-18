import { useCallback, useEffect, useState } from "react";
import { ArchiveRestore, ArrowLeft, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchArchivedCards, restoreCard } from "@/lib/api";
import type { ArchivedCard } from "@/types";

interface ArchivedCardsViewProps {
  boardSlug: string;
  onBack: () => void;
}

export function ArchivedCardsView({
  boardSlug,
  onBack,
}: ArchivedCardsViewProps) {
  const [boardName, setBoardName] = useState(boardSlug);
  const [canWrite, setCanWrite] = useState(false);
  const [cards, setCards] = useState<ArchivedCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchArchivedCards(boardSlug);
      setBoardName(res.board_name);
      setCanWrite(res.can_write);
      setCards(res.cards);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load archived cards.");
    } finally {
      setLoading(false);
    }
  }, [boardSlug]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleRestore = async (cardId: number) => {
    await restoreCard(cardId);
    setCards((prev) => prev.filter((c) => c.id !== cardId));
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <Button variant="outline" size="sm" onClick={onBack}>
          <ArrowLeft className="h-4 w-4" />
          Back to {boardName}
        </Button>
        <div>
          <h1 className="text-xl font-semibold m-0">
            Archived Cards — {boardName}
          </h1>
          <p className="text-xs text-muted-foreground m-0">
            Auto-archived cards from this board.
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
          <span className="text-sm">Loading archived cards...</span>
        </div>
      ) : cards.length === 0 ? (
        <Card className="p-10 text-center">
          <p className="text-sm text-muted-foreground m-0">
            No archived cards on this board.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cards.map((c) => (
            <Card key={c.id} className="flex flex-col justify-between">
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-sm">{c.title}</CardTitle>
                  <Badge variant="outline" className="text-[11px] shrink-0">
                    {c.list_name}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="pt-2 space-y-3">
                <div className="text-xs text-muted-foreground">
                  Archived:{" "}
                  {c.archived_at
                    ? new Date(c.archived_at).toLocaleString()
                    : "Unknown"}
                </div>
                {canWrite && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => void handleRestore(c.id)}
                    className="w-full"
                  >
                    <ArchiveRestore className="h-3.5 w-3.5" />
                    Restore to Board
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
