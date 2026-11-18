import { useEffect, useState } from "react";
import { ArrowRight, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchSummary } from "@/lib/api";
import type { SummaryBoard } from "@/types";

interface SummaryViewProps {
  onSelectBoard: (slug: string) => void;
}

export function SummaryView({ onSelectBoard }: SummaryViewProps) {
  const [boards, setBoards] = useState<SummaryBoard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSummary()
      .then((res) => setBoards(res.boards))
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Failed to load summary.")
      )
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 gap-2 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        <span className="text-sm">Loading summary...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md border border-destructive/50 bg-destructive/15 px-3 py-2 text-xs text-red-700 dark:text-red-200">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold m-0">Cross-Board Summary</h1>
        <p className="text-xs text-muted-foreground m-0 mt-0.5">
          Overview of active cards across all management boards.
        </p>
      </div>

      {boards.length === 0 ? (
        <Card className="p-10 text-center">
          <p className="text-sm text-muted-foreground m-0">No active boards.</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {boards.map((b) => (
            <Card key={b.id}>
              <CardHeader className="pb-3 flex-row items-center justify-between space-y-0">
                <div className="flex items-center gap-2">
                  <CardTitle className="text-base">{b.name}</CardTitle>
                  <Badge variant="secondary">{b.total_cards} cards</Badge>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onSelectBoard(b.slug)}
                >
                  Open Board
                  <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                  {b.lists.map((lst) => (
                    <div
                      key={lst.id}
                      className="rounded-lg border border-border/80 bg-background/40 p-2.5 space-y-2"
                    >
                      <div className="flex items-center justify-between text-xs font-semibold">
                        <span className="truncate">{lst.name}</span>
                        <Badge variant="outline" className="text-[10px]">
                          {lst.cards.length}
                          {lst.wip_limit > 0 ? `/${lst.wip_limit}` : ""}
                        </Badge>
                      </div>
                      <div className="space-y-1.5 max-h-44 overflow-y-auto">
                        {lst.cards.length === 0 ? (
                          <div className="text-[11px] text-muted-foreground italic">
                            Empty
                          </div>
                        ) : (
                          lst.cards.map((c) => (
                            <div
                              key={c.id}
                              onClick={() => onSelectBoard(b.slug)}
                              className="rounded border border-border/60 bg-card px-2 py-1.5 text-xs hover:border-primary/60 cursor-pointer"
                            >
                              <div className="font-medium truncate">
                                {c.title}
                              </div>
                              {c.assignees.length > 0 && (
                                <div className="text-[10px] text-muted-foreground truncate mt-0.5">
                                  {c.assignees.map((u) => u.username).join(", ")}
                                </div>
                              )}
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
