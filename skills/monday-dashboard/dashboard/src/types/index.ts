export type StatusState = "idle" | "thinking" | "executing" | "error";

export interface Session {
  sessionId: string;
  model?: string;
  channel?: string;
  lastActivity?: number;
  inputTokens?: number;
  outputTokens?: number;
  totalTokens?: number;
  lastHeartbeatText?: string;
}

export interface StatusResponse {
  state: StatusState;
  currentSession: Session | null;
  tokenUsage: {
    input: number;
    output: number;
    total: number;
  };
  heartbeat: {
    lastText: string;
    sentAt: number;
  };
}

export interface TodoItem {
  id: string;
  title: string;
  status: "pending" | "in-progress" | "completed";
  priority: "P0" | "P1" | "P2" | "P3";
  content: string;
  notes?: string[];
  filePath?: string;
  lineNumber?: number;
}

export interface IdeaItem {
  id: string;
  title: string;
  summary: string;
  tags: string[];
  createdAt: string;
  filePath: string;
}

export interface ProjectItem {
  id: string;
  name: string;
  description: string;
  status: "active" | "archived" | "planning";
  todos: number;
  completed: number;
  path: string;
}
