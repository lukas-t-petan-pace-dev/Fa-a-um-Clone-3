/**
 * Nexus AI BR Framework - Node.js Wrapper
 * 
 * Este módulo fornece uma interface JavaScript/TypeScript
 * para interagir com o framework Python Nexus AI BR.
 * 
 * @example
 * const { Agent } = require('./index.js');
 * 
 * const agent = new Agent({
 *   name: 'MeuBot',
 *   goal: 'Ajudar o usuário',
 *   reasoning: 'deterministic',
 *   tools: [minhaFuncao]
 * });
 * 
 * const response = await agent.run('Olá');
 */

const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

const FRAMEWORK_PATH = path.join(__dirname);

class NexusAIAgent {
  constructor(config) {
    this.name = config.name || 'Agent';
    this.goal = config.goal || '';
    this.reasoning = config.reasoning || 'deterministic';
    this.tools = config.tools || [];
    this.useTokens = config.useTokens || false;
    this.verbose = config.verbose !== false;
    this.tempFile = null;
  }

  async _createTempScript() {
    const toolsCode = this.tools.map(tool => {
      if (typeof tool === 'function') {
        const name = tool.name || 'tool';
        const code = tool.toString();
        return `
def ${name}(*args, **kwargs):
    ${code.replace(/\n/g, '\n    ')}
`;
      }
      return '';
    }).join('\n');

    const reasoningMap = {
      'deterministic': 'DeterministicReasoning',
      'rulebased': 'RuleBasedReasoning',
      'simulated': 'SimulatedLLMReasoning',
      'llm': 'LLMReasoning'
    };

    const reasoningClass = reasoningMap[this.reasoning.toLowerCase()] || 'DeterministicReasoning';

    const script = `
import sys
sys.path.insert(0, '${FRAMEWORK_PATH.replace(/\\/g, '\\\\')}')

from framework import Agent, ${reasoningClass}

${toolsCode}

_agent = Agent(
    name="${this.name}",
    goal="${this.goal}",
    reasoning=${reasoningClass}(),
    use_tokens=${this.useTokens},
    verbose=${this.verbose}
)

${this.tools.map(tool => {
  const name = typeof tool === 'function' ? (tool.name || 'tool') : 'tool';
  return `_agent.add_tool(${name})`;
}).join('\n')}

if __name__ == "__main__":
    import json
    task = sys.argv[1] if len(sys.argv) > 1 else ""
    result = _agent.run(task)
    print(json.dumps({"status": "success", "result": result}))
`;

    const tempDir = os.tmpdir();
    this.tempFile = path.join(tempDir, `aegis_${Date.now()}.py`);
    fs.writeFileSync(this.tempFile, script, 'utf8');
  }

  async run(task) {
    await this._createTempScript();
    
    return new Promise((resolve, reject) => {
      const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
      
      const proc = spawn(pythonCmd, [this.tempFile, task], {
        cwd: FRAMEWORK_PATH,
        shell: true
      });

      let output = '';
      let errorOutput = '';

      proc.stdout.on('data', (data) => {
        output += data.toString();
      });

      proc.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });

      proc.on('close', (code) => {
        try {
          fs.unlinkSync(this.tempFile);
        } catch (e) {}

        if (code === 0) {
          try {
            const result = JSON.parse(output.trim());
            resolve(result.result);
          } catch {
            resolve(output.trim());
          }
        } else {
          reject(new Error(errorOutput || `Process exited with code ${code}`));
        }
      });

      proc.on('error', (err) => {
        reject(err);
      });
    });
  }

  async chat() {
    console.log(`\n🤖 ${this.name} - Chat Interativo`);
    console.log(`Objetivo: ${this.goal}`);
    console.log('Digite "sair" para encerrar\n');

    const readline = require('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    const ask = () => {
      rl.question('Você: ', async (input) => {
        if (input.toLowerCase() === 'sair') {
          rl.close();
          return;
        }

        try {
          const response = await this.run(input);
          console.log(`\nAgent: ${response}\n`);
        } catch (err) {
          console.error(`Erro: ${err.message}\n`);
        }

        ask();
      });
    };

    ask();
  }
}

function createAgent(config) {
  return new NexusAIAgent(config);
}

function runAgentFile(filePath, task = null) {
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
  
  const args = task 
    ? ['-m', 'framework.cli', 'run', filePath, task]
    : ['-m', 'framework.cli', 'run', filePath];

  const proc = spawn(pythonCmd, args, {
    cwd: FRAMEWORK_PATH,
    stdio: 'inherit',
    shell: true
  });

  proc.on('close', (code) => {
    process.exit(code || 0);
  });
}

function chatWithAgentFile(filePath) {
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
  
  const proc = spawn(pythonCmd, ['-m', 'framework.cli', 'chat', filePath], {
    cwd: FRAMEWORK_PATH,
    stdio: 'inherit',
    shell: true
  });

  proc.on('close', (code) => {
    process.exit(code || 0);
  });
}

function initProject(name) {
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
  
  const proc = spawn(pythonCmd, ['-m', 'framework.cli', 'init', name], {
    cwd: FRAMEWORK_PATH,
    stdio: 'inherit',
    shell: true
  });

  proc.on('close', (code) => {
    process.exit(code || 0);
  });
}

module.exports = {
  NexusAIAgent,
  Agent: NexusAIAgent,
  createAgent,
  runAgentFile,
  chatWithAgentFile,
  initProject,
  FRAMEWORK_PATH
};
