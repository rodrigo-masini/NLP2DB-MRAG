from typing import Dict, Any
from pilot.scene.base_chat import BaseChat
from pilot.scene.base import ChatScene
from pilot.configs.config import Config
from pilot.summary.db_summary_client import DBSummaryClient

CFG = Config()

class ChatWithDbQA(BaseChat):
    chat_scene: str = ChatScene.ChatWithDbQA.value

    def __init__(self, chat_session_id, db_name, user_input, **kwargs):
        super().__init__(
            chat_mode=ChatScene.ChatWithDbQA,
            chat_session_id=chat_session_id,
            current_user_input=user_input,
            **kwargs,
        )
        self.db_name = db_name
        self.top_k = CFG.KNOWLEDGE_SEARCH_TOP_SIZE

    async def generate_input_values(self) -> Dict[str, Any]:
        """Generates input values for the prompt template."""
        table_info = ""
        if self.db_name:
            client = DBSummaryClient()
            # This call needs to be async if it involves I/O or LLM calls
            table_info = await client.get_db_summary(
                dbname=self.db_name, query=self.current_user_input, topk=self.top_k
            )
        
        return {
            "input": self.current_user_input,
            "table_info": table_info,
        }
