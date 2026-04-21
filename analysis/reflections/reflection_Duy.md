# 📝 Bài Thu Hoạch Cá Nhân - Lab 14

**Họ và tên:** Nguyễn Đức Duy
**Vai trò:** QA & Analysis Specialist

## 1. Kết quả thực hiện
Trong Lab 14, vai trò của tôi là đảm bảo chất lượng hệ thống thông qua việc phân tích sâu các sai sót:
- **Failure Analysis**: Phân tích file `benchmark_results.json` để xác định các mẫu lỗi (error patterns). Điều này đã giúp nhóm phát hiện ra nguyên nhân V2 bị điểm thấp do trả lời quá dài dòng không sát Ground Truth.
- **Root Cause Investigation**: Áp dụng kỹ thuật **5 Whys** để truy vết các lỗi về Retrieval. Kết quả cho thấy lỗi 0% Hit Rate ban đầu là do cấu hình sai đường dẫn kiến thức trong Agent.
- **Reporting**: Hoàn thiện báo cáo phân cụm lỗi (Failure Clustering), giúp Team Lead có cái nhìn tổng quát về các rủi ro của hệ thống hiện tại.

## 2. Khó khăn và Thách thức
- **Dữ liệu phân mảnh**: Với 50 cases và nhiều metrics (Accuracy, Hit Rate, MRR), việc tìm ra mối liên hệ giữa chúng khá phức tạp. Tôi đã phải dùng bảng so sánh để phát hiện ra sự tương quan giữa việc model trả lời dài và việc Judge (vốn ưu tiên sự ngắn gọn) chấm điểm thấp.
- **Khối lượng công việc**: Việc đọc và phân tích lý do chấm điểm (reasoning) của 50 cases là rất lớn. Tôi đã tập trung vào các case có điểm < 3 để tối ưu hóa thời gian.

## 3. Bài học rút ra
- Metrics chỉ là bề nổi, phân tích định tính (Root Cause) mới là chìa khóa để cải thiện sản phẩm.
- Một hệ thống QA tốt không chỉ tìm ra lỗi mà còn phải đề xuất được hướng xử lý (như việc đề xuất tinh chỉnh prompt để Agent trả lời cô đọng hơn).

---
*Ngày hoàn thành: 21/04/2026*
