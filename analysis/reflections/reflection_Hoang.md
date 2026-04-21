# 📝 Bài Thu Hoạch Cá Nhân - Lab 14

**Họ và tên:** Nguyễn Xuân Hoàng
**Vai trò:** Data & SDG Specialist

## 1. Kết quả thực hiện
Trong bài Lab này, tôi đảm nhận trách nhiệm xây dựng "nhiên liệu" cho Evaluation Factory:
- **Tạo Golden Set**: Nghiên cứu tài liệu SOP về Kiểm soát truy cập để thiết kế 50 test cases đa dạng, bao gồm các tình huống thông thường và các tình huống khẩn cấp (Escalation).
- **Phát triển SDG Script**: Sử dụng LLM để tự động sinh câu trả lời mẫu (Ground Truth) và gán các `expected_retrieval_ids` phục vụ việc đánh giá Hit Rate.
- **Kiểm soát chất lượng dữ liệu**: Thực hiện rà soát thủ công để đảm bảo các câu hỏi không bị trùng lặp và bám sát nội dung chuyên môn của SOP.

## 2. Khó khăn và Thách thức
- **Hallucination trong dữ liệu mẫu**: Đôi khi model GPT sinh ra các câu trả lời Ground Truth chứa thông tin nằm ngoài SOP. Tôi đã phải bổ sung các logic ràng buộc (constraints) trong prompt của script `synthetic_gen.py` để đảm bảo tính nhất quán.
- **Gán ID tài liệu**: Việc xác định chính xác chunk ID nào chứa câu trả lời cho từng câu hỏi đòi hỏi sự tỉ mỉ để không làm sai lệch chỉ số Hit Rate của nhóm.

## 3. Bài học rút ra
- "Garbage in, Garbage out". Nếu bộ dữ liệu Golden Set không chính xác, mọi chỉ số đánh giá sau đó đều vô nghĩa.
- Việc kết hợp giữa tạo dữ liệu tự động (SDG) và kiểm tra thủ công là phương pháp tối ưu nhất để xây dựng bộ dữ liệu benchmark đáng tin cậy.

---
*Ngày hoàn thành: 21/04/2026*
