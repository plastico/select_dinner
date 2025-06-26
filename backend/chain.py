# backend/chain.py
import os
import json
import re # ★★★ 正規表現ライブラリをインポート ★★★
from dotenv import load_dotenv
from typing import List 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers.pydantic import PydanticOutputParser

from schemas import AIResponse, Question, Suggestion, ChatMessage
from prompts import SYSTEM_PROMPT


# .envからAPIキーを読み込み
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY is not set in .env file")

# 1. 出力パーサーの準備
# Pydanticモデル(AIResponse)に基づいて、LLMの出力を解析する方法を定義
parser = PydanticOutputParser(pydantic_object=AIResponse)

# 2. LLMの準備
# temperatureを少し高めにして創造的な回答を促す
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)

# 3. プロンプトテンプレートの準備
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    # ★★★ ここに指示を追加 ★★★
    # ユーザー入力の直前に、毎回出力形式を思い出させるためのシステムメッセージ
    ("system", "あなたの応答は、必ず指示されたJSONスキーマに従ってください。\n{format_instructions}"),
    ("human", "{input}"),
])

# 4. LangChainチェーンの作成
# プロンプト、LLM、出力パーサーを `|` (パイプ)で連結する
# これがLangChain Expression Language (LCEL)の基本的な使い方
chain = prompt | llm | parser

# 会話履歴をLangChainが扱える形式に変換するヘルパー関数
def convert_history_to_langchain_format(history: List[ChatMessage]):
    langchain_history = []
    for msg in history:
        if msg.role == "user":
            langchain_history.append(HumanMessage(content=msg.content))
        elif msg.role == "model":
            # AIの応答はJSON形式の文字列として保存されている
            langchain_history.append(AIMessage(content=msg.content))
    return langchain_history


# メインの実行関数
async def invoke_chain(user_input: str, history: List[ChatMessage]) -> AIResponse:
    """
    ユーザー入力と会話履歴を基にLangChainを実行し、構造化された応答を返す。
    AIが返すJSONの形式（ネスト/フラット/マークダウン）のブレを吸収する。
    """
    langchain_history = convert_history_to_langchain_format(history)
    
    llm_input = {
        "input": user_input,
        "chat_history": langchain_history,
        "format_instructions": parser.get_format_instructions(),
    }

    raw_response_message = await (prompt | llm).ainvoke(llm_input)
    raw_content_str = raw_response_message.content

    print("--- AIからの生の応答 (Raw Response) ---")
    print(raw_content_str)
    print("---------------------------------------")

    # --- ★★★ マークダウンブロックを抽出する処理を追加 ★★★ ---
    # ```json ... ``` または ``` ... ``` のパターンに対応
    match = re.search(r"```(json)?\s*({.*})\s*```", raw_content_str, re.DOTALL)
    if match:
        # マッチした場合、JSON部分だけを抽出
        json_str = match.group(2)
        print("--- INFO: マークダウンブロックからJSONを抽出しました ---")
    else:
        # マッチしない場合、元の文字列をそのままJSONとして扱う
        json_str = raw_content_str.strip()

    # --- 二段構えのパース処理 ---
    # 試行1: 期待通りのネストされた形式としてパースを試みる
    try:
        parsed_response = parser.parse(json_str)
        if parsed_response.question or parsed_response.suggestion:
            print("--- パース成功：ネストされた形式で処理しました ---")
            return parsed_response
    except Exception as e:
        print(f"--- INFO: ネスト形式のパースに失敗({e})。フラット形式として再パースを試みます。 ---")

    # 試行2: フラットな形式として手動でパースし、AIResponseオブジェクトに変換する
    try:
        data = json.loads(json_str)
        if data.get("type") == "question":
            validated_question = Question.model_validate(data)
            print("--- パース成功：フラットなQuestion形式で処理しました ---")
            return AIResponse(question=validated_question, suggestion=None)
        
        elif data.get("type") == "suggestion":
            validated_suggestion = Suggestion.model_validate(data)
            print("--- パース成功：フラットなSuggestion形式で処理しました ---")
            return AIResponse(question=None, suggestion=validated_suggestion)
    
    except Exception as e:
        print(f"--- ERROR: 全てのパースに失敗しました: {e} ---")

    # 全てのパースに失敗した場合、最終的に空のオブジェクトを返す
    return AIResponse(question=None, suggestion=None)