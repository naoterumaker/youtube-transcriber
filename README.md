# 🎬 YouTube Transcriber

YouTube動画を簡単に文字起こしできるPythonツールです。

## ✨ 特徴

- 🚀 **簡単操作**: YouTube URLを入力するだけで文字起こし完了
- 🌍 **多言語対応**: 日本語・英語を優先的に、その他の言語にも対応
- 📝 **複数の出力形式**: Markdown・テキスト形式で出力可能
- 🔧 **Cursor対応**: 開発環境での利用に最適化

## 🚀 クイックスタート

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/your-username/youtube-transcriber.git
cd youtube-transcriber

# 仮想環境を作成してアクティベート
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 依存関係をインストール
pip install -r requirements.txt
```

### 使い方

```bash
# 基本的な使い方
python3 transcribe_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID"

# 出力ファイル名を指定
python3 transcribe_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID" \
  --output output/my_transcript.md --format md
```

## 📖 詳細な使い方

詳しいインストール手順や使い方については、[INSTALL.md](INSTALL.md) をご覧ください。

## 🎯 使用例

```bash
# 日本語の動画を文字起こし
python3 transcribe_youtube.py "https://www.youtube.com/watch?v=9G5QsztlRH4" \
  --output output/japanese_video.md

# テキスト形式で出力
python3 transcribe_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID" \
  --format txt
```

## 📋 オプション

- `--output`: 出力ファイルのパス（デフォルト: `output/transcript.md`）
- `--format`: 出力形式（`md` または `txt`、デフォルト: `md`）

## 🔧 開発環境での使用

### エディタでの使い方

1. 好きなエディタ（Cursor、VS Code、PyCharmなど）でプロジェクトフォルダを開く
2. ターミナルで仮想環境をアクティベート: `source .venv/bin/activate`
3. 文字起こし実行: `python transcribe_youtube.py "YouTube URL"`
4. `output/` フォルダの結果をエディタで確認・編集

## 🤝 貢献

プルリクエストやイシューの報告を歓迎します！

## 📄 ライセンス

MIT License

