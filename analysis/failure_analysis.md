# 📊 Báo cáo Nhóm: Phân tích Hiệu năng & Rủi ro (Lab 14)

## 1. Tổng quan Dự án
Mục tiêu của nhóm trong Lab 14 là xây dựng một "AI Evaluation Factory" để đánh giá và tối ưu hóa hệ thống RAG Agent. Chúng tôi tập trung vào việc đo lường định lượng sự khác biệt giữa phiên bản Agent cơ bản (V1) và phiên bản đã qua tối ưu hóa (V2).

### Chỉ số Hiệu năng Chính (Full Benchmark - 50 Cases)
| Metadata | Thông số |
| :--- | :--- |
| **Tổng số test cases** | 50 |
| **Agent V1 (Base) Score** | 4.64 / 5.0 |
| **Agent V2 (Optimized) Score** | 4.33 / 5.0 |
| **Retrieval Hit Rate** | 100.0% |
| **Judge Agreement Rate** | 95.5% |

---

## 2. Phân tích "5 Whys" (Root Cause Analysis)
Nhóm đã thực hiện phân tích sâu về việc tại sao Agent V2, dù được tối ưu Prompt Engineering, vẫn có điểm thấp hơn V1 trong một số kịch bản cụ thể.

**Vấn đề: Agent V2 thỉnh thoảng bị Judge chấm điểm thấp hơn V1 (Delta: -0.31).**
1. **Tại sao 1?** Do V2 trả lời quá chi tiết và bao quát các phần liên quan trong SOP, trong khi Ground Truth yêu cầu sự ngắn gọn tuyệt đối.
2. **Tại sao 2?** Vì Prompt V2 (Advanced Persona) khuyến khích tính chuyên nghiệp và đầy đủ, dẫn đến việc đưa thêm các bước phụ (như quy trình Escalation) mà không được nhắc đến trong câu trả lời mẫu.
3. **Tại sao 3?** Do chưa có sự đồng bộ hoàn hảo giữa "Tiêu chí chấm điểm của Judge" và "Cấu trúc phản hồi của Agent".
4. **Tại sao 4?** Vì chúng tôi sử dụng English System Prompt cho một Context Tiếng Việt, dẫn đến những sai khác nhỏ về sắc thái từ ngữ (Nuance) khi model dịch hoặc suy luận chéo ngôn ngữ.
5. **Tại sao 5 (Root Cause)?** **Thiếu sự tinh chỉnh (Fine-tuning) Ground Truth dựa trên sự đa dạng của câu trả lời thực tế.** Hệ thống đánh giá hiện tại đang quá cứng nhắc khi so sánh các phản hồi "đúng nhưng dài" với "đúng và ngắn".

---

## 3. Phân cụm lỗi (Failure Clustering)
| Nhóm lỗi | Tỉ lệ | Mô tả |
| :--- | :--- | :--- |
| **Over-comprehensiveness** | 60% | Agent trả lời đúng nhưng dư thừa thông tin so với Ground Truth. |
| **Instruction Following** | 25% | Một số trường hợp Agent không tuân thủ định dạng bullet point dù được yêu cầu (V1 thường match tốt hơn). |
| **Cross-lingual Nuance** | 15% | Các thuật ngữ như "Escalation" hoặc "CISO" đôi khi bị Agent giải thích rộng hơn ý nghĩa hẹp trong SOP. |

---

## 4. Bài học & Đề xuất hành động
Nhóm rút ra các kết luận quan trọng cho các chu kỳ phát triển tiếp theo:
1. **Pipeline Reliability**: Chúng tôi đã xây dựng thành công pipeline đánh giá hỗ trợ **Checkpoint & Resume**, giúp tiết kiệm thời gian và tài nguyên khi gặp lỗi hạ tầng.
2. **AIOps Culture**: Việc so sánh Delta Progress giữa các phiên bản Agent là bắt buộc để tránh tình trạng "Regression" (giảm sút hiệu năng khi nâng cấp).
3. **Hành động ngay**: Tinh chỉnh lại Prompt của Agent V2 để ưu tiên sự ngắn gọn (Conciseness) tương đương V1, đồng thời mở rộng bộ Ground Truth để ghi nhận các câu trả lời đúng nhưng diễn đạt khác nhau.

---
**Thay mặt nhóm AI Evaluation Factory**
*Ngày hoàn thành: 21/04/2026*
