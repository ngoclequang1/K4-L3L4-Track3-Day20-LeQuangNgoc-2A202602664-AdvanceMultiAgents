# Checklist hoàn thiện lab sau setup

- [x] Đọc README, GUIDE, RUBRIC, REPORT_TEMPLATE và 5 pseudo-code.
- [x] Hoàn thiện các hàm TODO trong agent, subagents, runner, curator.
- [x] Giữ nguyên tests/tasks/scripts và các hàm, hằng số có sẵn.
- [x] Test harness: 29/29 đạt.
- [x] Chạy baseline và subagents trên 3 task học; phân loại lỗi từ trace.
- [x] Curator: 1 lần đầu và 2 retry; đánh giá, loại skill không phù hợp, không sửa tay.
- [x] Chạy development skills-auto và lưu riêng kết quả.
- [x] Commit hypotheses trước freeze; tạo commit/tag freeze.
- [x] Chạy 3 điều kiện × 6 task; lưu đủ 18 run.json và trace.md.
- [x] Retry 5 lượt lỗi đúng một lần với cùng limit; giữ bản đầu và retry-log.
- [x] Verify freeze, tạo bảng so sánh và phân rã check.
- [x] Hoàn thiện báo cáo 10 mục và hướng dẫn tái lập.
- [x] Kiểm tra không có mẫu API key trong kết quả/báo cáo/skills.

Lưu ý: hai lượt chính vẫn GraphRecursionError sau retry (baseline/code-eval,
skills-auto/data-learn). Đã báo cáo nguyên trạng, không coi là task thành công.
Điểm model thấp và không đọc skill là kết quả thực nghiệm, không được sửa checker
hay chỉnh tay đầu ra task để nâng điểm.
