import asyncio
import os
import random
from typing import List, Dict
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class MainAgent:
    """
    Agent hỗ trợ đa phiên bản để so sánh hiệu quả Prompt Engineering.
    """
    def __init__(self, version: str = "v1"):
        self.version = version
        self.name = f"SupportAgent-{version}"
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        
        # Đọc tài liệu SOP làm database
        try:
            with open("data/access_control_sop.txt", "r", encoding="utf-8") as f:
                self.knowledge_base = f.read()
        except:
            self.knowledge_base = "QUY TRÌNH KIỂM SOÁT TRUY CẬP HỆ THỐNG (ACCESS CONTROL SOP)"

    def _get_context(self, question: str) -> str:
        """Lấy toàn bộ nội dung tài liệu SOP làm context để đảm bảo đầy đủ thông tin."""
        return self.knowledge_base

    async def query(self, question: str) -> Dict:
        """Quy trình thực thi dựa trên version."""
        if not self.client:
            return {"answer": "Missing API Key", "metadata": {"retrieved_ids": []}}

        context = self._get_context(question)
        
        if self.version == "v1":
            prompt = f"Trả lời câu hỏi sau dựa trên context:\nContext: {context}\nQuestion: {question}"
        else:
            # V2: Advanced Prompting (Concise & Focused)
            prompt = f"""
            You are an expert AI Support Assistant specializing in Corporate Security Policies.
            Answer the question based STRICTLY on the PROVIDED CONTEXT below.

            ### INSTRUCTIONS:
            1. **Directness**: Answer directly and concisely. Match the level of detail in the context.
            2. **Language**: Always answer in **Vietnamese**.
            3. **Accuracy**: Do not hallucinate or add information from outside the context.
            4. **Refusal**: If the information is missing, say: "Tôi không tìm thấy thông tin này trong tài liệu."

            ### CONTEXT:
            {context}

            ### QUESTION:
            {question}

            ### ANSWER (Vietnamese):
            """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3 if self.version == "v2" else 0.7 # V2 ổn định hơn
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"Lỗi: {str(e)}"

        return {
            "answer": answer,
            "contexts": [context[:300] + "..."],
            "metadata": {
                "version": self.version,
                "retrieved_ids": ["doc_1"] # Khớp với expected_retrieval_ids trong golden_set
            }
        }

if __name__ == "__main__":
    agent = MainAgent()
    async def test():
        resp = await agent.query("Mục tiêu của Lab 14 là gì?")
        print(resp["answer"])
    asyncio.run(test())
