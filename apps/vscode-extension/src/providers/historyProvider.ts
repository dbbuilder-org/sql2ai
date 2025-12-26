import * as vscode from 'vscode';

interface HistoryEntry {
    type: 'optimize' | 'explain' | 'review' | 'generate' | 'crud';
    input: string;
    output: string;
    timestamp: Date;
}

export class HistoryProvider implements vscode.TreeDataProvider<HistoryItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<HistoryItem | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    private history: HistoryEntry[] = [];
    private readonly maxHistory = 50;

    constructor(private context: vscode.ExtensionContext) {
        // Load history from storage
        this.history = context.globalState.get('sql2ai.history', []);
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    addEntry(type: HistoryEntry['type'], input: string, output: string): void {
        this.history.unshift({
            type,
            input: input.substring(0, 100),
            output: output.substring(0, 200),
            timestamp: new Date(),
        });

        // Keep only last N entries
        if (this.history.length > this.maxHistory) {
            this.history = this.history.slice(0, this.maxHistory);
        }

        // Save to storage
        this.context.globalState.update('sql2ai.history', this.history);
        this.refresh();
    }

    clearHistory(): void {
        this.history = [];
        this.context.globalState.update('sql2ai.history', []);
        this.refresh();
    }

    getTreeItem(element: HistoryItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: HistoryItem): HistoryItem[] {
        if (element) {
            return [];
        }

        return this.history.map((entry, index) => new HistoryItem(entry, index));
    }
}

class HistoryItem extends vscode.TreeItem {
    constructor(
        public readonly entry: HistoryEntry,
        public readonly index: number
    ) {
        const label = entry.input.substring(0, 40) + (entry.input.length > 40 ? '...' : '');
        super(label, vscode.TreeItemCollapsibleState.None);

        const icons: Record<HistoryEntry['type'], string> = {
            optimize: 'zap',
            explain: 'info',
            review: 'checklist',
            generate: 'sparkle',
            crud: 'database',
        };

        this.iconPath = new vscode.ThemeIcon(icons[entry.type] || 'file');
        this.description = new Date(entry.timestamp).toLocaleTimeString();
        this.tooltip = `${entry.type.toUpperCase()}\n\nInput:\n${entry.input}\n\nOutput:\n${entry.output}`;
        this.contextValue = 'historyEntry';
    }
}
