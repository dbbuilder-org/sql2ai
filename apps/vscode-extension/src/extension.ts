import * as vscode from 'vscode';
import { Sql2AiApiClient } from './services/apiClient';
import { ConnectionsProvider } from './providers/connectionsProvider';
import { HistoryProvider } from './providers/historyProvider';
import { registerCommands } from './commands';

let apiClient: Sql2AiApiClient;

export function activate(context: vscode.ExtensionContext) {
    console.log('SQL2.AI extension is now active');

    // Initialize API client
    const config = vscode.workspace.getConfiguration('sql2ai');
    apiClient = new Sql2AiApiClient(
        config.get('apiUrl') || 'https://api.sql2.ai',
        config.get('apiKey') || ''
    );

    // Register tree view providers
    const connectionsProvider = new ConnectionsProvider(apiClient);
    const historyProvider = new HistoryProvider(context);

    vscode.window.registerTreeDataProvider('sql2ai.connections', connectionsProvider);
    vscode.window.registerTreeDataProvider('sql2ai.history', historyProvider);

    // Register all commands
    registerCommands(context, apiClient, historyProvider);

    // Watch for configuration changes
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('sql2ai')) {
                const newConfig = vscode.workspace.getConfiguration('sql2ai');
                apiClient.updateConfig(
                    newConfig.get('apiUrl') || 'https://api.sql2.ai',
                    newConfig.get('apiKey') || ''
                );
            }
        })
    );

    // Register code lens provider for optimization hints
    if (config.get('showInlineHints')) {
        const codeLensProvider = new SqlCodeLensProvider(apiClient);
        context.subscriptions.push(
            vscode.languages.registerCodeLensProvider(
                { language: 'sql' },
                codeLensProvider
            )
        );
    }

    // Status bar item
    const statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.text = '$(database) SQL2.AI';
    statusBarItem.tooltip = 'SQL2.AI - Click to connect';
    statusBarItem.command = 'sql2ai.connect';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
}

export function deactivate() {
    console.log('SQL2.AI extension deactivated');
}

export function getApiClient(): Sql2AiApiClient {
    return apiClient;
}

class SqlCodeLensProvider implements vscode.CodeLensProvider {
    constructor(private apiClient: Sql2AiApiClient) {}

    provideCodeLenses(document: vscode.TextDocument): vscode.CodeLens[] {
        const codeLenses: vscode.CodeLens[] = [];
        const text = document.getText();

        // Find SELECT statements
        const selectRegex = /\bSELECT\b/gi;
        let match;

        while ((match = selectRegex.exec(text)) !== null) {
            const position = document.positionAt(match.index);
            const range = new vscode.Range(position, position);

            codeLenses.push(
                new vscode.CodeLens(range, {
                    title: '$(zap) Optimize',
                    command: 'sql2ai.optimizeQuery',
                    tooltip: 'Optimize this query with AI'
                })
            );
        }

        return codeLenses;
    }
}
