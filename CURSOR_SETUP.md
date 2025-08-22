# 🖥️ Cursor での YouTube Transcriber セットアップガイド

このガイドでは、Cursor エディタで YouTube Transcriber を効率的に使用する方法を説明します。

## 📦 Cursorでのプロジェクト設定

### 1. プロジェクトを開く

```bash
# ターミナルでプロジェクトフォルダに移動
cd path/to/youtube-transcriber

# Cursorでフォルダを開く
cursor .
```

または、Cursor の GUI から「Open Folder」で `youtube-transcriber` フォルダを選択します。

### 2. Python環境の設定

Cursor で Python インタープリターを設定：

1. `Cmd+Shift+P` (macOS) または `Ctrl+Shift+P` (Windows/Linux)
2. 「Python: Select Interpreter」を選択
3. `.venv/bin/python` (macOS/Linux) または `.venv\Scripts\python.exe` (Windows) を選択

### 3. 統合ターミナルの使用

Cursor の統合ターミナルを開く：
- `Ctrl+`` (バッククォート) または
- メニューから「Terminal > New Terminal」

## 🚀 Cursor での使用方法

### ターミナルでの実行

```bash
# 仮想環境をアクティベート
source .venv/bin/activate

# 文字起こし実行
python transcribe_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### ファイルの直接実行

1. `transcribe_youtube.py` を開く
2. `F5` または右上の再生ボタンをクリック
3. 実行時に引数を指定するプロンプトが表示される

## 🔧 便利な Cursor 機能

### 1. タスクの自動化

`.vscode/tasks.json` を作成して定型作業を自動化：

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "YouTube Transcribe",
            "type": "shell",
            "command": "python",
            "args": [
                "transcribe_youtube.py",
                "${input:youtubeUrl}",
                "--output",
                "output/${input:fileName}.md"
            ],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "options": {
                "cwd": "${workspaceFolder}"
            }
        }
    ],
    "inputs": [
        {
            "id": "youtubeUrl",
            "description": "YouTube URL",
            "default": "",
            "type": "promptString"
        },
        {
            "id": "fileName",
            "description": "Output file name (without extension)",
            "default": "transcript",
            "type": "promptString"
        }
    ]
}
```

### 2. ショートカットキーの設定

`.vscode/keybindings.json` でカスタムショートカットを設定：

```json
[
    {
        "key": "ctrl+shift+t",
        "command": "workbench.action.tasks.runTask",
        "args": "YouTube Transcribe"
    }
]
```

### 3. スニペットの活用

`.vscode/python.json` でよく使うコマンドをスニペット化：

```json
{
    "YouTube Transcribe Command": {
        "prefix": "yt-transcribe",
        "body": [
            "python transcribe_youtube.py \"$1\" --output output/$2.md --format md"
        ],
        "description": "YouTube transcribe command"
    }
}
```

## 📁 推奨フォルダ構成

```
youtube-transcriber/
├── .venv/                 # 仮想環境
├── .vscode/              # Cursor設定
│   ├── settings.json
│   ├── tasks.json
│   └── keybindings.json
├── output/               # 出力ファイル
├── transcribe_youtube.py # メインスクリプト
├── requirements.txt      # 依存関係
├── README.md            # プロジェクト説明
├── INSTALL.md           # インストールガイド
└── CURSOR_SETUP.md      # このファイル
```

## 🎯 ワークフロー例

### 日常的な使用パターン

1. **Cursor でプロジェクトを開く**
2. **統合ターミナルで仮想環境をアクティベート**
   ```bash
   source .venv/bin/activate
   ```
3. **YouTube URL をコピー**
4. **文字起こし実行**
   ```bash
   python transcribe_youtube.py "貼り付けたURL"
   ```
5. **`output/` フォルダの結果をCursorで確認・編集**

### バッチ処理

複数の動画を一度に処理する場合：

```bash
# 複数のURLを処理するスクリプト例
urls=(
    "https://www.youtube.com/watch?v=VIDEO_ID1"
    "https://www.youtube.com/watch?v=VIDEO_ID2"
    "https://www.youtube.com/watch?v=VIDEO_ID3"
)

for url in "${urls[@]}"; do
    video_id=$(echo $url | sed 's/.*v=//')
    python transcribe_youtube.py "$url" --output "output/${video_id}.md"
done
```

## 🔍 デバッグとトラブルシューティング

### Cursor でのデバッグ

1. `transcribe_youtube.py` にブレークポイントを設定
2. `F5` でデバッグモードで実行
3. 変数の値やエラーを詳細に確認

### よくある問題

- **仮想環境が認識されない**: Python インタープリターの設定を確認
- **モジュールが見つからない**: `pip install -r requirements.txt` を再実行
- **権限エラー**: ターミナルの権限設定を確認

## 💡 効率化のヒント

1. **エイリアスの作成**: よく使うコマンドをエイリアス化
2. **出力フォルダの整理**: 日付別、カテゴリ別にフォルダを分ける
3. **結果の確認**: Cursor のMarkdownプレビュー機能を活用
4. **バージョン管理**: Git でプロジェクトを管理

## 🤝 チーム開発

チームで使用する場合の推奨設定：

- `.vscode/settings.json` をリポジトリに含める
- 共通のタスクとスニペットを定義
- 出力フォルダの命名規則を統一

これで Cursor での YouTube Transcriber の効率的な使用が可能になります！
