import asyncio
import json
import os
import time
from dotenv import load_dotenv

from engine.runner import BenchmarkRunner
from agent.main_agent import MainAgent
from engine.llm_judge import LLMJudge
from engine.retrieval_eval import RetrievalEvaluator

load_dotenv()

async def run_benchmark_with_results(agent_instance, version_name: str):
    print(f"🚀 Khởi động Benchmark cho {version_name}...")

    if not os.path.exists("data/golden_set.jsonl"):
        print("❌ Thiếu data/golden_set.jsonl. Hãy chạy 'python data/synthetic_gen.py' trước.")
        return None, None

    with open("data/golden_set.jsonl", "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    if not dataset:
        print("❌ File data/golden_set.jsonl rỗng. Hãy tạo ít nhất 1 test case.")
        return None, None

    # Khởi tạo các components thực tế
    evaluator = RetrievalEvaluator()
    judge = LLMJudge()
    
    runner = BenchmarkRunner(agent_instance, evaluator, judge)
    
    # Cấu hình checkpoint cho từng phiên bản
    checkpoint_path = f"reports/checkpoint_{version_name.replace(' ', '_')}.json"
    results = await runner.run_all(dataset, batch_size=5, checkpoint_file=checkpoint_path)

    total = len(results)
    if total == 0:
        return [], {}

    summary = {
        "metadata": {
            "version": version_name, 
            "total": total, 
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "metrics": {
            "avg_score": sum(r["judge"]["final_score"] for r in results) / total,
            "hit_rate": sum(r["ragas"]["hit_rate"] for r in results) / total,
            "mrr": sum(r["ragas"]["mrr"] for r in results) / total,
            "agreement_rate": sum(r["judge"]["agreement_rate"] for r in results) / total,
            "avg_latency": sum(r["latency"] for r in results) / total
        },
        "usage": {
            "total_tokens": sum(r["usage"]["tokens"] for r in results),
            "total_cost_usd": sum(r["usage"]["cost"] for r in results)
        }
    }
    return results, summary

async def main():
    print("=== AI EVALUATION FACTORY: BẮT ĐẦU QUY TRÌNH ===")
    
    # Bước 1 & 2: Chạy Benchmark cho Agent_V1_Base
    agent_v1 = MainAgent(version="v1")
    v1_results, v1_summary = await run_benchmark_with_results(agent_v1, "Agent_V1_Base")
    
    if not v1_summary:
        print("❌ Không thể chạy Benchmark. Kiểm tra lại dữ liệu đầu vào.")
        return

    # Bước 3: Chạy Benchmark cho Agent_V2_Optimized
    agent_v2 = MainAgent(version="v2")
    v2_results, v2_summary = await run_benchmark_with_results(agent_v2, "Agent_V2_Optimized")
    
    # Bước 4: So sánh và đưa ra quyết định (Regression Gate)
    print("\n📊 --- KẾT QUẢ SO SÁNH (REGRESSION) ---")
    score_v1 = v1_summary["metrics"]["avg_score"]
    score_v2 = v2_summary["metrics"]["avg_score"]
    delta = score_v2 - score_v1
    
    cost_v2 = v2_summary["usage"]["total_cost_usd"]
    tokens_v2 = v2_summary["usage"]["total_tokens"]

    print(f"V1 Accuracy Score: {score_v1:.2f}")
    print(f"V2 Accuracy Score: {score_v2:.2f}")
    print(f"Delta Accuracy: {'+' if delta >= 0 else ''}{delta:.2f}")
    print(f"V2 Hit Rate: {v2_summary['metrics']['hit_rate']:.2f}")
    print("-" * 30)
    print(f"💰 TỔNG CHI PHÍ (V2): ${cost_v2:.4f}")
    print(f"🪙 TỔNG TOKENS (V2): {tokens_v2:,}")

    # Xuất báo cáo
    os.makedirs("reports", exist_ok=True)
    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump(v2_summary, f, ensure_ascii=False, indent=2)
    with open("reports/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(v2_results, f, ensure_ascii=False, indent=2)

    # Auto-Gate Decision
    if delta >= 0:
        print("\n✅ QUYẾT ĐỊNH: CHẤP NHẬN BẢN CẬP NHẬT (APPROVE RELEASE)")
    else:
        print("\n❌ QUYẾT ĐỊNH: TỪ CHỐI (BLOCK RELEASE) - HIỆU NĂNG GIẢM SÚT")

if __name__ == "__main__":
    asyncio.run(main())
