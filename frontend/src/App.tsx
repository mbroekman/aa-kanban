import { useCallback, useEffect, useState } from "react";
import {
  Archive,
  BarChart3,
  Kanban,
  Loader2,
  Search,
  Settings,
  Ticket,
  Users,
} from "lucide-react";
import { ArchivedBoardsView } from "@/components/ArchivedBoardsView";
import { ArchivedCardsView } from "@/components/ArchivedCardsView";
import { BoardFormDialog } from "@/components/BoardFormDialog";
import { BoardOverview } from "@/components/BoardOverview";
import { BoardView } from "@/components/BoardView";
import { SettingsView } from "@/components/SettingsView";
import { SummaryView } from "@/components/SummaryView";
import { TicketCreateView } from "@/components/TicketCreateView";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  fetchBoardDetail,
  fetchBoards,
  getSpaConfig,
  searchCards,
} from "@/lib/api";
import type {
  BoardDetail,
  BoardSummary,
  GroupRef,
  SearchResult,
  UserRef,
} from "@/types";

type RouteState =
  | { view: "overview" }
  | { view: "members" }
  | { view: "board"; slug: string }
  | { view: "archived-cards"; slug: string }
  | { view: "archived-boards" }
  | { view: "summary" }
  | { view: "ticket-create" }
  | { view: "settings" };

function parseRouteFromLocation(spaBase: string): RouteState {
  const path = window.location.pathname;
  const normalizedBase = spaBase.endsWith("/") ? spaBase : `${spaBase}/`;
  let rest = "";
  if (path.startsWith(normalizedBase)) {
    rest = path.slice(normalizedBase.length);
  }
  // Also support legacy /spa/ prefix if visited directly
  if (rest.startsWith("spa/")) {
    rest = rest.slice("spa/".length);
  }
  rest = rest.replace(/^\/+|\/+$/g, "");

  if (rest === "members") return { view: "members" };
  if (rest === "summary") return { view: "summary" };
  if (rest === "settings") return { view: "settings" };
  if (rest === "boards/archived") return { view: "archived-boards" };
  if (rest === "tickets/create" || rest === "tickets/success") {
    return { view: "ticket-create" };
  }
  const archivedMatch = rest.match(/^board\/([^/]+)\/archived$/);
  if (archivedMatch) {
    return { view: "archived-cards", slug: decodeURIComponent(archivedMatch[1]) };
  }
  const boardMatch = rest.match(/^board\/([^/]+)$/);
  if (boardMatch) {
    return { view: "board", slug: decodeURIComponent(boardMatch[1]) };
  }
  return { view: "overview" };
}

function routeToPath(spaBase: string, route: RouteState): string {
  const base = spaBase.endsWith("/") ? spaBase : `${spaBase}/`;
  switch (route.view) {
    case "overview":
      return base;
    case "members":
      return `${base}members/`;
    case "board":
      return `${base}board/${encodeURIComponent(route.slug)}/`;
    case "archived-cards":
      return `${base}board/${encodeURIComponent(route.slug)}/archived/`;
    case "archived-boards":
      return `${base}boards/archived/`;
    case "summary":
      return `${base}summary/`;
    case "ticket-create":
      return `${base}tickets/create/`;
    case "settings":
      return `${base}settings/`;
  }
}

export function App() {
  const config = getSpaConfig();

  const [boards, setBoards] = useState<BoardSummary[]>([]);
  const [canManage, setCanManage] = useState(false);
  const [canCreateTicket, setCanCreateTicket] = useState(false);
  const [archivedCount, setArchivedCount] = useState(0);
  const [allGroups, setAllGroups] = useState<GroupRef[]>([]);
  const [currentUser, setCurrentUser] = useState<UserRef | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [route, setRoute] = useState<RouteState>(() =>
    parseRouteFromLocation(config.spaBase)
  );
  const [boardDetail, setBoardDetail] = useState<BoardDetail | null>(null);
  const [loadingBoard, setLoadingBoard] = useState(false);
  const [createBoardOpen, setCreateBoardOpen] = useState(false);

  const [globalQuery, setGlobalQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);

  const loadBoards = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchBoards();
      setBoards(res.boards);
      setCanManage(res.can_manage);
      setCanCreateTicket(res.can_create_ticket);
      setArchivedCount(res.archived_count);
      setAllGroups(res.all_groups || []);
      setCurrentUser(res.user);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load boards.");
    } finally {
      setLoading(false);
    }
  }, []);

  const loadBoard = useCallback(async (slug: string) => {
    setLoadingBoard(true);
    setError(null);
    try {
      const detail = await fetchBoardDetail(slug);
      setBoardDetail(detail);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load board.");
      setRoute({ view: "overview" });
    } finally {
      setLoadingBoard(false);
    }
  }, []);

  useEffect(() => {
    void loadBoards();
  }, [loadBoards]);

  useEffect(() => {
    if (route.view === "board") {
      void loadBoard(route.slug);
    } else {
      setBoardDetail(null);
    }
  }, [route, loadBoard]);

  useEffect(() => {
    const onPopState = () => {
      setRoute(parseRouteFromLocation(config.spaBase));
    };
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, [config.spaBase]);

  useEffect(() => {
    const q = globalQuery.trim();
    if (q.length < 2) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(() => {
      setSearching(true);
      searchCards(q)
        .then((res) => setSearchResults(res.results))
        .catch(() => setSearchResults([]))
        .finally(() => setSearching(false));
    }, 250);
    return () => clearTimeout(timer);
  }, [globalQuery]);

  const navigate = (next: RouteState) => {
    const targetUrl = routeToPath(config.spaBase, next);
    window.history.pushState({}, "", targetUrl);
    setRoute(next);
    setGlobalQuery("");
    setSearchResults([]);
  };

  const hasMemberBoards = boards.some((b) => b.is_members_board);

  return (
    <div className="p-4 sm:p-6 space-y-5">
      {/* Top SPA Toolbar */}
      <header className="flex flex-col xl:flex-row xl:items-center justify-between gap-3 pb-4 border-b border-border">
        <div
          onClick={() => navigate({ view: "overview" })}
          className="flex items-center gap-2.5 cursor-pointer group shrink-0"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/15 text-primary border border-primary/30">
            <Kanban className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-base group-hover:text-primary transition-colors">
                {config.appName}
              </span>
              <span className="rounded bg-primary/15 px-1.5 py-0.5 text-[10px] font-medium text-primary">
                Modern UI
              </span>
            </div>
            <p className="text-xs text-muted-foreground m-0">
              Boards, Tickets &amp; Workflows
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Global search */}
          <div className="relative w-56 sm:w-64">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              value={globalQuery}
              onChange={(e) => setGlobalQuery(e.target.value)}
              placeholder="Search all cards..."
              className="pl-8 h-8 text-xs"
            />
            {globalQuery.trim().length >= 2 && (
              <div className="absolute right-0 left-0 top-9 z-40 rounded-lg border border-border bg-popover p-1.5 shadow-xl max-h-72 overflow-y-auto">
                {searching ? (
                  <div className="p-2 text-xs text-muted-foreground flex items-center gap-2">
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    Searching...
                  </div>
                ) : searchResults.length > 0 ? (
                  searchResults.map((r) => (
                    <button
                      key={r.id}
                      type="button"
                      onClick={() =>
                        navigate({ view: "board", slug: r.board_slug })
                      }
                      className="w-full text-left rounded-md px-2.5 py-1.5 text-xs hover:bg-accent cursor-pointer bg-transparent border-0 text-foreground block"
                    >
                      <div className="font-medium truncate">{r.title}</div>
                      <div className="text-[11px] text-muted-foreground truncate">
                        {r.board_name} • {r.list_name}
                      </div>
                    </button>
                  ))
                ) : (
                  <div className="p-2 text-xs text-muted-foreground">
                    No matching cards.
                  </div>
                )}
              </div>
            )}
          </div>

          <Button
            variant={route.view === "overview" ? "default" : "outline"}
            size="sm"
            onClick={() => navigate({ view: "overview" })}
          >
            Boards
          </Button>

          {hasMemberBoards && (
            <Button
              variant={route.view === "members" ? "default" : "outline"}
              size="sm"
              onClick={() => navigate({ view: "members" })}
            >
              <Users className="h-3.5 w-3.5" />
              Members
            </Button>
          )}

          {canCreateTicket && (
            <Button
              variant={route.view === "ticket-create" ? "default" : "outline"}
              size="sm"
              onClick={() => navigate({ view: "ticket-create" })}
            >
              <Ticket className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400" />
              Submit Ticket
            </Button>
          )}

          {canManage && (
            <>
              <Button
                variant={route.view === "summary" ? "default" : "outline"}
                size="sm"
                onClick={() => navigate({ view: "summary" })}
              >
                <BarChart3 className="h-3.5 w-3.5" />
                Summary
              </Button>
              {archivedCount > 0 && (
                <Button
                  variant={
                    route.view === "archived-boards" ? "default" : "outline"
                  }
                  size="sm"
                  onClick={() => navigate({ view: "archived-boards" })}
                >
                  <Archive className="h-3.5 w-3.5" />
                  Archived ({archivedCount})
                </Button>
              )}
              <Button
                variant={route.view === "settings" ? "default" : "outline"}
                size="sm"
                onClick={() => navigate({ view: "settings" })}
              >
                <Settings className="h-3.5 w-3.5" />
                Settings
              </Button>
            </>
          )}
        </div>
      </header>

      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/15 px-4 py-3 text-sm text-red-700 dark:text-red-200">
          {error}
        </div>
      )}

      {/* Main Content */}
      {loading && route.view === "overview" ? (
        <div className="flex items-center justify-center py-20 gap-2 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span className="text-sm">Loading workspace...</span>
        </div>
      ) : route.view === "board" ? (
        loadingBoard || !boardDetail ? (
          <div className="flex items-center justify-center py-20 gap-2 text-muted-foreground">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span className="text-sm">Loading board...</span>
          </div>
        ) : (
          <BoardView
            detail={boardDetail}
            currentUser={currentUser}
            onBack={() => navigate({ view: "overview" })}
            onOpenArchivedCards={() =>
              navigate({ view: "archived-cards", slug: route.slug })
            }
            onBoardArchivedOrDeleted={() => {
              void loadBoards();
              navigate({ view: "overview" });
            }}
            onReload={() => loadBoard(route.slug)}
            onDetailChange={setBoardDetail}
          />
        )
      ) : route.view === "archived-cards" ? (
        <ArchivedCardsView
          boardSlug={route.slug}
          onBack={() => navigate({ view: "board", slug: route.slug })}
        />
      ) : route.view === "archived-boards" ? (
        <ArchivedBoardsView
          onBack={() => navigate({ view: "overview" })}
          onRestored={(slug) => {
            void loadBoards();
            navigate({ view: "board", slug });
          }}
        />
      ) : route.view === "summary" ? (
        <SummaryView
          onSelectBoard={(slug) => navigate({ view: "board", slug })}
        />
      ) : route.view === "ticket-create" ? (
        <TicketCreateView
          onDone={() => navigate({ view: "overview" })}
          onOpenBoard={(slug) => navigate({ view: "board", slug })}
        />
      ) : route.view === "settings" ? (
        <SettingsView />
      ) : (
        <BoardOverview
          boards={boards}
          membersOnly={route.view === "members"}
          canManage={canManage}
          onCreateBoard={() => setCreateBoardOpen(true)}
          onSelectBoard={(slug) => navigate({ view: "board", slug })}
        />
      )}

      <BoardFormDialog
        open={createBoardOpen}
        onOpenChange={setCreateBoardOpen}
        allGroups={allGroups}
        onSaved={(slug) => {
          void loadBoards();
          navigate({ view: "board", slug });
        }}
      />
    </div>
  );
}
