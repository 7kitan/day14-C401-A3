# 📝 Bài Thu Hoạch Cá Nhân - Lab 14

**Họ và tên:** Trần Trọng Giang
**Vai trò:** AI Specialist & Judge Architect

## 1. Kết quả thực hiện
Trong Lab 14, nhiệm vụ trọng tâm của tôi là thiết kế "hệ thống giám khảo" để đảm bảo tính khách quan cho quá trình benchmark:
- **Multi-Judge Consensus**: Thiết kế lớp `LLMJudge` hỗ trợ sử dụng đa model (GPT-4o-mini & GPT-4o) để thực hiện chấm điểm chéo.
- **Grading Rubrics**: Xây dựng bộ tiêu chuẩn chấm điểm (rubrics) tập trung vào 2 khía cạnh: **Accuracy** (Độ chính xác nội dung) và **Professionalism** (Sự chuyên nghiệp trong diễn đạt).
- **Consensus Analysis**: Thực hiện tính toán **Agreement Rate**. Trong lần chạy cuối cùng, hệ thống đạt độ đồng thuận cao (~95.5%), khẳng định tính tin cậy của bộ Judge.

## 2. Khó khăn và Thách thức
- **Xử lý Timeout**: Đôi khi các model Judge phản hồi chậm hoặc bị lỗi kết nối mạng. Tôi đã phải phối hợp cùng nhóm Backend để xử lý lỗi timeout và cơ chế retry để không làm gián đoạn pipeline.
- **Judge bias**: Nhận thấy các model mini đôi khi chấm điểm "thoáng" hơn model lớn. Tôi đã tinh chỉnh hệ thống instruction của Judge để chúng bám sát Ground Truth hơn, giảm thiểu các trường hợp "hallucination judge".

## 3. Bài học rút ra
- Đừng bao giờ tin vào một model duy nhất. Việc sử dụng Multi-Judge giúp phát hiện ra các sai sót mà một model lẻ có thể bỏ qua.
- Sự đồng thuận (Agreement Rate) là chỉ số quan trọng phản ánh mức độ "chuẩn hóa" của bộ tiêu chuẩn chấm điểm mà nhóm đã đề ra.

---
*Ngày hoàn thành: 21/04/2026*
