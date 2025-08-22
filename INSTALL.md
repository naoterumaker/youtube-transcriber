# YouTube Transcriber インストールガイド

YouTube動画の文字起こしを簡単に行うPythonツールです。

## 📋 必要な環境

- Python 3.8以上
- pip（Pythonパッケージマネージャー）

## 🚀 インストール方法

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-username/youtube-transcriber.git
cd youtube-transcriber
```

### 2. 仮想環境の作成（推奨）

```bash
# 仮想環境を作成
python3 -m venv .venv

# 仮想環境をアクティベート
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

## 📖 使い方

### 基本的な使い方

```bash
python transcribe_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### オプション付きの使い方

```bash
# 出力ファイル名を指定
python transcribe_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID" \
  --output output/my_transcript.md

# テキスト形式で出力
python transcribe_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID" \
  --format txt
```

### 利用可能なオプション

- `--output`: 出力ファイルのパス（デフォルト: `output/transcript.md`）
- `--format`: 出力形式（`md` または `txt`、デフォルト: `md`）

## 🔧 Cursor での使い方

### 1. プロジェクトを開く

Cursorで `youtube-transcriber` フォルダを開きます。

### 2. ターミナルでコマンド実行

Cursor内のターミナルで以下を実行：

```bash
# 仮想環境をアクティベート
source .venv/bin/activate

# 文字起こし実行
python transcribe_youtube.py "YouTube URL"
```

### 3. 結果の確認

`output/` フォルダに生成されたMarkdownファイルをCursorで開いて確認できます。

## 🌍 対応言語

このツールは以下の優先順位で字幕を取得します：

1. 日本語 (`ja`, `ja-JP`)
2. 英語 (`en`, `en-US`)
3. その他利用可能な言語

## 📁 出力形式

### Markdown形式（デフォルト）

```markdown
# YouTube Transcript

**URL:** https://www.youtube.com/watch?v=VIDEO_ID

**Generated:** 2025-01-22 12:34:56

---

文字起こし内容がここに表示されます...
```

### テキスト形式

```
文字起こし内容がここに表示されます...
```

## ⚠️ トラブルシューティング

### よくある問題

1. **字幕が見つからない**: 動画に字幕が存在しない場合はエラーになります
2. **プライベート動画**: 非公開動画の文字起こしはできません
3. **ネットワークエラー**: インターネット接続を確認してください

### エラーメッセージの例

```
RuntimeError: Could not fetch transcript: No transcripts available for this video
```

→ この動画には字幕が利用できません。

## 🔄 アップデート

```bash
# リポジトリを更新
git pull origin main

# 依存関係を更新
pip install -r requirements.txt --upgrade
```

## 📞 サポート

問題が発生した場合は、GitHubのIssuesページで報告してください。

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。
