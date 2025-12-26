import * as vscode from 'vscode';
import { Sql2AiApiClient, Connection } from '../services/apiClient';

export class ConnectionsProvider implements vscode.TreeDataProvider<ConnectionItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<ConnectionItem | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    constructor(private apiClient: Sql2AiApiClient) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: ConnectionItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: ConnectionItem): Promise<ConnectionItem[]> {
        if (element) {
            return [];
        }

        try {
            const connections = await this.apiClient.listConnections();
            return connections.map(c => new ConnectionItem(c));
        } catch (error) {
            return [
                new ConnectionItem({
                    id: 'error',
                    name: 'Unable to load connections',
                    db_type: 'postgresql',
                    host: '',
                    database: '',
                    status: 'error',
                }),
            ];
        }
    }
}

class ConnectionItem extends vscode.TreeItem {
    constructor(public readonly connection: Connection) {
        super(connection.name, vscode.TreeItemCollapsibleState.None);

        this.description = `${connection.db_type} - ${connection.database}`;
        this.tooltip = `${connection.host}/${connection.database}`;

        // Set icon based on status
        const iconColor = connection.status === 'connected'
            ? 'testing.iconPassed'
            : connection.status === 'error'
                ? 'testing.iconFailed'
                : 'testing.iconQueued';

        this.iconPath = new vscode.ThemeIcon('database', new vscode.ThemeColor(iconColor));

        this.contextValue = 'connection';
    }
}
