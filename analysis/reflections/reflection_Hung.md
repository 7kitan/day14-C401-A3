# 📝 Bài Thu Hoạch Cá Nhân - Lab 14

**Họ và tên:** Nguyễn Duy Hưng
**Vai trò:** Team Lead & DevOps Engineer

## 1. Kết quả thực hiện
Với vai trò trưởng nhóm trong Lab 14, tôi chịu trách nhiệm điều phối chung và quản lý hạ tầng vận hành:
- **Điều phối nhóm**: Phân chia công việc giữa các mảng Data, AI và QA, đảm bảo các thành phần tích hợp mượt mà vào một pipeline duy nhất.
- **Xây dựng Runner & Checkpoint**: Thiết kế hệ thống `BenchmarkRunner` với cơ chế **Checkpoint & Resume** tự động. Điều này giúp team không bị mất dữ liệu khi gặp sự cố mạng hoặc timeout từ LLM providers.
- **Quản lý Release Gate**: Thiết lập logic tự động so sánh hiệu năng (Regression Testing) trong `main.py`. Hệ thống sẽ dựa trên chỉ số Delta để đưa ra quyết định "Block" hoặc "Approve" việc cập nhật Agent.

## 2. Khó khăn và Thách thức
- **Concurrency & Rate Limit**: Việc cân bằng giữa tốc độ đánh giá (Async) và giới hạn của OpenAI API là một bài toán khó. Tôi đã áp dụng Semaphore và cấu hình batching hợp lý để tối ưu hóa thời gian eval mà không bị lỗi 429.
- **Hợp nhất dữ liệu**: Việc đồng bộ hóa định dạng báo cáo giữa các mảng (Retrieval, LLM Judge) yêu cầu sự thống nhất chặt chẽ về schema dữ liệu ngay từ đầu.

## 3. Bài học rút ra
- Trong các dự án AI quy mô lớn, việc có một quy trình đánh giá chuẩn (Evaluation SOP) quan trọng không kém việc phát triển model.
- Làm việc nhóm hiệu quả cần sự liên lạc liên tục, đặc biệt là khi các module (Agent, Judge, Data) có liên kết chặt chẽ với nhau theo mô hình pipeline.

---
*Ngày hoàn thành: 21/04/2026*
