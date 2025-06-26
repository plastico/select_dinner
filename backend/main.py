# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder

from schemas import ChatRequest, AIResponse
from chain import invoke_chain

app = FastAPI(
    title="夕食提案AIエージェント API",
    description="LangChainとFastAPIで構築された、対話型の献立提案AI",
    version="1.0.0",
)

# CORS (Cross-Origin Resource Sharing) の設定
# フロントエンドからのリクエストを許可する
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のオリジンに制限してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", summary="サーバーの動作確認用")
async def read_root():
    return {"status": "ok", "message": "Welcome to Dinner Suggestion AI Agent!"}

@app.post("/chat", summary="AIと対話し、応答を取得する")
async def chat(request: ChatRequest):
    """
    ユーザーからのメッセージと会話履歴を受け取り、AIからの次の応答を返す。
    """
    try:
        response_pydantic: AIResponse = await invoke_chain(request.message, request.history)
        
        # 修正箇所: 応答の中身を見て、フロントに返すものを決める
        if response_pydantic.question:
            return jsonable_encoder(response_pydantic.question)
        elif response_pydantic.suggestion:
            return jsonable_encoder(response_pydantic.suggestion)
        else:
            # 念の為のエラーハンドリング
            raise ValueError("AI response is empty.")

    except Exception as e:
        print(f"Error during chain invocation: {e}")
        # エラーが発生した場合もフロントエンドが処理できる形式で返す
        return jsonable_encoder({
            "type": "question",
            "message": f"申し訳ありません、エラーが発生しました。もう一度お試しください。(詳細: {e})",
            "options": ["もう一度試す"]
        })

@app.get("/start", summary="最初の質問を取得する")
async def start_conversation():
    """
    会話の開始時に、AIからの最初の質問を生成する。
    """
    try:
        response_pydantic: AIResponse = await invoke_chain("こんにちは、献立の相談をお願いします。", [])
        
        # 修正箇所: 応答の中身を見て、フロントに返すものを決める
        if response_pydantic.question:
            return jsonable_encoder(response_pydantic.question)
        else:
            # 最初の応答は必ず質問のはずだが、念の為エラーハンドリング
            raise ValueError("Initial response is not a question.")
            
    except Exception as e:
        print(f"Error during start conversation: {e}")
        return jsonable_encoder({
            "type": "question",
            "message": f"エージェントの起動に失敗しました。(詳細: {e})",
            "options": []
        })

# サーバーを起動するためのコマンド (開発用)
# ターミナルで `uvicorn main:app --reload` を実行