import asyncio
import time
import json
import os
from typing import List, Dict
# Import other components...

class BenchmarkRunner:
    def __init__(self, agent, evaluator, judge, max_concurrent: int = 5):
        self.agent = agent
        self.evaluator = evaluator
        self.judge = judge
        self.semaphore = asyncio.Semaphore(max_concurrent)

    def _estimate_tokens(self, text: str) -> int:
        """Ước tính số lượng token dựa trên độ dài văn bản (1 token ~ 4 ký tự)."""
        if not text:
            return 0
        return len(text) // 4 + 1

    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Tính toán chi phí dựa trên bảng giá OpenAI (USD)."""
        # Giá theo 1M tokens
        prices = {
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4o": {"input": 5.00, "output": 15.00},
            "claude": {"input": 3.00, "output": 15.00} # Giá trung bình tham khảo
        }
        
        # Tìm model phù hợp nhất
        selected_price = prices["gpt-4o-mini"] # Default
        for key in prices:
            if key in model.lower():
                selected_price = prices[key]
                break
        
        cost = (prompt_tokens * selected_price["input"] + completion_tokens * selected_price["output"]) / 1_000_000
        return cost

    async def run_single_test(self, test_case: Dict) -> Dict:
        async with self.semaphore:
            start_time = time.perf_counter()
            
            try:
                # 1. Gọi Agent
                question = test_case["question"]
                response = await self.agent.query(question)
                latency = time.perf_counter() - start_time
                
                # Ước tính tokens của Agent
                agent_prompt_tokens = self._estimate_tokens(question)
                agent_completion_tokens = self._estimate_tokens(response["answer"])
                agent_cost = self._calculate_cost(getattr(self.agent, 'model', 'gpt-4o-mini'), agent_prompt_tokens, agent_completion_tokens)

                # Delay nhỏ để giãn cách request giữa Agent và Judge
                await asyncio.sleep(0.5)
                
                # 2. Chạy Retrieval metrics
                ragas_scores = await self.evaluator.score(test_case, response)
                
                # 3. Chạy Multi-Judge
                judge_result = await self.judge.evaluate_multi_judge(
                    question, 
                    response["answer"], 
                    test_case["expected_answer"]
                )
                
                # Ước tính cost của Judge (Giả định Judge tốn gấp đôi Token do có prompt dài)
                judge_prompt_tokens = self._estimate_tokens(question + response["answer"] + test_case["expected_answer"]) * 2
                judge_completion_tokens = 200 # Ước tính kết quả JSON của Judge
                
                # Tính tổng chi phí cho 1 Case
                total_tokens = agent_prompt_tokens + agent_completion_tokens + judge_prompt_tokens + judge_completion_tokens
                total_cost = agent_cost + self._calculate_cost("gpt-4o", judge_prompt_tokens, judge_completion_tokens)
                
                return {
                    "test_case": question,
                    "agent_response": response["answer"],
                    "latency": latency,
                    "ragas": ragas_scores,
                    "judge": judge_result,
                    "usage": {
                        "tokens": total_tokens,
                        "cost": total_cost
                    },
                    "status": "fail" if judge_result["final_score"] < 3 else "pass"
                }
            except Exception as e:
                print(f"❌ Lỗi nghiêm trọng tại case '{test_case.get('question', 'Unknown')}': {e}")
                return {
                    "test_case": test_case.get("question"),
                    "status": "error",
                    "error": str(e),
                    "judge": {"final_score": 0, "agreement_rate": 0},
                    "ragas": {"hit_rate": 0, "mrr": 0},
                    "usage": {"tokens": 0, "cost": 0}
                }

    async def run_all(self, dataset: List[Dict], batch_size: int = 1, checkpoint_file: str = "reports/checkpoint.json") -> List[Dict]:
        """
        Chạy benchmark hỗ trợ Resume từ điểm dừng trước đó.
        """
        results = []
        
        # 1. Thử nạp dữ liệu từ Checkpoint
        if os.path.exists(checkpoint_file):
            try:
                with open(checkpoint_file, "r", encoding="utf-8") as f:
                    results = json.load(f)
                print(f"🔄 Đã tìm thấy file checkpoint. Đang khôi phục {len(results)} kết quả...")
            except Exception as e:
                print(f"⚠️ Không thể đọc checkpoint: {e}. Sẽ chạy lại từ đầu.")

        # 2. Lọc danh sách cần chạy (chỉ giữ lại những câu chưa có kết quả)
        completed_questions = {r["test_case"] for r in results if r["status"] != "error"}
        remaining_dataset = [case for case in dataset if case["question"] not in completed_questions]

        if not remaining_dataset:
            print("✅ Tất cả các câu trong dataset đã hoàn thành. Trả về kết quả từ checkpoint.")
            return results

        total_remaining = len(remaining_dataset)
        total_batches = (total_remaining + batch_size - 1) // batch_size
        print(f"🔄 Bắt đầu chạy {total_remaining} cases còn lại ({total_batches} batches)...")
        
        for i in range(0, total_remaining, batch_size):
            batch_num = i // batch_size + 1
            print(f"📦 Đang xử lý batch {batch_num}/{total_batches}...")
            batch = remaining_dataset[i:i + batch_size]
            tasks = [self.run_single_test(case) for case in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            
            # Ghi checkpoint ngay sau mỗi batch để đảm bảo an toàn
            os.makedirs(os.path.dirname(checkpoint_file), exist_ok=True)
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            # Thêm sleep để tránh Rate Limit
            await asyncio.sleep(2)
            
        return results
