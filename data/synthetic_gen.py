import json
import asyncio
import os
from typing import List, Dict
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def generate_qa_from_text(text: str, num_pairs: int = 10) -> List[Dict]:
    """
    Sử dụng OpenAI API để tạo các cặp (Question, Expected Answer, Context)
    từ đoạn văn bản cho trước.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return []
        
    client = AsyncOpenAI(api_key=api_key)
    print(f"🚀 Đang tạo {num_pairs} cặp QA từ văn bản nguồn...")
    
    prompt = f"""
    Bạn là một chuyên gia về AI Evaluation. Dựa trên văn bản dưới đây, hãy tạo ra {num_pairs} cặp câu hỏi và trả lời.
    
    Yêu cầu:
    1. Trả về định dạng JSON list.
    2. Mỗi phần tử gồm:
       - 'question': Câu hỏi.
       - 'expected_answer': Câu trả lời chuẩn.
       - 'expected_retrieval_ids': Danh sách các Section ID chứa đáp án (e.g., ['section_1', 'section_2']).
       - 'metadata': {{'difficulty': 'easy/hard', 'type': 'fact-check/adversarial'}}
    3. Đảm bảo có ít nhất 2 câu hỏi 'adversarial' (tấn công prompt) hoặc 'edge case' (ngoài ngữ cảnh).
    
    LƯU Ý: Văn bản nguồn được phân chia thành các Section như '=== Section 1: ... ==='. Hãy sử dụng ID dạng 'section_x' tương ứng.
    
    Văn bản nguồn:
    {text}
    """

    try:
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        # Giả sử LLM trả về dạng {"qa_pairs": [...]}
        pairs = data.get("qa_pairs", []) if isinstance(data, dict) else data
        if not pairs and isinstance(data, dict):
             # Fallback nếu LLM trả về trực tiếp list trong một key khác hoặc format khác
             for key in data:
                 if isinstance(data[key], list):
                     pairs = data[key]
                     break
        return pairs
    except Exception as e:
        print(f"❌ Lỗi khi gọi OpenAI: {e}")
        return []

async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ Cảnh báo: OPENAI_API_KEY chưa được thiết lập. Dùng dữ liệu mẫu.")
        qa_pairs = [
            {"question": "Lab 14 yêu cầu gì?", "expected_answer": "...", "expected_retrieval_ids": ["readme_1"], "metadata": {"difficulty": "easy"}}
        ]
    else:
        # Sử dụng tài liệu Access Control SOP làm dữ liệu nguồn
        with open("data/access_control_sop.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Tạo 50 cases theo từng batch 10 để ổn định hơn
        total_cases = 50
        batch_size = 10
        qa_pairs = []
        
        for i in range(0, total_cases, batch_size):
            print(f"📦 Đang tạo batch {i//batch_size + 1}/{total_cases//batch_size}...")
            batch_pairs = await generate_qa_from_text(content, num_pairs=batch_size)
            qa_pairs.extend(batch_pairs)
            # Tránh Rate Limit nhẹ
            await asyncio.sleep(1)
    
    os.makedirs("data", exist_ok=True)
    with open("data/golden_set.jsonl", "w", encoding="utf-8") as f:
        for pair in qa_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    
    print(f"✅ Hoàn thành! Đã lưu {len(qa_pairs)} cases vào data/golden_set.jsonl")

if __name__ == "__main__":
    asyncio.run(main())
