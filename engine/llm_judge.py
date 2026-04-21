import asyncio
import os
import json
from typing import Dict, Any, List
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()

class LLMJudge:
    def __init__(self, models: List[str] = None):
        if models is None:
            # Sử dụng 2 model OpenAI khác nhau để đối chiếu kết quả (Consensus)
            model_a = os.getenv("JUDGE_MODEL_A", "gpt-4o-mini")
            model_b = os.getenv("JUDGE_MODEL_B", "gpt-4o")
            self.models = [model_a, model_b]
        else:
            self.models = models
            
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
        self.anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) if os.getenv("ANTHROPIC_API_KEY") else None
        
        self.rubrics = {
            "accuracy": "Score from 1-5 based on accuracy compared to Ground Truth. 5: Perfect, 1: Completely wrong or Hallucination.",
            "professionalism": "Score from 1-5 on response style. 5: Professional, polite, 1: Sloppy or inappropriate."
        }

    async def _get_score(self, model: str, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        """Gọi một model cụ thể (OpenAI hoặc Anthropic) để lấy điểm."""
        prompt = f"""
        You are an objective AI judge. Score the Assistant's response based on the Question and the Ground Truth answer.
        
        Question: {question}
        Ground Truth: {ground_truth}
        Assistant's Response: {answer}
        
        Scoring Criteria:
        1. Accuracy: {self.rubrics['accuracy']}
        2. Professionalism: {self.rubrics['professionalism']}
        
        Return JSON format: {{"accuracy": score, "professionalism": score, "reasoning": "brief explanation in English"}}
        """
        
        try:
            # Phân loại model để gọi client tương ứng
            if "gpt" in model.lower() and self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            
            elif "claude" in model.lower() and self.anthropic_client:
                # Claude không hỗ trợ json_object mode như OpenAI, dùng prompt để yêu cầu JSON
                response = await self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt + "\nNOTE: Return ONLY raw JSON, no explanatory text. Must start with { and end with }."}]
                )
                # Parse JSON từ message content và làm sạch nếu có markdown
                text = response.content[0].text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
                return json.loads(text)
            
            else:
                raise ValueError(f"Model {model} không được hỗ trợ hoặc thiếu API Key tương ứng.")
                
        except Exception as e:
            print(f"❌ Lỗi khi gọi Judge {model}: {e}")
            return {"accuracy": 1, "professionalism": 1, "reasoning": f"Error: {str(e)}"}

    async def evaluate_multi_judge(self, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        """
        Gọi nhiều model Judge và tính toán kết quả cuối cùng.
        """
        if not self.openai_client and not self.anthropic_client:
            return {
                "final_score": 0.0,
                "agreement_rate": 0.0,
                "individual_scores": {},
                "reasoning": "Thiếu API Key cho cả OpenAI và Anthropic."
            }

        tasks = [self._get_score(m, question, answer, ground_truth) for m in self.models]
        results = await asyncio.gather(*tasks)
        
        scores = {}
        valid_results = []
        for i, model_name in enumerate(self.models):
            # Kiểm tra xem result có thực sự thành công không (accuracy > 1 là dấu hiệu mẫu)
            # Ở đây ta check nếu reasoning không chứa "Error"
            if "Error" not in str(results[i].get("reasoning", "")):
                scores[model_name] = results[i]
                valid_results.append(results[i])
            else:
                scores[model_name] = {"accuracy": None, "error": results[i].get("reasoning")}
            
        if not valid_results:
            return {
                "final_score": 1.0,
                "agreement_rate": 0.0,
                "individual_scores": scores,
                "status": "all_failed",
                "reasoning": "Tất cả các Judge đều thất bại."
            }
            
        # Tính điểm Accuracy
        accuracy_scores = [r.get("accuracy", 1) for r in valid_results]
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)
        
        # Tính toán độ lệch (nếu có ít nhất 2 kết quả thành công)
        if len(accuracy_scores) >= 2:
            max_diff = max(accuracy_scores) - min(accuracy_scores)
            agreement = 1.0 - (max_diff / 4.0) 
            status = "high_agreement" if max_diff <= 1 else "conflict"
        else:
            agreement = 1.0 # Chỉ có 1 judge thành công
            status = "single_judge"
        
        return {
            "final_score": avg_accuracy,
            "agreement_rate": agreement,
            "individual_scores": scores,
            "status": status,
            "reasoning": valid_results[0].get("reasoning", "")
        }
