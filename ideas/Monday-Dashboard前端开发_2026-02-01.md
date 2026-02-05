# Monday Dashboard 前端开发任务分解

## 1. 项目概述

开发一个独立的前端 Dashboard 界面，通过公仔动画展示 AI (Monday) 的工作状态，并用 Trello 风格看板展示 TODO、Ideas、Projects 信息。

### 1.1 功能需求

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 公仔动画 | 展示空闲/思考/执行/错误状态 | P0 |
| TODO 看板 | Markdown TODO 列表，悬浮显示详情 | P0 |
| Ideas 看板 | 创意想法列表 | P0 |
| Projects 看板 | 项目进度追踪 | P0 |
| 备注功能 | 在事项上添加备注 | P1 |
| 高亮联动 | 执行任务时高亮对应 TODO/Project | P1 |
| 实时更新 | WebSocket/API 轮询状态变化 | P1 |

---

## 2. OpenClaw 源码调研

### 2.1 工作状态获取接口

#### 2.1.1 会话状态 (Session Status)

**文件**: `src/config/sessions/types.ts`

```typescript
type SessionEntry = {
  // 核心状态
  sessionId: string;
  updatedAt: number;
  abortedLastRun?: boolean;      // 运行是否被中断
  
  // 模型信息
  modelProvider?: string;         // 提供商: anthropic, minimax
  model?: string;                 // 模型名: claude-opus-4-5, MiniMax-M2.1
  
  // Token 使用
  inputTokens?: number;
  outputTokens?: number;
  totalTokens?: number;
  
  // 思考级别
  thinkingLevel?: string;         // thinking 级别
  verboseLevel?: string;          // verbose 级别
  reasoningLevel?: string;        // reasoning 级别
  
  // 心跳信息
  lastHeartbeatText?: string;     // 最后心跳文本
  lastHeartbeatSentAt?: number;   // 最后心跳时间
  
  // 会话元数据
  label?: string;                 // 会话标签
  displayName?: string;           // 显示名称
  channel?: string;               // 渠道: telegram, webchat
  groupId?: string;
  
  // 技能快照
  skillsSnapshot?: SessionSkillSnapshot;
};
```

#### 2.1.2 状态命令 (Status Command)

**文件**: `src/commands/status.command.ts`

```bash
# 获取所有状态
openclaw status --all

# 获取 agent 状态
openclaw status agent

# 扫描状态
openclaw status scan
```

#### 2.1.3 状态类型定义

**文件**: `src/commands/status.ts`

```typescript
export type StatusSummary = {
  daemon: DaemonStatus;
  gateway: GatewayStatus;
  agents: AgentStatus[];
  channels: ChannelStatus[];
  os: OsSummary;
};

export type SessionStatus = {
  sessionId: string;
  status: "active" | "idle" | "error";
  lastActivity: string;
  currentTask?: string;
};
```

### 2.2 工作区数据位置

| 数据类型 | 路径 | 格式 |
|----------|------|------|
| TODO | `/Users/apple/openclaw/TODO/` | Markdown 文件 |
| Ideas | `/Users/apple/openclaw/ideas/` | Markdown 文件 |
| Projects | `/Users/apple/openclaw/projects/` | 目录结构 + README.md |

### 2.3 现有 Web 接口

**文件**: `src/web/`

```typescript
// Web Provider 用于消息通道
// 状态可通过 web server 获取
```

### 2.4 CLI 命令结构

**文件**: `src/cli/`

```bash
# 核心命令
openclaw status --all        # 完整状态扫描
openclaw agents list         # 列出所有 agent
openclaw sessions list       # 列出所有会话
openclaw health              # 健康检查
```

---

## 3. API 接口设计

### 3.1 状态获取 API

```typescript
// GET /api/status
interface StatusResponse {
  state: "idle" | "thinking" | "executing" | "error";
  currentSession: {
    sessionId: string;
    model: string;
    channel: string;
    lastActivity: number;
  };
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

// GET /api/todos
interface TodoResponse {
  items: TodoItem[];
  activeItem?: string;
}

interface TodoItem = {
  id: string;
  title: string;
  status: "pending" | "in-progress" | "completed";
  priority: "P0" | "P1" | "P2" | "P3";
  content: string;
  notes: string[];
  filePath: string;
  lineNumber: number;
};

// GET /api/ideas
interface IdeaResponse {
  items: IdeaItem[];
}

interface IdeaItem = {
  id: string;
  title: string;
  summary: string;
  tags: string[];
  createdAt: string;
  filePath: string;
};

// GET /api/projects
interface ProjectResponse {
  items: ProjectItem[];
  activeProject?: string;
}

interface ProjectItem = {
  id: string;
  name: string;
  description: string;
  status: "active" | "archived" | "planning";
  todos: number;
  completed: number;
  path: string;
};

// POST /api/items/:id/notes
interface AddNoteRequest {
  content: string;
}
```

### 3.2 WebSocket 实时更新

```typescript
// WebSocket /ws/status
interface WsMessage {
  type: "status_change" | "todo_update" | "idea_update" | "project_update";
  data: unknown;
}
```

---

## 4. 开发任务分解

### P0 - 基础架构

#### Task 4.1: 项目脚手架

**目录**: `frontend/dashboard/`

**文件**:
- [ ] `package.json` - 依赖配置
- [ ] `vite.config.ts` - Vite 配置
- [ ] `tsconfig.json` - TypeScript 配置
- [ ] `index.html` - 入口 HTML
- [ ] `src/main.tsx` - React 入口
- [ ] `src/App.tsx` - 主应用组件
- [ ] `src/App.css` - 全局样式

**技术栈**:
- React 18 + TypeScript
- Vite 5
- TailwindCSS 3
- Framer Motion (动画)
- Lucide React (图标)

**验收标准**:
- [ ] `npm install` 成功
- [ ] `npm run dev` 启动
- [ ] 页面显示 Hello World

**预估时间**: 30 分钟

---

#### Task 4.2: 状态管理 Store

**文件**:
- [ ] `src/store/index.ts` - Zustand store
- [ ] `src/store/status.ts` - 状态 slice
- [ ] `src/store/todos.ts` - TODO slice
- [ ] `src/store/ideas.ts` - Ideas slice
- [ ] `src/store/projects.ts` - Projects slice

**设计**:

```typescript
// src/store/status.ts
interface StatusState {
  state: "idle" | "thinking" | "executing" | "error";
  session: Session | null;
  tokenUsage: TokenUsage;
  lastHeartbeat: string | null;
  
  // Actions
  setState: (state: StatusState["state"]) => void;
  updateSession: (session: Partial<Session>) => void;
  updateTokenUsage: (usage: TokenUsage) => void;
}

// src/store/todos.ts
interface TodoState {
  items: TodoItem[];
  activeItemId: string | null;
  
  loadTodos: () => Promise<void>;
  setActiveItem: (id: string | null) => void;
  addNote: (itemId: string, note: string) => void;
}
```

**验收标准**:
- [ ] Zustand store 创建成功
- [ ] TypeScript 类型完整
- [ ] 支持持久化 (localStorage)

**预估时间**: 1 小时

---

#### Task 4.3: API 客户端层

**文件**:
- [ ] `src/api/client.ts` - HTTP 客户端
- [ ] `src/api/endpoints.ts` - 端点定义
- [ ] `src/api/websocket.ts` - WebSocket 客户端

**设计**:

```typescript
// src/api/client.ts
class ApiClient {
  private baseUrl: string;
  private ws: WebSocket | null = null;
  
  async get<T>(path: string): Promise<T>;
  async post<T>(path: string, data: unknown): Promise<T>;
  
  connectWs(handler: (msg: WsMessage) => void): void;
  disconnectWs(): void;
}

export const api = new ApiClient("/api");
```

**验收标准**:
- [ ] 基础 GET/POST 请求
- [ ] WebSocket 连接/断开
- [ ] 自动重连机制

**预估时间**: 1 小时

---

### P0 - 核心组件

#### Task 4.4: 公仔动画组件

**文件**:
- [ ] `src/components/Mascot/index.tsx`
- [ ] `src/components/Mascot/Mascot.css`
- [ ] `src/components/Mascot/animations/`

**状态映射**:

| OpenClaw 状态 | 公仔状态 | 动画 |
|---------------|----------|------|
| idle | 空闲 | 待机动画、呼吸效果 |
| thinking | 思考 | 闪烁眼睛、思考动画 |
| executing | 执行 | 忙碌动画、敲键盘 |
| error | 错误 | 警示动画、抖动 |

**设计**:

```typescript
// src/components/Mascot/index.tsx
interface MascotProps {
  state: "idle" | "thinking" | "executing" | "error";
  size?: "sm" | "md" | "lg";
  animated?: boolean;
}

export function Mascot({ state, size = "md", animated = true }: MascotProps) {
  // 根据 state 选择不同动画组件
  const animation = useMemo(() => {
    switch (state) {
      case "idle": return <IdleAnimation />;
      case "thinking": return <ThinkingAnimation />;
      case "executing": return <ExecutingAnimation />;
      case "error": return <ErrorAnimation />;
    }
  }, [state]);
  
  return <div className="mascot">{animation}</div>;
}
```

**验收标准**:
- [ ] 4 种状态动画完整
- [ ] 支持大小切换
- [ ] 动画流畅 (60fps)

**预估时间**: 3 小时

---

#### Task 4.5: Trello 看板组件

**文件**:
- [ ] `src/components/Board/index.tsx`
- [ ] `src/components/Board/Column.tsx`
- [ ] `src/components/Board/Card.tsx`
- [ ] `src/components/Board/CardModal.tsx`

**设计**:

```typescript
// src/components/Board/index.tsx
interface BoardProps {
  items: BoardItem[];
  type: "todo" | "idea" | "project";
  activeId?: string;
  onItemClick: (item: BoardItem) => void;
  onAddNote: (itemId: string, note: string) => void;
}

export function Board({ items, type, activeId, onItemClick }: BoardProps) {
  const columns = groupByStatus(items);
  
  return (
    <div className="board">
      {columns.map(col => (
        <Column 
          key={col.status} 
          title={col.title} 
          items={col.items}
          onItemClick={onItemClick}
        />
      ))}
    </div>
  );
}
```

**交互设计**:
- 悬浮显示详情 Tooltip
- 点击打开 Modal
- Modal 内添加备注
- 高亮选中项

**验收标准**:
- [ ] 3 列布局 (Todo/Idea/Project)
- [ ] 拖拽排序 (可选 P1)
- [ ] 悬浮显示详情
- [ ] Modal 交互完整

**预估时间**: 3 小时

---

#### Task 4.6: 数据解析器

**文件**:
- [ ] `src/parsers/todo.ts`
- [ ] `src/parsers/idea.ts`
- [ ] `src/parsers/project.ts`

**设计**:

```typescript
// src/parsers/todo.ts
interface ParsedTodo {
  id: string;
  title: string;
  status: "pending" | "in-progress" | "completed";
  priority: "P0" | "P1" | "P2" | "P3";
  content: string;
  filePath: string;
  lineNumber: number;
}

function parseTodoFile(content: string, filePath: string): ParsedTodo[] {
  // 解析 Markdown 格式的 TODO
  // - [ ] 待办
  // - [x] 完成
  // - [!] 高优先级
}

// src/parsers/idea.ts
interface ParsedIdea {
  id: string;
  title: string;
  summary: string;
  tags: string[];
  createdAt: string;
  content: string;
}

function parseIdeaFile(content: string, filePath: string): ParsedIdea {
  // 解析 Markdown frontmatter
}

// src/parsers/project.ts
interface ParsedProject {
  id: string;
  name: string;
  description: string;
  status: "active" | "archived" | "planning";
  todos: number;
  completed: number;
}

function parseProject(path: string): ParsedProject {
  // 解析目录结构 + README.md
}
```

**验收标准**:
- [ ] 正确解析 TODO markdown
- [ ] 正确解析 Idea frontmatter
- [ ] 正确解析 Project 目录

**预估时间**: 2 小时

---

### P1 - 增强功能

#### Task 4.7: 实时状态同步

**文件**:
- [ ] `src/hooks/useStatus.ts` - 状态轮询 Hook
- [ ] `src/hooks/useWs.ts` - WebSocket Hook
- [ ] `src/components/LiveIndicator.tsx` - 实时指示器

**设计**:

```typescript
// src/hooks/useStatus.ts
function useStatus(pollInterval = 5000) {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  
  useEffect(() => {
    const fetchStatus = async () => {
      const data = await api.get<StatusResponse>("/status");
      setStatus(data);
    };
    
    fetchStatus();
    const interval = setInterval(fetchStatus, pollInterval);
    return () => clearInterval(interval);
  }, [pollInterval]);
  
  return status;
}

// src/hooks/useWs.ts
function useWs() {
  const [connected, setConnected] = useState(false);
  
  useEffect(() => {
    api.connectWs((msg) => {
      switch (msg.type) {
        case "status_change":
          statusStore.setState(msg.data.state);
          break;
        case "todo_update":
          todosStore.loadTodos();
          break;
      }
    });
    
    return () => api.disconnectWs();
  }, []);
  
  return { connected };
}
```

**验收标准**:
- [ ] 5 秒轮询更新
- [ ] WebSocket 实时推送
- [ ] 连接状态指示

**预估时间**: 2 小时

---

#### Task 4.8: 任务高亮联动

**文件**:
- [ ] `src/components/ActiveIndicator.tsx`
- [ ] `src/hooks/useTaskHighlight.ts`

**设计**:

```typescript
// 检测当前执行的任务
function getActiveTaskFromSession(session: Session): string | null {
  // 从 message 或 prompt 中提取任务关键词
  // 匹配 TODO/Project 标题
}

// 高亮组件
function ActiveHighlight({ taskId }: { taskId: string }) {
  const { pulse } = useAnimation();
  
  return (
    <div className={`highlight ${pulse ? "pulse" : ""}`}>
      <div className="ripple" />
    </div>
  );
}
```

**验收标准**:
- [ ] 执行任务时高亮对应 TODO
- [ ] 高亮动画效果
- [ ] 任务完成后自动取消

**预估时间**: 2 小时

---

#### Task 4.9: 备注持久化

**文件**:
- [ ] `src/components/NotesEditor.tsx`
- [ ] `src/api/notes.ts`

**设计**:

```typescript
// 备注存储位置
// - 内存: Zustand store
// - 持久化: localStorage + 定期同步到文件

interface Note {
  id: string;
  content: string;
  createdAt: string;
  updatedAt: string;
}

function saveNote(itemId: string, note: Note) {
  // 1. 更新 localStorage
  localStorage.setItem(`notes:${itemId}`, JSON.stringify(note));
  
  // 2. 同步到文件 (可选)
  // 追加到 TODO 文件的备注区域
  
  // 3. 发送到后端 (可选)
  api.post(`/items/${itemId}/notes`, note);
}
```

**验收标准**:
- [ ] 添加备注
- [ ] 编辑备注
- [ ] 删除备注
- [ ] localStorage 持久化

**预估时间**: 2 小时

---

### P2 - 后端服务

#### Task 4.10: Express API 服务器

**目录**: `backend/`

**文件**:
- [ ] `package.json`
- [ ] `src/index.ts` - 服务入口
- [ ] `src/routes/status.ts` - 状态路由
- [ ] `src/routes/todos.ts` - TODO 路由
- [ ] `src/routes/ideas.ts` - Ideas 路由
- [ ] `src/routes/projects.ts` - Projects 路由
- [ ] `src/routes/notes.ts` - 备注路由
- [ ] `src/ws/handler.ts` - WebSocket 处理器

**设计**:

```typescript
// src/index.ts
import express from "express";
import { createWsHandler } from "./ws/handler.js";

const app = express();
const server = createServer(app);
const wsHandler = createWsHandler(server);

app.use(express.json());

// Routes
app.get("/api/status", statusHandler);
app.get("/api/todos", todosHandler);
app.get("/api/ideas", ideasHandler);
app.get("/api/projects", projectsHandler);
app.post("/api/items/:id/notes", notesHandler);

// WebSocket
wsHandler.on("status_change", (data) => {
  wsHandler.broadcast({ type: "status_change", data });
});

server.listen(3000, () => {
  console.log("Dashboard API server running on port 3000");
});
```

**验收标准**:
- [ ] API 服务启动
- [ ] 所有端点返回正确数据
- [ ] WebSocket 正常工作

**预估时间**: 3 小时

---

#### Task 4.11: OpenClaw 状态集成

**文件**:
- [ ] `src/integrations/openclaw.ts`

**设计**:

```typescript
// 读取 OpenClaw 状态
async function getOpenClawStatus(): Promise<StatusResponse> {
  // 1. 读取会话文件
  const sessionsPath = path.join(os.homedir(), ".openclaw/sessions/");
  const sessions = await readSessions(sessionsPath);
  
  // 2. 获取当前活跃会话
  const activeSession = sessions.find(s => 
    Date.now() - s.updatedAt < IDLE_THRESHOLD
  );
  
  // 3. 解析状态
  const state = determineState(activeSession);
  
  return {
    state,
    currentSession: activeSession ? {
      sessionId: activeSession.sessionId,
      model: activeSession.model,
      channel: activeSession.channel,
      lastActivity: activeSession.updatedAt,
    } : null,
    tokenUsage: {
      input: activeSession?.inputTokens ?? 0,
      output: activeSession?.outputTokens ?? 0,
      total: activeSession?.totalTokens ?? 0,
    },
    lastHeartbeat: activeSession?.lastHeartbeatText,
  };
}

function determineState(session: SessionEntry): StatusState["state"] {
  if (!session) return "idle";
  if (session.abortedLastRun) return "error";
  if (session.lastHeartbeatSentAt) {
    const diff = Date.now() - session.lastHeartbeatSentAt;
    if (diff < 5000) return "thinking";
  }
  return "executing";
}
```

**验收标准**:
- [ ] 正确读取 OpenClaw 会话
- [ ] 状态判断逻辑正确
- [ ] Token 统计准确

**预估时间**: 2 小时

---

### P2 - 部署与优化

#### Task 4.12: 打包与部署

**文件**:
- [ ] `Dockerfile`
- [ ] `docker-compose.yml`
- [ ] `.env.example`
- [ ] `部署文档 DEPLOY.md`

**验收标准**:
- [ ] Docker 镜像构建成功
- [ ] docker-compose 启动
- [ ] 文档完整

**预估时间**: 1 小时

---

#### Task 4.13: 性能优化

**优化项**:
- [ ] 代码分割 (Code Splitting)
- [ ] 懒加载 (Lazy Loading)
- [ ] 虚拟滚动 (Virtual Scroll) - 大列表
- [ ] 缓存策略

**验收标准**:
- [ ] Lighthouse 性能 > 80
- [ ] 首屏加载 < 2s

**预估时间**: 2 小时

---

## 5. 项目结构

```
frontend/dashboard/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── index.html
├── public/
│   └── mascot/          # 公仔动画素材
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── App.css
│   ├── api/
│   │   ├── client.ts
│   │   ├── endpoints.ts
│   │   └── websocket.ts
│   ├── store/
│   │   ├── index.ts
│   │   ├── status.ts
│   │   ├── todos.ts
│   │   ├── ideas.ts
│   │   └── projects.ts
│   ├── components/
│   │   ├── Mascot/
│   │   │   ├── index.tsx
│   │   │   ├── Mascot.css
│   │   │   └── animations/
│   │   ├── Board/
│   │   │   ├── index.tsx
│   │   │   ├── Column.tsx
│   │   │   ├── Card.tsx
│   │   │   └── CardModal.tsx
│   │   ├── LiveIndicator.tsx
│   │   └── ActiveHighlight.tsx
│   ├── hooks/
│   │   ├── useStatus.ts
│   │   ├── useWs.ts
│   │   └── useTaskHighlight.ts
│   ├── parsers/
│   │   ├── todo.ts
│   │   ├── idea.ts
│   │   └── project.ts
│   └── types/
│       └── index.ts
│
backend/
├── package.json
├── src/
│   ├── index.ts
│   ├── routes/
│   │   ├── status.ts
│   │   ├── todos.ts
│   │   ├── ideas.ts
│   │   ├── projects.ts
│   │   └── notes.ts
│   ├── ws/
│   │   └── handler.ts
│   └── integrations/
│       └── openclaw.ts
│
├── Dockerfile
├── docker-compose.yml
└── DEPLOY.md
```

---

## 6. 开发顺序

```
Week 1
├── Day 1
│   ├── Task 4.1 项目脚手架 (0.5h)
│   └── Task 4.2 状态管理 Store (1h)
├── Day 2
│   ├── Task 4.3 API 客户端层 (1h)
│   └── Task 4.6 数据解析器 (2h)
├── Day 3
│   └── Task 4.4 公仔动画组件 (3h)
├── Day 4
│   └── Task 4.5 Trello 看板组件 (3h)
└── Day 5
    ├── Task 4.7 实时状态同步 (2h)
    └── Task 4.8 任务高亮联动 (2h)

Week 2
├── Day 1
│   ├── Task 4.9 备注持久化 (2h)
│   └── Task 4.10 Express API 服务器 (3h)
├── Day 2
│   └── Task 4.11 OpenClaw 状态集成 (2h)
├── Day 3
│   ├── Task 4.12 打包与部署 (1h)
│   └── Task 4.13 性能优化 (2h)
└── Day 4-5
    └── 测试与修复
```

---

## 7. 依赖清单

### 前端依赖

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "zustand": "^4.5.0",
    "framer-motion": "^11.0.0",
    "lucide-react": "^0.300.0",
    "axios": "^1.6.0",
    "date-fns": "^3.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

### 后端依赖

```json
{
  "dependencies": {
    "express": "^4.18.0",
    "ws": "^8.16.0",
    "cors": "^2.8.5",
    "dotenv": "^16.4.0",
    "chokidar": "^3.6.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.0",
    "@types/ws": "^8.5.0",
    "@types/cors": "^2.8.0",
    "typescript": "^5.3.0"
  }
}
```

---

## 8. 风险与挑战

| 风险 | 缓解措施 |
|------|----------|
| OpenClaw 状态格式变化 | 抽象状态解析层，易于适配 |
| 公仔动画制作耗时 | 先用 SVG/emoji，后期替换精细动画 |
| WebSocket 稳定性 | 自动重连、心跳检测 |
| 大列表性能 | 虚拟滚动、懒加载 |

---

## 9. 验收测试

### 功能测试

- [ ] 公仔 4 状态动画正确显示
- [ ] TODO 列表正确解析和显示
- [ ] Ideas 列表正确解析和显示
- [ ] Projects 列表正确解析和显示
- [ ] 悬浮显示详情
- [ ] Modal 添加备注
- [ ] 实时状态更新
- [ ] 任务执行时高亮

### 性能测试

- [ ] 首屏加载 < 2s
- [ ] 状态更新无感知
- [ ] 100+ TODO 项流畅滚动

### 兼容性测试

- [ ] Chrome 最新版
- [ ] Safari 最新版
- [ ] Firefox 最新版

---

*文档版本: 1.0*
*创建时间: 2026-02-01*
*作者: Monday AI*
