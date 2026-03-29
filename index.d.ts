/**
 * Aegis AI Framework - TypeScript Definitions
 */

export interface AgentConfig {
  name: string;
  goal: string;
  reasoning?: 'deterministic' | 'rulebased' | 'simulated' | 'llm';
  useTokens?: boolean;
  verbose?: boolean;
  tools?: ToolFunction[];
}

export type ToolFunction = (args: any) => any;

export class AegisAgent {
  constructor(config: AgentConfig);
  
  run(task: string): Promise<string>;
  chat(): Promise<void>;
}

export function createAgent(config: AgentConfig): AegisAgent;
export function runAgentFile(filePath: string, task?: string): void;
export function chatWithAgentFile(filePath: string): void;
export function initProject(name: string): void;

export const FRAMEWORK_PATH: string;
