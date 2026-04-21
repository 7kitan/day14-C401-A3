from typing import List, Dict

class RetrievalEvaluator:
    def __init__(self):
        pass

    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
        """
        Tính toán xem ít nhất 1 trong expected_ids có nằm trong top_k của retrieved_ids không.
        """
        if not expected_ids or not retrieved_ids:
            return 0.0
        top_retrieved = retrieved_ids[:top_k]
        hit = any(doc_id in top_retrieved for doc_id in expected_ids)
        return 1.0 if hit else 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        """
        Tính Mean Reciprocal Rank.
        Tìm vị trí đầu tiên của một expected_id trong retrieved_ids.
        """
        if not expected_ids or not retrieved_ids:
            return 0.0
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return 1.0 / (i + 1)
        return 0.0

    async def score(self, test_case: Dict, agent_response: Dict) -> Dict:
        """
        Tính toán các chỉ số retrieval cho một test case cụ thể.
        """
        expected_ids = test_case.get("expected_retrieval_ids", [])
        # Agent cần trả về metadata chứa retrieved_ids
        retrieved_ids = agent_response.get("metadata", {}).get("retrieved_ids", [])
        
        # Nếu Agent không trả về IDs cụ thể mà chỉ trả về context, 
        # trong thực tế ta có thể mapping context -> ID. 
        # Ở đây giả định Agent đã được nâng cấp để trả về IDs.
        
        hit_rate = self.calculate_hit_rate(expected_ids, retrieved_ids)
        mrr = self.calculate_mrr(expected_ids, retrieved_ids)
        
        return {
            "hit_rate": hit_rate,
            "mrr": mrr
        }
