# 📝 Bài Thu Hoạch Cá Nhân - Lab 14

**Họ và tên:** Nguyễn Tuấn Kiệt
**Vai trò:** Retrieval & Backend Engineer

## 1. Kết quả thực hiện
Nhiệm vụ chính của tôi trong Lab 14 là đảm bảo nền tảng kỹ thuật cho việc truy xuất thông tin (Retrieval):
- **Phát triển Retrieval Evaluator**: Hiện thực hóa lớp `RetrievalEvaluator` để tính toán tự động các chỉ số **Hit Rate** và **MRR (Mean Reciprocal Rank)**.
- **Tối ưu hóa pipeline**: Phối hợp cùng Team Lead để debug và sửa lỗi cấu hình đường dẫn tài liệu trong Agent, nâng Hit Rate từ 0% lên 100% bền vững.
- **Mapping Dữ liệu**: Xây dựng logic để đối chiếu Metadata từ kết quả truy xuất thực tế với danh sách Ground Truth ID được cung cấp từ nhóm Data.

## 2. Khó khăn và Thách thức
- **Lỗi đường dẫn (Path mismatch)**: Trong quá trình tích hợp, Agent ban đầu bị cấu hình sai file kiến thức (đọc README thay vì SOP). Tôi đã phải trace log và phối hợp với các thành viên để khắc phục triệt để lỗi này ngay trong giai đoạn đánh giá sơ bộ.
- **Độ trễ hệ thống**: Việc tính toán các metrics phức tạp cho 50 cases cùng lúc đôi khi gây lag. Tôi đã tối ưu hóa các hàm xử lý chuỗi và loop để đảm bảo báo cáo được sinh ra nhanh chóng sau khi benchmark kết thúc.

## 3. Bài học rút ra
- Retrieval là "trái tim" của hệ thống RAG. Nếu quá trình tìm kiếm thông tin không chính xác, mọi nỗ lực tối ưu hóa Prompt của LLM đều sẽ phản tác dụng.
- Kỹ năng debug và tracing log là cực kỳ quan trọng khi làm việc với các hệ thống AI phức tạp, nơi lỗi có thể nằm ở bất kỳ tầng nào từ Ingestion đến Retrieval.

---
*Ngày hoàn thành: 21/04/2026*
