import { create } from 'zustand';
import { TodoItem } from '../types';

interface TodoStore {
  items: TodoItem[];
  activeItemId: string | null;
  
  setTodos: (items: TodoItem[]) => void;
  setActiveItem: (id: string | null) => void;
  updateTodo: (id: string, updates: Partial<TodoItem>) => void;
}

export const useTodoStore = create<TodoStore>((set) => ({
  items: [],
  activeItemId: null,
  
  setTodos: (items) => set({ items }),
  setActiveItem: (id) => set({ activeItemId: id }),
  updateTodo: (id, updates) => set((state) => ({
    items: state.items.map(item => item.id === id ? { ...item, ...updates } : item)
  }))
}));
