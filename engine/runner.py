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

    async def run_single_test(self, test_case: Dict) -> Dict:
        async with self.semaphore:
            start_time = time.perf_counter()
            
            try:
                # 1. Gọi Agent
                response = await self.agent.query(test_case["question"])
                latency = time.perf_counter() - start_time
                
                # Delay nhỏ để giãn cách request giữa Agent và Judge
                await asyncio.sleep(0.5)
                
                # 2. Chạy Retrieval metrics
                ragas_scores = await self.evaluator.score(test_case, response)
                
                # 3. Chạy Multi-Judge
                judge_result = await self.judge.evaluate_multi_judge(
                    test_case["question"], 
                    response["answer"], 
                    test_case["expected_answer"]
                )
                
                return {
                    "test_case": test_case["question"],
                    "agent_response": response["answer"],
                    "latency": latency,
                    "ragas": ragas_scores,
                    "judge": judge_result,
                    "status": "fail" if judge_result["final_score"] < 3 else "pass"
                }
            except Exception as e:
                print(f"❌ Lỗi nghiêm trọng tại case '{test_case.get('question', 'Unknown')}': {e}")
                return {
                    "test_case": test_case.get("question"),
                    "status": "error",
                    "error": str(e),
                    "judge": {"final_score": 0, "agreement_rate": 0},
                    "ragas": {"hit_rate": 0, "mrr": 0}
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
        completed_questions = {r["test_case"] for r in results}
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
            
            # Thêm sleep để tránh Rate Limit (giãn cách rộng hơn để an toàn)
            await asyncio.sleep(3)
            
        return results
