import { useEffect, useState } from "react";
import { CheckCircle2, Loader2, Ticket } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { createTicket, fetchTicketOptions } from "@/lib/api";
import type { LabelItem } from "@/types";

interface TicketCreateViewProps {
  onDone: () => void;
  onOpenBoard: (slug: string) => void;
}

export function TicketCreateView({
  onDone,
  onOpenBoard,
}: TicketCreateViewProps) {
  const [teams, setTeams] = useState<
    { id: number; name: string; board_name: string }[]
  >([]);
  const [labels, setLabels] = useState<LabelItem[]>([]);
  const [loading, setLoading] = useState(true);

  const [teamId, setTeamId] = useState<string>("");
  const [labelId, setLabelId] = useState<string>("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createdInfo, setCreatedInfo] = useState<{
    boardSlug: string;
    boardName: string;
  } | null>(null);

  useEffect(() => {
    fetchTicketOptions()
      .then((res) => {
        setTeams(res.teams);
        setLabels(res.labels);
        if (res.teams.length > 0) {
          setTeamId(String(res.teams[0].id));
        }
      })
      .catch((err: unknown) =>
        setError(
          err instanceof Error ? err.message : "Failed to load ticket options."
        )
      )
      .finally(() => setLoading(false));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !teamId) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await createTicket({
        title: title.trim(),
        description: description.trim(),
        assigned_team_id: Number(teamId),
        label_id: labelId ? Number(labelId) : null,
      });
      setCreatedInfo({
        boardSlug: res.board_slug,
        boardName: res.board_name,
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to submit ticket.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 gap-2 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        <span className="text-sm">Loading ticket form...</span>
      </div>
    );
  }

  if (createdInfo) {
    return (
      <Card className="max-w-xl mx-auto mt-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
            <CheckCircle2 className="h-5 w-5" />
            Ticket Submitted
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground m-0">
            Your ticket has been created on <strong>{createdInfo.boardName}</strong>.
          </p>
          <div className="flex gap-2">
            <Button onClick={() => onOpenBoard(createdInfo.boardSlug)}>
              View Board
            </Button>
            <Button variant="outline" onClick={onDone}>
              Back to Overview
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Ticket className="h-5 w-5 text-amber-600 dark:text-amber-400" />
          Submit a Ticket
        </CardTitle>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 rounded-md border border-destructive/50 bg-destructive/15 px-3 py-2 text-xs text-red-700 dark:text-red-200">
            {error}
          </div>
        )}

        {teams.length === 0 ? (
          <p className="text-sm text-muted-foreground m-0">
            Ticket system is currently unavailable. No ticket teams are configured.
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-muted-foreground block mb-1">
                  Target Team
                </label>
                <select
                  value={teamId}
                  onChange={(e) => setTeamId(e.target.value)}
                  className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm text-foreground"
                >
                  {teams.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name} ({t.board_name})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground block mb-1">
                  Category Label
                </label>
                <select
                  value={labelId}
                  onChange={(e) => setLabelId(e.target.value)}
                  className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm text-foreground"
                >
                  <option value="">None</option>
                  {labels.map((lbl) => (
                    <option key={lbl.id} value={lbl.id}>
                      {lbl.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                Title
              </label>
              <Input
                autoFocus
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Short summary of your request..."
              />
            </div>

            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                Description (Markdown supported)
              </label>
              <Textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={6}
                placeholder="Provide details, links, or steps..."
              />
            </div>

            <div className="flex justify-end gap-2">
              <Button type="button" variant="ghost" onClick={onDone}>
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={submitting || !title.trim() || !teamId}
              >
                {submitting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  "Submit Ticket"
                )}
              </Button>
            </div>
          </form>
        )}
      </CardContent>
    </Card>
  );
}
