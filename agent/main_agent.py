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

    def _get_sections(self) -> Dict[str, str]:
        """Chia tài liệu SOP thành các Sections dựa trên tiêu đề '=== Section X: ... ==='."""
        sections = {}
        current_section_id = "unknown"
        lines = self.knowledge_base.split('\n')
        
        current_content = []
        for line in lines:
            if line.startswith("=== Section"):
                if current_section_id != "unknown":
                    sections[current_section_id] = '\n'.join(current_content).strip()
                
                # Trích xuất ID (e.g., 'section_1')
                try:
                    parts = line.split(':')
                    sec_name = parts[0].strip(' =').lower().replace(' ', '_')
                    current_section_id = sec_name
                except:
                    current_section_id = f"section_{len(sections) + 1}"
                
                current_content = [line]
            else:
                current_content.append(line)
        
        # Add last section
        if current_section_id != "unknown":
            sections[current_section_id] = '\n'.join(current_content).strip()
            
        return sections

    def _retrieve_context(self, question: str) -> Dict:
        """Tìm kiếm section phù hợp nhất dựa trên từ khóa (Simulated Vector Search)."""
        sections = self._get_sections()
        best_section_id = "section_1" # Default
        max_matches = -1
        
        # Một logic tìm kiếm đơn giản: đếm số từ khóa xuất hiện trong section
        keywords = [w.lower() for w in question.split() if len(w) > 3]
        
        for sec_id, content in sections.items():
            content_lower = content.lower()
            matches = sum(1 for kw in keywords if kw in content_lower)
            if matches > max_matches:
                max_matches = matches
                best_section_id = sec_id
                
        return {
            "content": sections.get(best_section_id, self.knowledge_base),
            "section_id": best_section_id
        }

    async def query(self, question: str) -> Dict:
        """Quy trình thực thi dựa trên version."""
        if not self.client:
            return {"answer": "Missing API Key", "metadata": {"retrieved_ids": []}}

        # Thực hiện Retrieval "thật"
        retrieval_result = self._retrieve_context(question)
        context = retrieval_result["content"]
        section_id = retrieval_result["section_id"]
        
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
                temperature=0.3 if self.version == "v2" else 0.7 
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"Lỗi: {str(e)}"

        return {
            "answer": answer,
            "contexts": [context[:300] + "..."],
            "metadata": {
                "version": self.version,
                "retrieved_ids": [section_id] 
            }
        }

if __name__ == "__main__":
    agent = MainAgent()
    async def test():
        resp = await agent.query("Mục tiêu của Lab 14 là gì?")
        print(resp["answer"])
    asyncio.run(test())
