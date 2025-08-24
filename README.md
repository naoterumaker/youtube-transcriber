# 🎬 YouTube Transcriber

YouTube動画を簡単に文字起こしできるPythonツールです。

## ✨ 特徴

- 🚀 **簡単操作**: YouTube URLを入力するだけで文字起こし完了
- 📺 **チャンネル一括処理**: チャンネル名を指定して全動画の文字起こしを一括取得
- 📊 **詳細分析データ**: CSV・Excel形式でエンゲージメント指標を出力
- 🔄 **APIキーローテーション**: 複数のAPIキーを自動切り替えしてクォータ制限を回避
- 📁 **整理されたディレクトリ構造**: チャンネル別・日付別の階層構造で自動整理
- 📈 **ワークフロー対応**: プログレスバー・サマリーレポート自動生成
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

### 設定

#### 1. YouTube Data API v3 キーを取得

1. [Google Cloud Console](https://console.developers.google.com/) にアクセス
2. 新しいプロジェクトを作成（または既存のプロジェクトを選択）
3. **APIとサービス** → **ライブラリ** から「YouTube Data API v3」を検索
4. YouTube Data API v3 を**有効化**
5. **APIとサービス** → **認証情報** → **認証情報を作成** → **APIキー**
6. 作成されたAPIキーをコピー

#### 2. 環境変数ファイルを設定

```bash
# env.example をコピーして .env ファイルを作成
cp env.example .env
```

`.env` ファイルを編集してAPIキーを設定：
```bash
# YouTube Data API v3 Keys
# 複数のAPIキーを設定することでクォータ制限を回避できます
YOUTUBE_API_KEY_1=your_actual_api_key_1_here
YOUTUBE_API_KEY_2=your_actual_api_key_2_here
YOUTUBE_API_KEY_3=your_actual_api_key_3_here
YOUTUBE_API_KEY_4=your_actual_api_key_4_here
YOUTUBE_API_KEY_5=your_actual_api_key_5_here
```

**⚠️ 重要**: 
- `.env` ファイルは絶対に公開リポジトリにコミットしないでください
- 上記のAPIキーは例です。必ず自分のAPIキーに置き換えてください
- 複数のAPIキーを設定すると、クォータ制限時に自動的に次のキーに切り替わります

### 使い方

#### 単一動画の文字起こし
```bash
# 基本的な使い方（後方互換性）
python3 transcribe_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID"

# 新しいコマンド形式
python3 transcribe_youtube.py video "https://www.youtube.com/watch?v=VIDEO_ID"

# 出力ファイル名を指定
python3 transcribe_youtube.py video "https://www.youtube.com/watch?v=VIDEO_ID" \
  --output output/my_transcript.md --format md
```

#### チャンネル全動画の文字起こし＋分析
```bash
# チャンネル名を指定して全動画を処理（インタラクティブに期間選択）
python3 transcribe_youtube.py channel "チャンネル名"

# 期間を指定して処理
python3 transcribe_youtube.py channel "チャンネル名" --period 3months   # 直近3か月
python3 transcribe_youtube.py channel "チャンネル名" --period 6months   # 直近半年
python3 transcribe_youtube.py channel "チャンネル名" --period 1year     # 直近1年
python3 transcribe_youtube.py channel "チャンネル名" --period all       # 全期間

# 出力ディレクトリを指定
python3 transcribe_youtube.py channel "チャンネル名" \
  --output-dir output/my_channel --format md

# 処理する動画数を制限（期間フィルタと併用可能）
python3 transcribe_youtube.py channel "チャンネル名" \
  --period 6months --max-videos 50

# 文字起こしのみ（分析データなし）
python3 transcribe_youtube.py channel "チャンネル名" \
  --transcripts-only

# CSV/Excel生成をスキップ
python3 transcribe_youtube.py channel "チャンネル名" \
  --no-csv
```

## 📖 詳細な使い方

詳しいインストール手順や使い方については、[INSTALL.md](INSTALL.md) をご覧ください。

## 🎯 使用例

```bash
# 日本語の動画を文字起こし
python3 transcribe_youtube.py video "https://www.youtube.com/watch?v=9G5QsztlRH4" \
  --output output/japanese_video.md

# テキスト形式で出力
python3 transcribe_youtube.py video "https://www.youtube.com/watch?v=VIDEO_ID" \
  --format txt

# 人気YouTuberのチャンネル全動画を文字起こし＋分析（インタラクティブ期間選択）
python3 transcribe_youtube.py channel "HikakinTV" \
  --output-dir output/hikakin_analysis

# 直近半年の動画のみ処理（期間指定）
python3 transcribe_youtube.py channel "東海オンエア" \
  --period 6months --output-dir output/tokai_6months

# 直近3か月の最新50本のみ処理
python3 transcribe_youtube.py channel "中田敦彦のYouTube大学" \
  --period 3months --max-videos 50

# 全期間の動画を分析データのみ生成（文字起こしなし）
python3 transcribe_youtube.py channel "ビジネス系チャンネル" \
  --period all --transcripts-only
```

## 📋 オプション

### 単一動画（video コマンド）
- `--output`: 出力ファイルのパス（デフォルト: `output/transcript.md`）
- `--format`: 出力形式（`md` または `txt`、デフォルト: `md`）

### チャンネル（channel コマンド）
- `--output-dir`: 出力ディレクトリ（デフォルト: `output/channel_analysis`）
- `--format`: 文字起こしの出力形式（`md` または `txt`、デフォルト: `md`）
- `--period`: 取得期間（`3months`, `6months`, `1year`, `all`）※指定しない場合はインタラクティブ選択
- `--max-videos`: 処理する最大動画数（指定しない場合は期間に応じた推奨数を提案）
- `--no-csv`: CSV/Excel分析データの生成をスキップ
- `--transcripts-only`: 文字起こしのみ生成（分析データなし）

### 📅 期間選択機能
- **直近3か月**: 最大100本程度を推奨
- **直近半年**: 最大200本程度を推奨  
- **直近1年**: 最大500本程度を推奨
- **全期間**: 最大1000本程度を推奨（実用的な上限）

## 🔑 APIキー管理

- 複数のYouTube Data API v3キーを設定することで、クォータ制限を回避できます
- APIクォータに達すると自動的に次のキーに切り替わります
- 5つまでのAPIキーをサポート（`YOUTUBE_API_KEY_1` ～ `YOUTUBE_API_KEY_5`）

## 📊 出力データ構造

### チャンネル分析時の出力構造
```
output/channel_analysis/
└── チャンネル名_20240101_123456/
    ├── transcripts/              # 文字起こしファイル
    │   ├── 動画タイトル1_VIDEO_ID1.md
    │   ├── 動画タイトル2_VIDEO_ID2.md
    │   └── ...
    ├── data/                     # 分析データ
    │   ├── チャンネル名_analysis.csv
    │   └── チャンネル名_analysis.xlsx
    └── summary_report.md         # サマリーレポート
```

### CSV分析データの項目
Google Apps Scriptと同じ項目を出力：

| 項目 | 説明 |
|------|------|
| チェック | 空欄（手動チェック用） |
| タイトル | 動画タイトル |
| 動画リンク | YouTube動画URL |
| サムネイル画像 | サムネイル画像URL |
| チャンネル名 | チャンネル名 |
| 投稿日 | 動画投稿日（YYYY/MM/DD形式） |
| 視聴回数 | 動画の視聴回数 |
| 高評価数 | 高評価数 |
| コメント数 | コメント数 |
| 動画時間 | 動画時間（HH:MM:SS形式） |
| チャンネル登録者数 | チャンネル登録者数 |
| 拡散率 | 視聴回数 ÷ チャンネル登録者数 × 100 |
| 視聴コメント率 | コメント数 ÷ 視聴回数 × 100 |
| 視聴高評価率 | 高評価数 ÷ 視聴回数 × 100 |
| 視聴エンゲージメント率 | (高評価数 + コメント数) ÷ 視聴回数 × 100 |

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

