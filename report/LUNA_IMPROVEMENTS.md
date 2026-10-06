# Cải thiện runtime và thử nghiệm Luna — 06/10/2026

Đây là thí nghiệm bổ sung trên **tập học**, không thay báo cáo/thí nghiệm đã freeze.
Không sửa checker, task gốc, tests gốc, prompt/hằng số được cung cấp, hay `skills/auto`.

## Thay đổi code

- Agent tự cấu hình `gpt-6-luna` với Chat Completions và `reasoning_effort=none`.
  Bỏ tham số temperature cho Luna, dùng mặc định API; không áp cấu hình này lên model khác.
  Model truyền từ caller được copy, không bị sửa trực tiếp.
- Thêm PYTHONPATH tới workspace của sandbox để test import được package.
- Khi edit dùng chuỗi cũ hoặc shell có SyntaxError/thiếu thư viện, phản hồi công cụ
  chỉ rõ cách phục hồi thay vì lặp nguyên lệnh. Không chứa đáp án task.
- Trên Linux, chuẩn hóa CRLF thành LF cho file Python trong sandbox trước khi agent chạy.
  Không ghi vào workspace gốc và không sửa điểm/checker; regression test kiểm tra
  hash test gốc đạt đồng thời bytes trong repository không đổi.
- Runner lưu bản ghi cả khi build agent lỗi, chỉ lấy final_message từ AI message
  đã kết thúc, và ghi model/API/reasoning/nguồn skill/revision trong các lượt mới.
- Cho phép nguồn skill bổ sung nhưng bắt buộc lưu trong results directory riêng.
  CLI có sẵn không bị sửa; dùng script bổ sung bên dưới cho nguồn skill mới.
- Curator nhấn mạnh phải lưu đầy đủ quy ước từ learning feedback; không sửa tay skill.

## Kết quả thực tế

| Learning task | 4o-mini chính trước đây (limit 40) | Luna, skill v2 (limit 60) | Lỗi runtime cuối | skills_read |
|---|---:|---:|---|---:|
| code-learn | 2/10 | 10/10 | Không | 1 |
| data-learn | 0/8 | 5/8 | Không | 2 |
| logs-learn | 0/9 | 9/9 | Không | 1 |

Nguồn cuối: `results/luna-learning-v5/skills-auto/*/run.json` và `trace.md`.
Mean score cuối 0,875; tổng check 24/27. Code và logs đạt đủ yêu cầu được checker kiểm tra.
Data đạt cả 5 check kỹ thuật nhưng còn 3 rule thất bại: tiền integer cents,
meta(source, rows_in, rows_used), clean.csv với schema yêu cầu.
**Chưa đạt toàn bộ lab** và chưa có bộ so sánh 18 lượt mới bằng Luna; không kết luận
khả năng tổng quát hóa sang eval từ ba task học này.

Skill cuối ở `report/generated-skills/luna-auto-v2`: python-code-repair và log-file-triage.
Curator trả hai skill hợp lệ; không có skill dữ liệu bảng trong bộ cuối, vì vậy các quy ước
reporting của data chưa được truyền đầy đủ. skills_read=2 của data là đọc hai skill hiện có,
không có nghĩa nó đã đọc một skill tabular. V1 ở `report/generated-skills/luna-auto` có tabular-analysis,
nhưng skill đó chỉ nói giữ schema/đơn vị khi được chỉ định, không lưu đầy đủ quy ước đã học.
Không ghép thủ công nội dung hoặc chèn các giá trị đáp án vào skill/runner để tăng điểm.

Skill bổ sung ban đầu được tạo ở skills/luna-auto và skills/luna-auto-v2, đúng như
skills_source lịch sử trong run.json. Kiểm tra cuối cho thấy verify_freeze kiểm tra
toàn bộ skills/ nên các thư mục bổ sung đã chuyển sang report/generated-skills/,
giữ nguyên bytes. Không sửa metadata lịch sử; hash bộ skill không đổi. Script chạy
tiếp dùng vị trí mới, còn thư mục skills/ được khôi phục đúng trạng thái đã freeze.

Cả model, cấu hình nhiệt độ, runtime, newline, skill và giới hạn bước đều thay đổi;
do đó bảng trên chỉ mô tả cải thiện quan sát được, không tách riêng tác dụng của Luna.

## Các lượt trung gian được giữ nguyên

- `results/runtime-recovery-v2`: 4o-mini + phản hồi phục hồi; code 1/10 và data 0/8,
  cả hai vẫn chạm limit 40. Chỉ sửa môi trường không đủ khắc phục hành vi model này.
- `results/luna-runtime-v3`: Luna + skill frozen cũ; code 9/10, data 4/8, không lỗi runtime.
  Code đọc skill thật; CRLF còn gây false negative ở tests_not_modified trong lượt này.
- `results/luna-learning-v4`: code 10/10 nhưng bị ngắt ở 40 trước kiểm chứng cuối;
  data 5/8; logs 5/9. Ba skill curator V1 được lưu nguyên văn.
- `results/luna-learning-v5`: dùng giới hạn chuẩn 60 của CLI lab, không chỉ tăng vô hạn.
  Trace code V4 cho thấy nhiều edit tuần tự, không phải vòng lặp nguyên lệnh, nên tăng
  40→60 là để đủ bước kiểm chứng/kết thúc. Ba lượt cuối không có lỗi.
- Lượt curator Luna đầu bị API 400 vì temperature=0 đi cùng reasoning mặc định;
  sửa cấu hình rồi có hai lượt sinh skill thành công. Không chạy curator tiếp trong phiên này.
  Một lệnh PowerShell khởi động bị treo được hủy trước khi vào container; dùng cmd và mount
  tương đối để chạy lượt V5. Không tính lệnh chưa vào container là lượt LLM.

## Kiểm chứng và tái lập

36/36 test đạt: 29 test gốc + 7 regression test trong report/test_runtime_fixes.py.
verify_freeze: checked 6 runs of skill conditions: OK.
verify_submission xác nhận file bảo vệ không đổi, đủ 18 kết quả chính cũ,
và không thấy mẫu API key trong report/results/skills.

Chạy từ PowerShell, với `.env` chứa LAB_MODEL=openai:gpt-6-luna và OPENAI_API_KEY:

```powershell
docker run --rm -v "${PWD}:/lab" -w /lab lab-deepagents-verify python -m pytest tests report/test_runtime_fixes.py
docker run --rm --env-file .env -v "${PWD}:/lab" -w /lab lab-deepagents-verify python report/run_luna.py --tasks learn --results results/luna-followup
```

Script từ chối ghi đè kết quả đã tồn tại. Các lệnh gọi model có tốn API token.
Đổi model trên giao diện Codex không thay model của lab; lab đọc `.env`.

Tài liệu tương thích: [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna).
Bước tiếp theo cần một thí nghiệm mới, được ghi nhận riêng, để curator cung cấp đầy đủ
skill reporting dữ liệu rồi kiểm chứng cả ba điều kiện trên eval; chưa thực hiện bước đó.
