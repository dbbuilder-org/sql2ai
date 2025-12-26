import * as vscode from 'vscode';
import { Sql2AiApiClient } from '../services/apiClient';
import { HistoryProvider } from '../providers/historyProvider';

export function registerCommands(
    context: vscode.ExtensionContext,
    apiClient: Sql2AiApiClient,
    historyProvider: HistoryProvider
) {
    // Optimize Query
    context.subscriptions.push(
        vscode.commands.registerCommand('sql2ai.optimizeQuery', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            const selection = editor.selection;
            const sql = selection.isEmpty
                ? editor.document.getText()
                : editor.document.getText(selection);

            if (!sql.trim()) {
                vscode.window.showWarningMessage('No SQL to optimize');
                return;
            }

            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'Optimizing query...',
                    cancellable: false,
                },
                async () => {
                    try {
                        const config = vscode.workspace.getConfiguration('sql2ai');
                        const dbType = config.get('defaultDatabase') as string;

                        const result = await apiClient.optimizeQuery(sql, dbType);

                        // Show result in new document
                        const doc = await vscode.workspace.openTextDocument({
                            language: 'sql',
                            content: `-- Original Query:\n${result.original_query}\n\n-- Optimized Query:\n${result.optimized_query}\n\n-- Suggestions:\n${result.suggestions.map(s => `-- ${s}`).join('\n')}\n\n-- Estimated Improvement: ${result.estimated_improvement}`,
                        });
                        await vscode.window.showTextDocument(doc, { preview: false });

                        historyProvider.addEntry('optimize', sql, result.optimized_query);
                    } catch (error: any) {
                        vscode.window.showErrorMessage(`Optimization failed: ${error.message}`);
                    }
                }
            );
        })
    );

    // Explain Query
    context.subscriptions.push(
        vscode.commands.registerCommand('sql2ai.explainQuery', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            const selection = editor.selection;
            const sql = selection.isEmpty
                ? editor.document.getText()
                : editor.document.getText(selection);

            if (!sql.trim()) {
                vscode.window.showWarningMessage('No SQL to explain');
                return;
            }

            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'Explaining query...',
                    cancellable: false,
                },
                async () => {
                    try {
                        const config = vscode.workspace.getConfiguration('sql2ai');
                        const dbType = config.get('defaultDatabase') as string;

                        const result = await apiClient.explainQuery(sql, dbType);

                        // Show in output panel
                        const outputChannel = vscode.window.createOutputChannel('SQL2.AI Explanation');
                        outputChannel.clear();
                        outputChannel.appendLine('=== Query Explanation ===\n');
                        outputChannel.appendLine(result.explanation);
                        outputChannel.appendLine('\n=== Execution Steps ===\n');
                        result.steps.forEach((step, i) => {
                            outputChannel.appendLine(`${i + 1}. ${step}`);
                        });
                        outputChannel.appendLine(`\nComplexity: ${result.complexity}`);
                        if (result.estimated_rows) {
                            outputChannel.appendLine(`Estimated Rows: ${result.estimated_rows}`);
                        }
                        outputChannel.show();

                        historyProvider.addEntry('explain', sql, result.explanation);
                    } catch (error: any) {
                        vscode.window.showErrorMessage(`Explanation failed: ${error.message}`);
                    }
                }
            );
        })
    );

    // Review Code
    context.subscriptions.push(
        vscode.commands.registerCommand('sql2ai.reviewCode', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            const sql = editor.document.getText();
            if (!sql.trim()) {
                vscode.window.showWarningMessage('No SQL to review');
                return;
            }

            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'Reviewing code...',
                    cancellable: false,
                },
                async () => {
                    try {
                        const config = vscode.workspace.getConfiguration('sql2ai');
                        const dbType = config.get('defaultDatabase') as string;

                        const result = await apiClient.reviewCode(sql, dbType);

                        // Show diagnostics
                        const diagnosticCollection = vscode.languages.createDiagnosticCollection('sql2ai');
                        const diagnostics: vscode.Diagnostic[] = [];

                        result.issues.forEach(issue => {
                            const severity = issue.severity === 'error'
                                ? vscode.DiagnosticSeverity.Error
                                : issue.severity === 'warning'
                                    ? vscode.DiagnosticSeverity.Warning
                                    : vscode.DiagnosticSeverity.Information;

                            const line = issue.line ? issue.line - 1 : 0;
                            const range = new vscode.Range(line, 0, line, 1000);

                            const diagnostic = new vscode.Diagnostic(
                                range,
                                `[${issue.rule}] ${issue.message}`,
                                severity
                            );
                            diagnostics.push(diagnostic);
                        });

                        diagnosticCollection.set(editor.document.uri, diagnostics);

                        // Show summary
                        vscode.window.showInformationMessage(
                            `Code Review: Score ${result.score}/100 - ${result.summary}`
                        );

                        historyProvider.addEntry('review', sql, result.summary);
                    } catch (error: any) {
                        vscode.window.showErrorMessage(`Review failed: ${error.message}`);
                    }
                }
            );
        })
    );

    // Generate from Prompt
    context.subscriptions.push(
        vscode.commands.registerCommand('sql2ai.generateFromPrompt', async () => {
            const prompt = await vscode.window.showInputBox({
                prompt: 'Describe the SQL you want to generate',
                placeHolder: 'e.g., Create a query to find customers who ordered in the last 30 days',
            });

            if (!prompt) {
                return;
            }

            const editor = vscode.window.activeTextEditor;
            const context = editor ? editor.document.getText() : undefined;

            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'Generating SQL...',
                    cancellable: false,
                },
                async () => {
                    try {
                        const config = vscode.workspace.getConfiguration('sql2ai');
                        const dbType = config.get('defaultDatabase') as string;

                        const result = await apiClient.generateSql(prompt, dbType, context);

                        // Insert at cursor or open new document
                        if (editor) {
                            await editor.edit(editBuilder => {
                                const position = editor.selection.active;
                                editBuilder.insert(position, `\n${result.sql}\n`);
                            });
                        } else {
                            const doc = await vscode.workspace.openTextDocument({
                                language: 'sql',
                                content: `-- Generated SQL\n-- Prompt: ${prompt}\n\n${result.sql}`,
                            });
                            await vscode.window.showTextDocument(doc);
                        }

                        historyProvider.addEntry('generate', prompt, result.sql);
                    } catch (error: any) {
                        vscode.window.showErrorMessage(`Generation failed: ${error.message}`);
                    }
                }
            );
        })
    );

    // Generate CRUD
    context.subscriptions.push(
        vscode.commands.registerCommand('sql2ai.generateCrud', async () => {
            const tableName = await vscode.window.showInputBox({
                prompt: 'Enter the table name',
                placeHolder: 'e.g., Customers',
            });

            if (!tableName) {
                return;
            }

            const schema = await vscode.window.showInputBox({
                prompt: 'Enter the schema (optional)',
                placeHolder: 'e.g., dbo',
                value: 'dbo',
            });

            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'Generating CRUD procedures...',
                    cancellable: false,
                },
                async () => {
                    try {
                        const config = vscode.workspace.getConfiguration('sql2ai');
                        const dbType = config.get('defaultDatabase') as string;

                        const result = await apiClient.generateCrud(tableName, schema || 'dbo', dbType);

                        const doc = await vscode.workspace.openTextDocument({
                            language: 'sql',
                            content: `-- CRUD Procedures for ${schema}.${tableName}\n\n${result.sql}`,
                        });
                        await vscode.window.showTextDocument(doc);

                        historyProvider.addEntry('crud', tableName, result.sql);
                    } catch (error: any) {
                        vscode.window.showErrorMessage(`CRUD generation failed: ${error.message}`);
                    }
                }
            );
        })
    );

    // Analyze Execution Plan
    context.subscriptions.push(
        vscode.commands.registerCommand('sql2ai.analyzeExecutionPlan', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            const plan = editor.document.getText();
            if (!plan.trim()) {
                vscode.window.showWarningMessage('No execution plan to analyze');
                return;
            }

            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'Analyzing execution plan...',
                    cancellable: false,
                },
                async () => {
                    try {
                        const config = vscode.workspace.getConfiguration('sql2ai');
                        const dbType = config.get('defaultDatabase') as string;

                        const result = await apiClient.analyzeExecutionPlan(plan, dbType);

                        const outputChannel = vscode.window.createOutputChannel('SQL2.AI Plan Analysis');
                        outputChannel.clear();
                        outputChannel.appendLine('=== Execution Plan Analysis ===\n');
                        outputChannel.appendLine(result.explanation);
                        outputChannel.appendLine('\n=== Recommendations ===\n');
                        result.steps.forEach((step, i) => {
                            outputChannel.appendLine(`${i + 1}. ${step}`);
                        });
                        outputChannel.show();
                    } catch (error: any) {
                        vscode.window.showErrorMessage(`Analysis failed: ${error.message}`);
                    }
                }
            );
        })
    );

    // Format SQL
    context.subscriptions.push(
        vscode.commands.registerCommand('sql2ai.formatSql', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            const sql = editor.document.getText();
            if (!sql.trim()) {
                return;
            }

            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'Formatting SQL...',
                    cancellable: false,
                },
                async () => {
                    try {
                        const config = vscode.workspace.getConfiguration('sql2ai');
                        const dbType = config.get('defaultDatabase') as string;

                        const formattedSql = await apiClient.formatSql(sql, dbType);

                        await editor.edit(editBuilder => {
                            const fullRange = new vscode.Range(
                                editor.document.positionAt(0),
                                editor.document.positionAt(sql.length)
                            );
                            editBuilder.replace(fullRange, formattedSql);
                        });
                    } catch (error: any) {
                        vscode.window.showErrorMessage(`Formatting failed: ${error.message}`);
                    }
                }
            );
        })
    );

    // Connect to Database
    context.subscriptions.push(
        vscode.commands.registerCommand('sql2ai.connect', async () => {
            try {
                const isHealthy = await apiClient.healthCheck();
                if (!isHealthy) {
                    const openSettings = await vscode.window.showErrorMessage(
                        'Cannot connect to SQL2.AI API. Check your settings.',
                        'Open Settings'
                    );
                    if (openSettings) {
                        vscode.commands.executeCommand('workbench.action.openSettings', 'sql2ai');
                    }
                    return;
                }

                const connections = await apiClient.listConnections();

                if (connections.length === 0) {
                    vscode.window.showInformationMessage(
                        'No connections found. Add connections at app.sql2.ai'
                    );
                    return;
                }

                const selected = await vscode.window.showQuickPick(
                    connections.map(c => ({
                        label: c.name,
                        description: `${c.db_type} - ${c.host}/${c.database}`,
                        detail: c.status,
                        connection: c,
                    })),
                    { placeHolder: 'Select a database connection' }
                );

                if (selected) {
                    const result = await apiClient.testConnection(selected.connection.id);
                    if (result.success) {
                        vscode.window.showInformationMessage(
                            `Connected to ${selected.label}: ${result.message}`
                        );
                    } else {
                        vscode.window.showErrorMessage(
                            `Connection failed: ${result.message}`
                        );
                    }
                }
            } catch (error: any) {
                vscode.window.showErrorMessage(`Connection error: ${error.message}`);
            }
        })
    );
}
