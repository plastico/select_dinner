# backend/schemas.py
from pydantic import BaseModel, Field
from typing import List, Literal, Optional 


# --- フロントエンドとの通信用スキーマ ---

class ChatMessage(BaseModel):
    role: Literal["user", "model"]
    content: str

class ChatRequest(BaseModel):
    history: List[ChatMessage]
    message: str

# --- LangChainの出力パーサー用スキーマ ---

class Question(BaseModel):
    """ユーザーに質問をするときに使用するスキーマ"""
    type: Literal["question"] = "question"
    message: str = Field(description="ユーザーへの質問文")
    options: List[str] = Field(description="ユーザーに示す回答の選択肢リスト")
    # ★★★ この行を追加 ★★★
    free_text_allowed: bool = Field(default=True, description="自由入力を許可するかどうかを示すフラグ")
    
class Dish(BaseModel):
    """一つの料理を表すスキーマ"""
    name: str = Field(description="料理名")
    description: str = Field(description="その料理の簡単な説明")

class MenuSet(BaseModel):
    """主菜・副菜・汁物の献立セットを表すスキーマ"""
    reason: str = Field(description="この献立セットを提案する理由")
    main_dish: Dish = Field(description="主菜")
    side_dish: Dish = Field(description="副菜")
    soup: Dish = Field(description="汁物")

class Suggestion(BaseModel):
    """最終的な献立を提案するときに使用するスキーマ"""
    type: Literal["suggestion"] = "suggestion"
    message: str = Field(description="提案の際の冒頭メッセージ")
    menus: List[MenuSet] = Field(description="提案する献立セットのリスト")

# 修正箇所: Unionをやめて、一つの包括的なモデルを定義する
class AIResponse(BaseModel):
    """AIの応答を統一的に扱うためのスキーマ。質問か提案のどちらかを含みます。"""
    question: Optional[Question] = Field(default=None, description="ユーザーへの質問。提案の場合はnullになります。")
    suggestion: Optional[Suggestion] = Field(default=None, description="最終的な献立提案。質問の場合はnullになります。")