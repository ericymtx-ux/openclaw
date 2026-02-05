import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import type { IncomingMessage, ServerResponse } from "node:http";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { loadSessionStore } from "../../src/config/sessions/store.js";

// Helper to send JSON response
const sendJson = (res: ServerResponse, data: unknown) => {
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify(data));
};

const sendError = (res: ServerResponse, code: number, message: string) => {
  res.statusCode = code;
  res.end(JSON.stringify({ error: message }));
};

// Helper to serve static files
const serveStatic = (req: IncomingMessage, res: ServerResponse, basePath: string, rootDir: string) => {
  const url = new URL(req.url ?? "/", "http://localhost");
  let filePath = url.pathname.replace(basePath, "");
  if (filePath === "" || filePath === "/") filePath = "index.html";
  
  const fullPath = path.join(rootDir, filePath);
  
  // Prevent directory traversal
  if (!fullPath.startsWith(rootDir)) {
    res.statusCode = 403;
    res.end("Forbidden");
    return;
  }

  fs.readFile(fullPath, (err, data) => {
    if (err) {
      if (err.code === "ENOENT") {
        // Fallback to index.html for SPA routing
        fs.readFile(path.join(rootDir, "index.html"), (err2, data2) => {
          if (err2) {
            res.statusCode = 404;
            res.end("Not Found");
            return;
          }
          res.setHeader("Content-Type", "text/html");
          res.end(data2);
        });
        return;
      }
      res.statusCode = 500;
      res.end("Internal Server Error");
      return;
    }

    const ext = path.extname(fullPath);
    const contentType = {
      ".html": "text/html",
      ".js": "text/javascript",
      ".css": "text/css",
      ".json": "application/json",
      ".png": "image/png",
      ".jpg": "image/jpeg",
      ".svg": "image/svg+xml",
    }[ext] || "application/octet-stream";

    res.setHeader("Content-Type", contentType);
    res.end(data);
  });
};

export default function register(api: OpenClawPluginApi) {
  const logger = api.logger;
  
  // Define paths
  const HOME_DIR = os.homedir();
  const OPENCLAW_DIR = path.join(HOME_DIR, "openclaw"); // Assuming repo is here or data is here
  const TODO_DIR = path.join(OPENCLAW_DIR, "TODO");
  const IDEAS_DIR = path.join(OPENCLAW_DIR, "ideas");
  const PROJECTS_DIR = path.join(OPENCLAW_DIR, "projects");
  const SESSIONS_DIR = path.join(HOME_DIR, ".openclaw", "sessions"); // Default session dir
  const DASHBOARD_DIST = path.join(api.source, "..", "dashboard", "dist");

  // API: Status
  api.registerHttpRoute({
    path: "/monday/api/status",
    handler: async (req, res) => {
      try {
        const storePath = path.join(SESSIONS_DIR, "sessions.json");
        const sessions = loadSessionStore(storePath);
        
        // Find most active session (updated recently)
        const sortedSessions = Object.values(sessions).sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0));
        const activeSession = sortedSessions[0];
        
        const now = Date.now();
        let state = "idle";
        
        if (activeSession) {
           const diff = now - (activeSession.updatedAt || 0);
           // Simple heuristic
           if (activeSession.abortedLastRun) {
             state = "error";
           } else if (diff < 10000) { // 10s active window
             state = "executing";
             if (activeSession.lastHeartbeatText?.includes("thinking")) {
                state = "thinking";
             }
           }
        }

        sendJson(res, {
          state,
          currentSession: activeSession ? {
            sessionId: activeSession.sessionId,
            model: activeSession.model,
            channel: activeSession.channel,
            lastActivity: activeSession.updatedAt,
            lastHeartbeatText: activeSession.lastHeartbeatText
          } : null,
          tokenUsage: {
             input: activeSession?.inputTokens || 0,
             output: activeSession?.outputTokens || 0,
             total: activeSession?.totalTokens || 0,
          },
          heartbeat: {
            lastText: activeSession?.lastHeartbeatText || "",
            sentAt: activeSession?.lastHeartbeatSentAt || 0
          }
        });
      } catch (err) {
        logger.error(`Error fetching status: ${err}`);
        sendError(res, 500, "Internal Server Error");
      }
    }
  });

  // API: Todos
  api.registerHttpRoute({
    path: "/monday/api/todos",
    handler: async (req, res) => {
      try {
        if (!fs.existsSync(TODO_DIR)) {
           return sendJson(res, { items: [] });
        }
        
        const files = fs.readdirSync(TODO_DIR).filter(f => f.endsWith(".md"));
        const items = [];
        
        for (const file of files) {
          const content = fs.readFileSync(path.join(TODO_DIR, file), "utf-8");
          const lines = content.split("\n");
          for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const match = line.match(/- \[(x| |!)\] (.*)/);
            if (match) {
              items.push({
                id: `${file}-${i}`,
                title: match[2],
                status: match[1] === "x" ? "completed" : "pending",
                priority: match[1] === "!" ? "P0" : "P2",
                filePath: file,
                lineNumber: i + 1
              });
            }
          }
        }
        
        sendJson(res, { items });
      } catch (err) {
        logger.error(`Error fetching todos: ${err}`);
        sendError(res, 500, "Internal Server Error");
      }
    }
  });

  // API: Ideas
  api.registerHttpRoute({
    path: "/monday/api/ideas",
    handler: async (req, res) => {
      try {
        if (!fs.existsSync(IDEAS_DIR)) {
           return sendJson(res, { items: [] });
        }

        const files = fs.readdirSync(IDEAS_DIR).filter(f => f.endsWith(".md"));
        const items = [];

        for (const file of files) {
          const content = fs.readFileSync(path.join(IDEAS_DIR, file), "utf-8");
          // Simple parsing: First line as title
          const title = content.split("\n")[0].replace(/^#\s*/, "");
          
          items.push({
            id: file,
            title,
            summary: "",
            tags: [],
            createdAt: "",
            filePath: file
          });
        }
        
        sendJson(res, { items });
      } catch (err) {
        logger.error(`Error fetching ideas: ${err}`);
        sendError(res, 500, "Internal Server Error");
      }
    }
  });

  // API: Projects
  api.registerHttpRoute({
    path: "/monday/api/projects",
    handler: async (req, res) => {
      try {
        if (!fs.existsSync(PROJECTS_DIR)) {
           return sendJson(res, { items: [] });
        }

        const dirs = fs.readdirSync(PROJECTS_DIR, { withFileTypes: true })
          .filter(d => d.isDirectory())
          .map(d => d.name);
          
        const items = dirs.map(dir => ({
          id: dir,
          name: dir,
          description: "",
          status: "active",
          todos: 0,
          completed: 0,
          path: dir
        }));
        
        sendJson(res, { items });
      } catch (err) {
        logger.error(`Error fetching projects: ${err}`);
        sendError(res, 500, "Internal Server Error");
      }
    }
  });

  // Serve Dashboard Frontend
  // We use a wildcard handler for serving static files
  api.registerHttpHandler(async (req, res) => {
    const url = new URL(req.url ?? "/", "http://localhost");
    if (url.pathname.startsWith("/monday/")) {
       // Skip API routes which are already handled by exact matches? 
       // Note: registerHttpRoute takes precedence in plugins-http.ts logic if defined there.
       // But wait, plugins-http.ts checks routes first, then handlers.
       // So if I registered /monday/api/status, it will be handled.
       // For /monday/dashboard, it falls through to here.
       
       if (!url.pathname.startsWith("/monday/api/")) {
         serveStatic(req, res, "/monday/", DASHBOARD_DIST);
         return true;
       }
    }
    return false;
  });
}
