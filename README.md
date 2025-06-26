# 対話型 夕食献立提案 AI エージェント (Dinner Suggestion AI Agent)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 💡 概要

「今晩の献立、決まらない…」

そんな悩みを、AI との対話を通じて解決する Web アプリケーションです。
ユーザー（奥様）の状況に合わせて、AI が「旦那様の好み」「冷蔵庫の中身」「使える調理器具」などを優しくヒアリング。あなたとご家庭に最適な献立を提案します。
このプロジェクトは、FastAPI と LangChain を使用して構築されており、Google Gemini をバックエンドの AI エンジンとして利用しています。

## 🚀 主な機能

- AI との対話形式による献立提案
- ユーザーの状況に合わせた質問（気分、食材、調理器具）
- 選択肢と自由入力に対応した柔軟な UI
- 主菜・副菜・汁物を組み合わせた献立セットの提案

## 🛠️ 技術スタック

このプロジェクトは、以下の技術を使用して構築されています。

- **フロントエンド**:
  ![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
  ![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
  ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
- **バックエンド**:
  ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
  ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
- **AI / LLM**:
  ![Google Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)
  ![LangChain](https://img.shields.io/badge/LangChain-FFFFFF?style=for-the-badge&logo=langchain&logoColor=black)

## ⚙️ 導入方法

このアプリケーションをあなたのローカル環境で動かすための手順です。

### 前提条件

- [Python](https://www.python.org/) (バージョン 3.10 以上)
- [Git](https://git-scm.com/)

### 1. リポジトリのクローン

まず、このリポジトリをクローンします。

```bash
git clone [https://github.com/](https://github.com/)[あなたのユーザー名]/[あなたのリポジトリ名].git
cd [あなたのリポジトリ名]
```

### 2. バックエンドのセットアップ

次に、バックエンドサーバーの環境を構築します。

1.  **`backend`ディレクトリに移動**

    ```bash
    cd backend
    ```

2.  **Python の仮想環境を作成し、有効化する**

    - Mac / Linux:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```
    - Windows:
      ```bash
      python -m venv venv
      venv\Scripts\activate
      ```

3.  **必要なライブラリをインストールする**
    (このプロジェクトには`requirements.txt`が必要です。もしリポジトリになければ、仮想環境を有効化した後、以下のコマンドで作成してください)

    ```bash
    # (初回のみ) requirements.txt を作成する場合
    pip freeze > requirements.txt

    # 依存ライブラリをインストール
    pip install -r requirements.txt
    ```

4.  **.env ファイルの作成と API キーの設定**
    `backend`ディレクトリ直下に `.env` という名前のファイルを新規作成し、以下の内容を記述します。

    ```.env
    GOOGLE_API_KEY="ここにあなたのGoogle AI (Gemini) APIキーを貼り付け"
    ```

    - API キーは[Google AI for Developers](https://ai.google.dev/)から取得してください。
    - **重要**: キーを`"`（ダブルクォーテーション）で囲まないでください。

### 3. フロントエンドのセットアップ

特別なビルドプロセスは不要です。`frontend`ディレクトリ内のファイルをそのまま使用します。

## ▶️ 実行方法

1.  **バックエンドサーバーを起動する**
    ターミナルで`backend`ディレクトリにいることを確認し（仮想環境が有効な状態で）、以下のコマンドを実行します。

    ```bash
    uvicorn main:app --reload
    ```

    サーバーが `http://127.0.0.1:8000` で起動します。

2.  **フロントエンドにアクセスする**
    お使いのウェブブラウザで、`frontend`ディレクトリにある`index.html`ファイルを開きます。
    - ファイルを直接ダブルクリックするか、エディタから「ブラウザで開く」などの機能を使用してください。

これで、ブラウザ上に AI とのチャット画面が表示され、会話を始めることができます。

## 📝 今後の展望 (ToDo)

- [ ] ユーザー認証機能の追加
- [ ] 過去の提案履歴の保存と表示
- [ ] レシピの画像表示
- [ ] より高度な AI のパーソナリティ設定
- [ ] Docker による環境構築の簡略化

## 📄 ライセンス

このプロジェクトは [MIT License](LICENSE) の下で公開されています。

## 🙏 謝辞

このプロジェクトの開発を通じて、対話型 AI の可能性と、それを支える技術の奥深さを学ぶことができました。
