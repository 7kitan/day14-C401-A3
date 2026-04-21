# 📝 Bài Thu Hoạch Cá Nhân - Lab 14

**Họ và tên:** Nguyễn Văn Bách
**Vai trò:** AI Evaluation Specialist

## 1. Kết quả thực hiện
Trong bài Lab 14, tôi tập trung vào việc phát triển bộ khung đánh giá tự động và tối ưu hóa phản hồi của Agent:
- **Tối ưu hóa Prompt V2**: Thực hiện English-Vietnamese prompt engineering để cải thiện khả năng trích xuất thông tin từ tài liệu SOP tiếng Việt. Đã nâng điểm số của Agent V2 từ **1.05 lên 4.33**.
- **Xây dựng Benchmark Pipeline**: Hỗ trợ Team Lead hoàn thiện script `main.py`, đảm bảo quy trình chạy benchmark diễn ra ổn định và có khả năng phục hồi từ checkpoint.
- **Phân tích kết quả**: Phối hợp cùng nhóm QA để đối chiếu các câu trả lời của Agent với Ground Truth, từ đó điều chỉnh instruction để tăng tính chính xác và ngắn gọn.

## 2. Khó khăn và Thách thức
- **Sắc thái ngôn ngữ**: Việc sử dụng hệ thống prompt tiếng Anh cho dữ liệu tiếng Việt đôi khi làm model bị "phân tâm" hoặc trả lời quá chi tiết dẫn đến giảm điểm so với câu trả lời mẫu. Tôi đã phải thử nghiệm 3-4 phiên bản prompt khác nhau để tìm ra cấu trúc tối ưu nhất.
- **Batch Processing**: Việc xử lý đồng thời nhiều request dễ dẫn đến timeout. Tôi đã cùng nhóm DevOps tinh chỉnh tham số `batch_size` và `semaphore` để cân bằng giữa tốc độ và tính ổn định.

## 3. Bài học rút ra
- AI Evaluation là một quy trình lặp (Iterative Process). Không có một prompt nào hoàn hảo ngay từ đầu mà cần được đo lường và tinh chỉnh dựa trên dữ liệu thực tế.
- Sự phối hợp giữa nhóm Data (tạo Golden Set) và nhóm Evaluation là chìa khóa để đảm bảo bộ test case phản ánh đúng các tình huống thực tế mà người dùng gặp phải.

---
*Ngày hoàn thành: 21/04/2026*
