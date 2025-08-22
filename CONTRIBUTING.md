# 🤝 Contributing to YouTube Transcriber

YouTube Transcriber プロジェクトへの貢献を歓迎します！

## 🚀 開発環境のセットアップ

1. リポジトリをフォーク
2. ローカルにクローン
3. 仮想環境を作成
4. 依存関係をインストール

```bash
git clone https://github.com/your-username/youtube-transcriber.git
cd youtube-transcriber
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 📝 貢献の方法

### バグ報告

バグを発見した場合は、以下の情報を含めてIssueを作成してください：

- **OS**: macOS, Windows, Linux
- **Python バージョン**: `python --version`
- **エラーメッセージ**: 完全なスタックトレース
- **再現手順**: 問題を再現する具体的な手順
- **期待される動作**: 本来どうあるべきか

### 機能リクエスト

新機能の提案は以下の形式でお願いします：

- **概要**: 機能の簡潔な説明
- **動機**: なぜその機能が必要か
- **詳細**: 具体的な実装案や使用例
- **代替案**: 他に考えられる解決方法

### プルリクエスト

1. **Issue の確認**: まず関連する Issue が存在するか確認
2. **ブランチ作成**: `feature/feature-name` または `fix/bug-name`
3. **コード作成**: 機能追加やバグ修正
4. **テスト**: 変更が既存機能を破壊しないことを確認
5. **プルリクエスト作成**: 明確な説明と共に

## 🔧 コーディング規約

### Python スタイル

- **PEP 8** に従う
- **Type hints** を使用（Python 3.8+）
- **Docstrings** を関数とクラスに追加

### コミットメッセージ

```
type(scope): description

詳細な説明（必要に応じて）
```

**Type:**
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: コードスタイル
- `refactor`: リファクタリング
- `test`: テスト
- `chore`: その他

**例:**
```
feat(transcription): add support for auto-generated captions
fix(cli): handle invalid YouTube URLs gracefully
docs(readme): update installation instructions
```

## 🧪 テスト

テストを追加する場合は `tests/` ディレクトリに配置：

```bash
# テスト実行
python -m pytest tests/

# カバレッジ確認
python -m pytest --cov=. tests/
```

## 📚 ドキュメント

ドキュメントの更新も重要な貢献です：

- README.md の改善
- INSTALL.md の追加情報
- コード内のコメント
- 使用例の追加

## 🎯 優先度の高い貢献領域

現在、以下の分野での貢献を特に歓迎しています：

1. **エラーハンドリングの改善**
2. **多言語字幕の対応強化**
3. **出力フォーマットの追加**
4. **テストカバレッジの向上**
5. **パフォーマンスの最適化**

## ❓ 質問やサポート

- **Issue**: バグや機能リクエスト
- **Discussion**: 一般的な質問や議論

## 🙏 謝辞

すべての貢献者に感謝します！プロジェクトの改善に協力いただき、ありがとうございます。
