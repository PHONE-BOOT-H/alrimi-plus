export interface Source {
  n: number;
  title: string | null;
  source_type: string;
  source_url: string | null;
  similarity: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  model?: string;
}

export interface School {
  school_code: string;
  school_name: string;
  school_type: string | null;
  region: string | null;
}
