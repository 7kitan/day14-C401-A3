# 📊 Báo cáo Nhóm: Phân tích Hiệu năng & Rủi ro (Lab 14 - Expert Level)

## 1. Tổng quan Dự án
Mục tiêu của nhóm trong Lab 14 là xây dựng một "AI Evaluation Factory" để đánh giá và tối ưu hóa hệ thống RAG Agent. Chúng tôi đã thực hiện benchmark phiên bản Agent V2 (Optimized) trên bộ Golden Dataset gồm 51 câu hỏi được sinh từ tài liệu Access Control SOP.

### 📈 So sánh Hiệu năng Regression (V1 vs V2)
| Chỉ số | Agent V1 (Base) | Agent V2 (Optimized) | Biến thiên (Delta) |
| :--- | :---: | :---: | :---: |
| **Accuracy Score** | **3.98** | **3.47** | 📉 **-0.51** |
| **Hit Rate (Retrieval)** | 70.59% | 70.59% | 0.0% |
| **Average Latency** | 1.95s | **1.31s** | ⚡ **-33%** |
| **Total Cost (51 Cases)** | $0.2439 | **$0.1999** | 💰 **-18%** |

> [!WARNING]
> **Nhận định Regression Gate:** Mặc dù phiên bản V2 đạt được sự tối ưu đáng kể về tốc độ và chi phí, nhưng điểm **Accuracy sụt giảm nghiêm trọng (-0.51)**. Điều này vi phạm tiêu chuẩn chất lượng để Release. Hệ thống khuyến nghị **Rollback** hoặc tinh chỉnh lại Prompt Engineering của V2.

---

## 2. Phân tích "5 Whys" (Root Cause Analysis Kỹ thuật)
Nhóm đã phân tích các case thất bại điển hình (Score 1.0 - 2.0), ví dụ: "Công cụ lưu trữ audit log" hoặc "Thời hạn báo cáo CISO".

**Vấn đề: Agent không tìm thấy thông tin (Hallucination of Absence) dù tài liệu có dữ liệu.**
1. **Tại sao 1?** Do giai đoạn Retrieval trả về Section không chứa từ khóa mục tiêu (Hit Rate chỉ đạt 70%).
2. **Tại sao 2?** Vì thuật toán Tìm kiếm từ khóa (Keyword-based) hiện tại quá đơn giản, không xử lý được các từ đồng nghĩa hoặc các thuật ngữ chuyên môn ghép (e.g., "Audit log" vs "Security Audit").
3. **Tại sao 3?** Do tài liệu SOP được viết bằng tiếng Việt nhưng các câu hỏi/từ khóa truy vấn đôi khi mang sắc thái thuật ngữ tiếng Anh, gây lệch pha khi so khớp từ vựng thô (Exact matching).
4. **Tại sao 4?** Hệ thống **Chunking** hiện tại chia theo Section cứng nhắc, nếu thông tin nằm ở ranh giới giữa 2 Section (Ingestion boundary), Retrieval sẽ dễ dàng bỏ sót.
5. **Tại sao 5 (Root Cause)?** **Sự thiếu hụt của Semantic Search (Tìm kiếm ngữ nghĩa).** Việc chỉ dựa vào Keyword matching thuần túy trên một bộ tài liệu kỹ thuật có nhiều thuật ngữ đồng nghĩa (Audit, Review, Log, Splunk) dẫn đến tỉ lệ sót thông tin (Recall) cao, từ đó làm giảm điểm Accuracy tổng thể.

---

## 3. Phân tính Chi phí (Cost Analysis)
Dữ liệu thực tế từ phiên chạy 51 cases:

| Hạng mục | Thông số |
| :--- | :--- |
| **Tổng Tokens tiêu thụ** | 17,618 |
| **Tổng chi phí thực tế (USD)** | **$0.19998** |
| **Chi phí trung bình/Case** | ~$0.0039 |

> [!NOTE]
> Chi phí này bao gồm cả việc gọi Agent V2 (Prompt phức tạp) và hệ thống Multi-Judge (GPT-4o). Mức giá này hoàn toàn khả thi cho việc chạy Regression Testing định kỳ trong môi trường CI/CD doanh nghiệp.

---

## 4. Phân cụm lỗi (Failure Clustering)
| Nhóm lỗi | Tỉ lệ (Ước tính) | Ví dụ thực tế |
| :--- | :--- | :--- |
| **Retrieval Miss (Keyword)** | 60% | Không tìm thấy "Splunk" dù có trong Section 7. |
| **Partial Answer** | 30% | Chỉ nêu "Line Manager" mà quên "IT Admin" cho quyền Level 2. |
| **Terminology Confusion** | 10% | Nhầm lẫn giữa quy trình phê duyệt thường và Escalation (P1). |

---

## 5. Bài học & Đề xuất hành động
1. **Multi-Judge Reliability**: Độ đồng thuận 99% cho thấy bộ Judge gpt-4o và gpt-4o-mini hoạt động cực kỳ ổn định, có thể tin tưởng để làm Gate tự động.
2. **Retrieval Upgrade**: Cần thay thế Keyword Search bằng **Vector Embeddings (OpenAI Text-embedding-3-small)** để giải quyết vấn đề Hit Rate thấp (70%).
3. **Action Plan**: Tinh chỉnh lại bộ Ground Truth để bao quát các trường hợp Agent trả lời đúng ý nhưng khác từ ngữ so với đáp án mẫu.

---
**Thay mặt nhóm AI Evaluation Factory**
*Ngày hoàn thành: 21/04/2026*
