# Enhanced File Merger

コードファイルを1つのファイルにマージするPythonスクリプトです。ソースコードの保存、共有、レビュー、またはAIによる解析のために使用できます。

## 特徴

- 💻 **柔軟な設定**: YAMLベースの設定ファイルでカスタマイズ可能
- 🌏 **マルチエンコーディング対応**: UTF-8, Shift-JIS, EUC-JPなど複数のエンコーディングをサポート
- 📝 **メタデータ付き出力**: ファイル情報やタイムスタンプを含む
- 🔍 **行番号表示**: オプションで行番号を追加可能
- ⚡ **カスタマイズ可能な除外パターン**: 不要なファイルを柔軟に除外
- 📊 **詳細なサマリー**: 処理結果の統計情報を表示

## インストール方法

### pipxを使用したインストール（推奨）

1. pipxをインストール:
```bash
# Pythonがインストールされていない場合は先にインストールしてください
python -m pip install --user pipx
python -m pipx ensurepath
```

2. このリポジトリをクローン:
```bash
git clone https://github.com/yourusername/enhanced-file-merger.git
cd enhanced-file-merger
```

3. enhanced-file-mergerをインストール:
```bash
pipx install .
```

4. 除外リストをホームディレクトリにコピー
```bash
cp .enhanced-file-merger-config.yaml.example ~/.enhanced-file-merger-config.yaml
```

インストール後は `merge-files` コマンドがグローバルで使用可能になります。

### アンインストール方法

pipxでインストールした場合は以下のコマンドでアンインストールできます：

```bash
pipx uninstall enhanced-file-merger
```

## 基本的な使い方

最もシンプルな使用方法:
```bash
merge-files ソースディレクトリ 出力ファイル名
```

例:
```bash
merge-files ./src output.txt
```

## 高度な使用方法

### カスタム設定ファイルの使用

カスタム設定ファイルの使用
```bash
merge-files ./src output.txt --config my_custom_config.yaml
```

### 追加の除外パターンを指定

```bash
merge-files ./src output.txt --exclude "*.log" --exclude "temp*"
```

### エンコーディングを指定

```bash
merge-files ./src output.txt --encoding shift-jis
```

### その他のオプション

```bash
# サマリー無しで実行
merge-files ./src output.txt --no-summary

# エラーのみ表示（サイレントモード）
merge-files ./src output.txt --silent
```

## 設定ファイル

設定ファイルは以下の項目をカスタマイズできます：

```yaml
output_format:
  add_line_numbers: true    # 行番号を表示
  show_file_count: true     # ファイル数を表示
  show_summary: true        # サマリーを表示
  separator_line: "="       # 区切り文字
  separator_length: 80      # 区切り線の長さ

exclude_patterns:
  directories:              # 除外するディレクトリ
    - node_modules
    - __pycache__
    - .git
  
  files:                    # 除外するファイル
    - "*.json"
    - "*.pyc"
    - "*.exe"
    
  system_files:             # 除外するシステムファイル
    - ".DS_Store"
    - "Thumbs.db"

encoding:
  default: "utf-8"          # デフォルトエンコーディング
  fallback:                 # フォールバックエンコーディング
    - "cp932"
    - "shift-jis"
    - "euc-jp"

output:
  add_timestamp: true       # タイムスタンプを追加
  timestamp_format: "%Y-%m-%d %H:%M:%S"
  line_ending: "auto"       # 改行コード（auto/lf/crlf）
```

## 出力例

```text
MERGED SOURCE CODE FILES
================================================================================
Project Directory: /absolute/path/to/src
Merge Started: 2025-01-09 10:00:00
================================================================================

### FILE: lib/utils.py
================================================================================
METADATA:
  Modified: 2025-01-09 10:00:00
  Size: 1234 bytes
  Full path: /absolute/path/to/src/lib/utils.py
================================================================================

   1 | def hello():
   2 |     print("Hello, World!")
   3 | 
   4 | if __name__ == "__main__":
   5 |     hello()

--------------------------------------------------------------------------------
```

## テストの実行

開発者は `poetry` を使用してユニットテストを実行できます。

```bash
poetry install
poetry run pytest
```

## 注意事項

1. **大きなファイル**: メモリ使用量に注意してください
2. **エンコーディング**: 自動検出は完璧ではありません
3. **除外パターン**: 意図しないファイルが含まれていないか確認してください

## トラブルシューティング

### よくある問題と解決方法

1. **UnicodeDecodeError が発生する場合**
   - `--encoding` オプションで適切なエンコーディングを指定してください
   - .enhanced-file-merger-config.yamlのfallbackエンコーディングを確認してください

2. **意図しないファイルが含まれる場合**
   - .enhanced-file-merger-config.yamlの除外パターンを確認してください
   - `--exclude` オプションで追加の除外パターンを指定してください

3. **メモリ不足になる場合**
   - 処理するディレクトリを分割してください
   - 不要なファイルを除外パターンに追加してください

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください

## コントリビューション

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

## 謝辞

- このプロジェクトは多くのオープンソースソフトウェアに支えられています
- コントリビュータの皆様に感謝いたします
