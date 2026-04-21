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
            # Và 1 model thứ 3 làm Tie-breaker khi có xung đột
            model_a = os.getenv("JUDGE_MODEL_A", "gpt-4o-mini")
            model_b = os.getenv("JUDGE_MODEL_B", "gpt-4o")
            model_c = os.getenv("JUDGE_MODEL_C", "gpt-4o") # Tie-breaker mặc định là GPT-4o
            self.models = [model_a, model_b]
            self.tie_breaker_model = model_c
        else:
            self.models = models[:2]
            self.tie_breaker_model = models[2] if len(models) > 2 else models[-1]
            
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
                response = await self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt + "\nNOTE: Return ONLY raw JSON, no explanatory text. Must start with { and end with }."}]
                )
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
        Gọi nhiều model Judge và thực hiện Tie-breaker nếu cần.
        """
        if not self.openai_client and not self.anthropic_client:
            return {
                "final_score": 0.0,
                "agreement_rate": 0.0,
                "individual_scores": {},
                "reasoning": "Thiếu API Key cho cả OpenAI và Anthropic."
            }

        # Bước 1: Gọi 2 Judge ban đầu
        tasks = [self._get_score(m, question, answer, ground_truth) for m in self.models]
        results = await asyncio.gather(*tasks)
        
        valid_results = []
        scores = {}
        for i, model_name in enumerate(self.models):
            scores[model_name] = results[i]
            if "Error" not in str(results[i].get("reasoning", "")):
                valid_results.append(results[i])
            
        if not valid_results:
            return {"final_score": 1.0, "agreement_rate": 0.0, "individual_scores": scores, "status": "all_failed"}
            
        accuracy_scores = [r.get("accuracy", 1) for r in valid_results]
        max_diff = max(accuracy_scores) - min(accuracy_scores) if len(accuracy_scores) >= 2 else 0
        
        # Bước 2: Kiểm tra xung đột (Xung đột khi lệch > 1 điểm)
        if max_diff > 1 and self.tie_breaker_model:
            print(f"⚖️ Xung đột điểm số ({max_diff}). Đang gọi Tie-breaker: {self.tie_breaker_model}...")
            tie_result = await self._get_score(self.tie_breaker_model, question, answer, ground_truth)
            scores[f"{self.tie_breaker_model} (Tie-breaker)"] = tie_result
            
            # Điểm cuối bằng trung bình của Tie-breaker và điểm gần nó nhất trong các Judge cũ
            final_accuracy = tie_result.get("accuracy", 1)
            reasoning = f"[Tie-breaker used] {tie_result.get('reasoning', '')}"
            status = "resolved_by_tie_breaker"
        else:
            final_accuracy = sum(accuracy_scores) / len(accuracy_scores)
            reasoning = valid_results[0].get("reasoning", "")
            status = "high_agreement" if max_diff <= 1 else "single_judge"

        agreement = 1.0 - (max_diff / 4.0) if len(accuracy_scores) >= 2 else 1.0
        
        return {
            "final_score": final_accuracy,
            "agreement_rate": agreement,
            "individual_scores": scores,
            "status": status,
            "reasoning": reasoning
        }

