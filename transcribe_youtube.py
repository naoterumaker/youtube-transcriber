#!/usr/bin/env python3
import re
import os
import csv
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import time
from pathlib import Path

import click
import pandas as pd
from tqdm import tqdm
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global variables for API key rotation
_current_api_key_index = 0
_api_keys = []


def parse_duration(duration: str) -> int:
    """ISO 8601 duration (PT1H2M3S) を秒数に変換"""
    if not duration:
        return 0
    
    # PT1H2M3S のような形式をパース
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)
    
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds


def format_duration(seconds: int) -> str:
    """秒数を HH:MM:SS 形式に変換"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def calculate_engagement_metrics(video_stats: Dict, subscriber_count: int) -> Dict[str, float]:
    """エンゲージメント指標を計算"""
    view_count = int(video_stats.get('viewCount', 0))
    like_count = int(video_stats.get('likeCount', 0))
    comment_count = int(video_stats.get('commentCount', 0))
    
    # 拡散率 (視聴回数 / チャンネル登録者数)
    spread_rate = (view_count / subscriber_count * 100) if subscriber_count > 0 else 0
    
    # 視聴コメント率 (コメント数 / 視聴回数 * 100)
    comment_rate = (comment_count / view_count * 100) if view_count > 0 else 0
    
    # 視聴高評価率 (高評価数 / 視聴回数 * 100)
    like_rate = (like_count / view_count * 100) if view_count > 0 else 0
    
    # 視聴エンゲージメント率 ((高評価数 + コメント数) / 視聴回数 * 100)
    engagement_rate = ((like_count + comment_count) / view_count * 100) if view_count > 0 else 0
    
    return {
        'spread_rate': round(spread_rate, 4),
        'comment_rate': round(comment_rate, 4),
        'like_rate': round(like_rate, 4),
        'engagement_rate': round(engagement_rate, 4)
    }


def get_date_range_from_period(period: str) -> tuple[Optional[datetime], Optional[datetime]]:
    """期間文字列から日付範囲を取得"""
    now = datetime.now()
    
    if period == "3months":
        start_date = now - timedelta(days=90)
        return start_date, now
    elif period == "6months":
        start_date = now - timedelta(days=180)
        return start_date, now
    elif period == "1year":
        start_date = now - timedelta(days=365)
        return start_date, now
    elif period == "all":
        return None, None  # 全期間
    else:
        return None, None


def get_recommended_video_count(period: str, total_videos: int) -> Optional[int]:
    """期間に応じた推奨動画数を取得"""
    if period == "3months":
        # 3か月なら最大100本程度が適切
        return min(100, total_videos)
    elif period == "6months":
        # 半年なら最大200本程度
        return min(200, total_videos)
    elif period == "1year":
        # 1年なら最大500本程度
        return min(500, total_videos)
    elif period == "all":
        # 全期間の場合は制限なし（ただし実用的な上限を設定）
        return min(1000, total_videos)
    else:
        return None


def prompt_period_selection() -> str:
    """ユーザーに期間選択を促す"""
    click.echo("\n📅 取得期間を選択してください:")
    click.echo("1️⃣  直近3か月")
    click.echo("2️⃣  直近半年")
    click.echo("3️⃣  直近1年")
    click.echo("4️⃣  全期間")
    
    while True:
        choice = click.prompt("\n選択してください (1-4)", type=str).strip()
        
        if choice == "1":
            return "3months"
        elif choice == "2":
            return "6months"
        elif choice == "3":
            return "1year"
        elif choice == "4":
            return "all"
        else:
            click.echo("❌ 無効な選択です。1-4の数字を入力してください。")


def create_output_directory(base_dir: str, channel_name: str) -> Path:
    """チャンネル用の出力ディレクトリを作成"""
    # 安全なディレクトリ名を作成
    safe_channel_name = re.sub(r'[<>:"/\\|?*]', '_', channel_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    output_path = Path(base_dir) / f"{safe_channel_name}_{timestamp}"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # サブディレクトリを作成
    (output_path / "transcripts").mkdir(exist_ok=True)
    (output_path / "data").mkdir(exist_ok=True)
    
    return output_path


def extract_video_id(url_or_id: str) -> Optional[str]:
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([^#&?]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for pattern in patterns:
        m = re.search(pattern, url_or_id)
        if m:
            return m.group(1)
    return None


def load_api_keys():
    """環境変数から複数のAPIキーを読み込む"""
    global _api_keys
    if _api_keys:  # 既に読み込み済みの場合はそのまま返す
        return _api_keys
    
    # 複数のAPIキーを読み込み
    keys = []
    for i in range(1, 6):  # KEY_1 から KEY_5 まで
        key = os.getenv(f'YOUTUBE_API_KEY_{i}')
        if key and key.strip():
            keys.append(key.strip())
    
    # 複数キーが見つからない場合は単一キーを確認
    if not keys:
        single_key = os.getenv('YOUTUBE_API_KEY')
        if single_key and single_key.strip():
            keys.append(single_key.strip())
    
    if not keys:
        raise ValueError(
            "No YouTube API keys found. Please set YOUTUBE_API_KEY_1, YOUTUBE_API_KEY_2, etc. "
            "or YOUTUBE_API_KEY in your .env file."
        )
    
    _api_keys = keys
    click.echo(f"Loaded {len(_api_keys)} API key(s)")
    return _api_keys


def get_current_api_key():
    """現在のAPIキーを取得（ローテーション対応）"""
    global _current_api_key_index
    keys = load_api_keys()
    
    if _current_api_key_index >= len(keys):
        _current_api_key_index = 0
    
    return keys[_current_api_key_index]


def rotate_api_key():
    """次のAPIキーに切り替え"""
    global _current_api_key_index
    keys = load_api_keys()
    _current_api_key_index = (_current_api_key_index + 1) % len(keys)
    click.echo(f"Switched to API key {_current_api_key_index + 1}/{len(keys)}")


def get_youtube_service():
    """YouTube Data API v3 service を取得"""
    api_key = get_current_api_key()
    return build('youtube', 'v3', developerKey=api_key)


def handle_api_error(error, operation_name: str):
    """APIエラーを処理し、必要に応じてキーをローテーション"""
    error_str = str(error).lower()
    
    if 'quota' in error_str or '403' in error_str or 'exceeded' in error_str:
        click.echo(f"API quota exceeded during {operation_name}. Trying next API key...")
        rotate_api_key()
        return True  # リトライ可能
    else:
        click.echo(f"Error during {operation_name}: {error}", err=True)
        return False  # リトライ不可能


def get_channel_id_from_name(channel_name: str) -> Optional[str]:
    """チャンネル名からチャンネルIDを取得"""
    max_retries = len(load_api_keys())
    
    for attempt in range(max_retries):
        try:
            youtube = get_youtube_service()
            
            # チャンネル検索
            search_response = youtube.search().list(
                q=channel_name,
                type='channel',
                part='id',
                maxResults=1
            ).execute()
            
            if search_response['items']:
                return search_response['items'][0]['id']['channelId']
            return None
            
        except Exception as e:
            if handle_api_error(e, "channel search"):
                continue  # 次のAPIキーでリトライ
            else:
                return None
    
    click.echo("All API keys exhausted for channel search", err=True)
    return None


def get_channel_videos(channel_id: str, max_results: Optional[int] = None, 
                      start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[str]:
    """チャンネルの全動画IDを取得（ページネーション対応）"""
    video_ids = []
    next_page_token = None
    max_retries = len(load_api_keys())
    
    while True:
        success = False
        
        for attempt in range(max_retries):
            try:
                youtube = get_youtube_service()
                
                # 検索パラメータを構築
                search_params = {
                    'channelId': channel_id,
                    'type': 'video',
                    'part': 'id',
                    'maxResults': 50,  # API制限内での最大値
                    'order': 'date'
                }
                
                # 日付フィルタを追加
                if start_date:
                    search_params['publishedAfter'] = start_date.isoformat() + 'Z'
                if end_date:
                    search_params['publishedBefore'] = end_date.isoformat() + 'Z'
                if next_page_token:
                    search_params['pageToken'] = next_page_token
                
                # チャンネルの動画を検索
                search_response = youtube.search().list(**search_params).execute()
                
                # 動画IDを収集
                for item in search_response['items']:
                    video_ids.append(item['id']['videoId'])
                    if max_results and len(video_ids) >= max_results:
                        return video_ids[:max_results]
                
                # 次のページがあるかチェック
                next_page_token = search_response.get('nextPageToken')
                success = True
                break
                
            except Exception as e:
                if handle_api_error(e, "video list fetch"):
                    continue  # 次のAPIキーでリトライ
                else:
                    return video_ids  # エラーで終了、これまでの結果を返す
        
        if not success:
            click.echo("All API keys exhausted for video list fetch", err=True)
            break
            
        if not next_page_token:
            break
            
        # API制限を考慮して少し待機
        time.sleep(0.1)
    
    return video_ids


def get_video_info(video_id: str) -> Dict[str, Any]:
    """動画の詳細情報を取得"""
    max_retries = len(load_api_keys())
    
    for attempt in range(max_retries):
        try:
            youtube = get_youtube_service()
            
            video_response = youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()
            
            if video_response['items']:
                return video_response['items'][0]
            return {}
            
        except Exception as e:
            if handle_api_error(e, f"video info fetch for {video_id}"):
                continue  # 次のAPIキーでリトライ
            else:
                return {}
    
    click.echo(f"All API keys exhausted for video info fetch: {video_id}", err=True)
    return {}


def fetch_transcript(video_id: str) -> str:
    api = YouTubeTranscriptApi()
    preferred_languages = ["ja", "ja-JP", "en", "en-US"]
    last_error: Optional[Exception] = None
    for lang in preferred_languages:
        try:
            chunks = api.fetch(video_id, languages=[lang])
            return " ".join([c.text for c in chunks])
        except Exception as e:  # noqa: BLE001
            last_error = e
            continue
    try:
        chunks = api.fetch(video_id)
        return " ".join([c.text for c in chunks])
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"Could not fetch transcript: {e or last_error}")


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def fetch_channel_transcripts(channel_name: str, output_dir: str, max_videos: Optional[int] = None, 
                             fmt: str = "md", include_csv: bool = True, period: Optional[str] = None) -> None:
    """チャンネルの全動画の文字起こしとCSVデータを取得"""
    click.echo(f"🔍 Searching for channel: {channel_name}")
    
    # チャンネルIDを取得
    channel_id = get_channel_id_from_name(channel_name)
    if not channel_id:
        raise click.ClickException(f"Channel not found: {channel_name}")
    
    click.echo(f"✅ Found channel ID: {channel_id}")
    
    # チャンネル情報を取得
    channel_info = get_channel_info(channel_id)
    if not channel_info:
        raise click.ClickException(f"Failed to get channel information")
    
    channel_title = channel_info['snippet']['title']
    subscriber_count = int(channel_info['statistics'].get('subscriberCount', 0))
    
    click.echo(f"📺 Channel: {channel_title}")
    click.echo(f"👥 Subscribers: {subscriber_count:,}")
    
    # 期間選択（インタラクティブモード）
    if period is None:
        period = prompt_period_selection()
    
    # 日付範囲を取得
    start_date, end_date = get_date_range_from_period(period)
    
    # 期間情報を表示
    if period == "3months":
        click.echo("📅 取得期間: 直近3か月")
    elif period == "6months":
        click.echo("📅 取得期間: 直近半年")
    elif period == "1year":
        click.echo("📅 取得期間: 直近1年")
    elif period == "all":
        click.echo("📅 取得期間: 全期間")
    
    # 動画IDリストを取得
    click.echo("📋 Fetching video list...")
    video_ids = get_channel_videos(channel_id, max_videos, start_date, end_date)
    
    if not video_ids:
        click.echo("❌ No videos found in this channel.")
        return
    
    click.echo(f"📹 Found {len(video_ids)} videos")
    
    # 推奨動画数の表示と適用
    if max_videos is None:
        recommended_count = get_recommended_video_count(period, len(video_ids))
        if recommended_count and recommended_count < len(video_ids):
            click.echo(f"💡 推奨処理数: {recommended_count}本 (期間: {period})")
            if click.confirm(f"推奨数 {recommended_count}本で処理しますか？", default=True):
                video_ids = video_ids[:recommended_count]
                click.echo(f"📹 Processing {len(video_ids)} videos (recommended limit applied)")
            else:
                click.echo(f"📹 Processing all {len(video_ids)} videos")
        else:
            click.echo(f"📹 Processing all {len(video_ids)} videos")
    else:
        video_ids = video_ids[:max_videos]
        click.echo(f"📹 Processing {len(video_ids)} videos (user limit applied)")
    
    # 出力ディレクトリを作成
    output_path = create_output_directory(output_dir, channel_name)
    click.echo(f"📁 Output directory: {output_path}")
    
    # CSVデータ用のリスト
    csv_data = []
    csv_headers = [
        'チェック', 'タイトル', '動画リンク', 'サムネイル画像', 'チャンネル名', 
        '投稿日', '視聴回数', '高評価数', 'コメント数', '動画時間', 
        'チャンネル登録者数', '拡散率', '視聴コメント率', '視聴高評価率', '視聴エンゲージメント率'
    ]
    
    successful_transcripts = 0
    failed_transcripts = 0
    
    # プログレスバーで各動画を処理
    with tqdm(total=len(video_ids), desc="Processing videos") as pbar:
        for i, video_id in enumerate(video_ids, 1):
            try:
                pbar.set_description(f"Processing video {i}/{len(video_ids)}")
                
                # 動画情報を取得
                video_info = get_video_info(video_id)
                if not video_info or 'snippet' not in video_info:
                    pbar.write(f"⚠️  Skipping {video_id}: No video info available")
                    failed_transcripts += 1
                    pbar.update(1)
                    continue
                
                snippet = video_info['snippet']
                statistics = video_info.get('statistics', {})
                content_details = video_info.get('contentDetails', {})
                
                video_title = snippet.get('title', 'Unknown')
                published_at = snippet.get('publishedAt', '')
                
                # 統計情報を取得
                view_count = int(statistics.get('viewCount', 0))
                like_count = int(statistics.get('likeCount', 0))
                comment_count = int(statistics.get('commentCount', 0))
                
                # 動画時間を取得・変換
                duration_iso = content_details.get('duration', 'PT0S')
                duration_seconds = parse_duration(duration_iso)
                duration_formatted = format_duration(duration_seconds)
                
                # エンゲージメント指標を計算
                metrics = calculate_engagement_metrics(statistics, subscriber_count)
                
                # CSVデータを追加
                csv_row = [
                    '',  # チェック（空欄）
                    video_title,
                    f"https://www.youtube.com/watch?v={video_id}",
                    f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                    channel_title,
                    datetime.fromisoformat(published_at.replace('Z', '+00:00')).strftime('%Y/%m/%d') if published_at else '',
                    view_count,
                    like_count,
                    comment_count,
                    duration_formatted,
                    subscriber_count,
                    metrics['spread_rate'],
                    metrics['comment_rate'],
                    metrics['like_rate'],
                    metrics['engagement_rate']
                ]
                csv_data.append(csv_row)
                
                # 文字起こしを取得
                try:
                    transcript_text = fetch_transcript(video_id)
                    
                    # ファイル名を生成（安全な文字のみ使用）
                    safe_title = re.sub(r'[<>:"/\\|?*]', '_', video_title)[:50]
                    extension = "md" if fmt == "md" else "txt"
                    filename = f"{safe_title}_{video_id}.{extension}"
                    transcript_path = output_path / "transcripts" / filename
                    
                    # 出力フォーマット
                    url = f"https://www.youtube.com/watch?v={video_id}"
                    formatted_content = format_output(transcript_text, url, fmt, video_title)
                    
                    # ファイルに保存
                    with open(transcript_path, "w", encoding="utf-8") as f:
                        f.write(formatted_content)
                    
                    successful_transcripts += 1
                    pbar.write(f"✅ Saved transcript: {filename}")
                    
                except Exception as transcript_error:
                    pbar.write(f"⚠️  Failed to get transcript for {video_id}: {transcript_error}")
                    # CSVデータは保持（文字起こしが失敗してもデータは有効）
                
                # API制限を考慮して少し待機
                time.sleep(0.3)
                
            except Exception as e:
                pbar.write(f"❌ Failed to process {video_id}: {e}")
                failed_transcripts += 1
            
            pbar.update(1)
    
    # CSVファイルを保存
    if include_csv and csv_data:
        csv_path = output_path / "data" / f"{channel_title}_analysis.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(csv_headers)
            writer.writerows(csv_data)
        
        click.echo(f"📊 CSV saved: {csv_path}")
        
        # Excelファイルも生成
        try:
            excel_path = output_path / "data" / f"{channel_title}_analysis.xlsx"
            df = pd.DataFrame(csv_data, columns=csv_headers)
            df.to_excel(excel_path, index=False, engine='openpyxl')
            click.echo(f"📈 Excel saved: {excel_path}")
        except ImportError:
            click.echo("⚠️  openpyxl not installed. Excel file not generated.")
    
    # サマリーレポートを生成
    generate_summary_report(output_path, channel_title, len(video_ids), successful_transcripts, failed_transcripts, csv_data)
    
    click.echo(f"\n🎉 Completed!")
    click.echo(f"📊 Total videos: {len(video_ids)}")
    click.echo(f"✅ Successful transcripts: {successful_transcripts}")
    click.echo(f"❌ Failed transcripts: {failed_transcripts}")
    click.echo(f"📁 Output directory: {output_path}")


def get_channel_info(channel_id: str) -> Optional[Dict[str, Any]]:
    """チャンネルの詳細情報を取得"""
    max_retries = len(load_api_keys())
    
    for attempt in range(max_retries):
        try:
            youtube = get_youtube_service()
            
            channel_response = youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            ).execute()
            
            if channel_response['items']:
                return channel_response['items'][0]
            return None
            
        except Exception as e:
            if handle_api_error(e, f"channel info fetch for {channel_id}"):
                continue
            else:
                return None
    
    click.echo(f"All API keys exhausted for channel info fetch: {channel_id}", err=True)
    return None


def generate_summary_report(output_path: Path, channel_name: str, total_videos: int, 
                          successful: int, failed: int, csv_data: List) -> None:
    """サマリーレポートを生成"""
    report_path = output_path / "summary_report.md"
    
    # 基本統計を計算
    if csv_data:
        df = pd.DataFrame(csv_data[1:], columns=csv_data[0] if csv_data else [])  # ヘッダーを除く
        
        try:
            # 数値列を変換
            numeric_cols = ['視聴回数', '高評価数', 'コメント数', '拡散率', '視聴コメント率', '視聴高評価率', '視聴エンゲージメント率']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            avg_views = df['視聴回数'].mean() if '視聴回数' in df.columns else 0
            avg_likes = df['高評価数'].mean() if '高評価数' in df.columns else 0
            avg_comments = df['コメント数'].mean() if 'コメント数' in df.columns else 0
            avg_engagement = df['視聴エンゲージメント率'].mean() if '視聴エンゲージメント率' in df.columns else 0
            
        except Exception:
            avg_views = avg_likes = avg_comments = avg_engagement = 0
    else:
        avg_views = avg_likes = avg_comments = avg_engagement = 0
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report_content = f"""# YouTube Channel Analysis Report

## 📊 Channel Information
- **Channel Name:** {channel_name}
- **Analysis Date:** {timestamp}
- **Total Videos Found:** {total_videos}

## 🎯 Processing Results
- ✅ **Successful Transcripts:** {successful}
- ❌ **Failed Transcripts:** {failed}
- 📈 **Success Rate:** {(successful/total_videos*100):.1f}%

## 📈 Channel Statistics
- 👀 **Average Views:** {avg_views:,.0f}
- 👍 **Average Likes:** {avg_likes:,.0f}
- 💬 **Average Comments:** {avg_comments:,.0f}
- 🔥 **Average Engagement Rate:** {avg_engagement:.2f}%

## 📁 Output Structure
```
{output_path.name}/
├── transcripts/          # 文字起こしファイル
├── data/                 # CSV・Excelデータ
│   ├── {channel_name}_analysis.csv
│   └── {channel_name}_analysis.xlsx
└── summary_report.md     # このレポート
```

## 🔧 Generated Files
- **Transcript Files:** {successful} files in `transcripts/` directory
- **CSV Data:** `data/{channel_name}_analysis.csv`
- **Excel Data:** `data/{channel_name}_analysis.xlsx`
- **Summary Report:** `summary_report.md`

---
Generated by YouTube Transcriber
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    click.echo(f"📋 Summary report saved: {report_path}")


def format_output(text: str, url: str, fmt: str, title: str = None) -> str:
    if fmt == "txt":
        return text
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    title_section = ""
    if title:
        title_section = f"**Title:** {title}\n\n"
    
    return (
        f"# YouTube Transcript\n\n"
        f"{title_section}"
        f"**URL:** {url}\n\n"
        f"**Generated:** {ts}\n\n"
        f"---\n\n{text}\n"
    )


@click.group()
def cli():
    """YouTube Transcriber - 動画やチャンネルの文字起こしツール"""
    pass


@cli.command()
@click.argument("url")
@click.option("--output", "output_path", default="output/transcript.md", help="Output file path")
@click.option("--format", "fmt", type=click.Choice(["md", "txt"]), default="md", help="Output format")
def video(url: str, output_path: str, fmt: str) -> None:
    """単一の動画を文字起こし"""
    video_id = extract_video_id(url)
    if not video_id:
        raise click.ClickException("Invalid YouTube URL or ID")

    text = fetch_transcript(video_id)
    ensure_parent_dir(output_path)
    body = format_output(text, url, fmt)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(body)
    click.echo(f"Saved transcript to {output_path}")


@cli.command()
@click.argument("channel_name")
@click.option("--output-dir", default="output/channel_analysis", help="Output directory for channel analysis")
@click.option("--format", "fmt", type=click.Choice(["md", "txt"]), default="md", help="Output format for transcripts")
@click.option("--max-videos", type=int, help="Maximum number of videos to process")
@click.option("--period", type=click.Choice(["3months", "6months", "1year", "all"]), help="Time period to fetch videos from")
@click.option("--no-csv", is_flag=True, help="Skip CSV/Excel generation")
@click.option("--transcripts-only", is_flag=True, help="Generate transcripts only (no analysis data)")
def channel(channel_name: str, output_dir: str, fmt: str, max_videos: Optional[int], 
           period: Optional[str], no_csv: bool, transcripts_only: bool) -> None:
    """チャンネルの全動画を文字起こし＋分析データ生成"""
    try:
        include_csv = not no_csv and not transcripts_only
        fetch_channel_transcripts(channel_name, output_dir, max_videos, fmt, include_csv, period)
    except Exception as e:
        raise click.ClickException(str(e))


# 後方互換性のために、引数なしで実行された場合は単一動画モードとして動作
@click.command()
@click.argument("url")
@click.option("--output", "output_path", default="output/transcript.md", help="Output file path")
@click.option("--format", "fmt", type=click.Choice(["md", "txt"]), default="md", help="Output format")
def main(url: str, output_path: str, fmt: str) -> None:
    """単一の動画を文字起こし（後方互換性）"""
    video_id = extract_video_id(url)
    if not video_id:
        raise click.ClickException("Invalid YouTube URL or ID")

    text = fetch_transcript(video_id)
    ensure_parent_dir(output_path)
    body = format_output(text, url, fmt)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(body)
    click.echo(f"Saved transcript to {output_path}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ['video', 'channel']:
        cli()
    else:
        main()


