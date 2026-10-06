# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Lê Quang Ngọc | 2A202602664 | Cài đặt harness, thực nghiệm và phân tích báo cáo |

- Mô hình: `openai:gpt-4o-mini`; nhiệt độ 0; recursion limit 40 thống nhất cho thí nghiệm mới. Runner streaming giữ trace cuối khi gặp lỗi (mở rộng được phép trong pseudo-code 03).
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: Deep Agents 0.7.21; Python 3.12.15; Windows host; chạy agent trong Docker Linux.
- Số lần chạy tác vụ đã dùng / ngân sách: 18 kết quả chính + 3 development + 5 lượt lỗi đầu được lưu trước retry = 26 lượt mới; thêm 5 lượt cũ được lưu riêng, tổng 31 bản ghi. Tổng token ghi nhận 2.497.724, không gồm curator/kiểm tra kết nối/lượt bị ngắt không có bản ghi; đây không phải tổng hóa đơn API. Curator gọi 3 lần. Người dùng không đặt ngân sách số token cụ thể.
- Commit của tag `freeze`: `6e6014e22de04ae977f4f84ec0d25b9b25f3c94f`; hypotheses ở `6379aee` trước freeze. Không đổi skill sau tag.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Dự đoán subagents không cải thiện đồng đều điểm eval; token có thể tăng khi thực sự giao việc. Learning code-learn đạt 3/10 so với baseline 4/10 và không gọi subagent. Căn cứ: GUIDE 2.3 và pseudo-code 02 về chi phí và cô lập ngữ cảnh.
- H2 (skills-auto so với baseline): Dự đoán skill giúp một phần check quy ước lặp lại nhưng không bảo đảm sửa lỗi tính toán hoặc cải thiện mọi tác vụ. Baseline learning bỏ sót cả 9 check rule_. Căn cứ: pseudo-code 04/05 về SkillsBench và việc đọc/làm theo skill.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán cải thiện learning lớn hơn eval vì curator chỉ thấy learning feedback còn eval có quy ước mới; chênh lệch nhỏ có thể là nhiễu. Căn cứ: README 2.2 và nhận xét SkillEvolBench trong pseudo-code 04.

Giả thuyết được viết trước khi chạy/đọc điểm eval. Đề eval Markdown từng được đọc khi lập checklist đầu phiên; hạn chế này được công khai ở mục 9. Curator không nhận đề hay kết quả eval.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có các công cụ tệp `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`; công cụ shell `execute`; và công cụ subagent `task`. Công cụ `execute` cho phép chạy lệnh.
2. `general-purpose` dùng cho nghiên cứu câu hỏi phức tạp, tìm kiếm tệp/nội dung và tác vụ nhiều bước, có cùng công cụ với tác tử chính. Mỗi lần gọi mặc định là độc lập: subagent chỉ thấy prompt được giao và trả về một báo cáo cuối, nên prompt phải chứa đủ ngữ cảnh.
3. Từ `task`: “Each invocation is stateless by default: the agent sees only the prompt you give it”. Từ `execute`: “You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search.”

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng từ detail/vết |
|---|---|---|---|
| code-learn | parse_price_all_formats | B | wrong for: ['(12.00)'] |
| code-learn | csv_quoting_follows_docstring | B | to_csv_row returned 'Desk, large "oak",10.00,2' |
| code-learn | rule_type_hints | E | RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value. |
| code-learn | rule_regression_tests | E | RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass. |
| code-learn | rule_changelog | E | RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets). |
| data-learn | north_q1_revenue | B | north_q1_revenue: wrong value (got 0.0) |
| data-learn | north_q1_orders | B | north_q1_orders: wrong value (got 0) |
| data-learn | top_region | B | top_region: wrong value (got 'South') |
| data-learn | missing_amount_orders | B | missing_amount_orders: wrong value (got 12) |
| data-learn | duplicate_rows_removed | B | duplicate_rows_removed: wrong value (got 8) |
| data-learn | rule_money_in_cents | E | RULE: money values in answer.json are integer cents (1606.67 USD is written 160667). |
| data-learn | rule_meta_block | E | RULE: answer.json has an object `meta` = {"source": <input file name>, "rows_in": <number of data rows in the input file, duplicates included>, "rows_used": <number of distinct orders with a known amount>}. |
| data-learn | rule_clean_csv | E | RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row per distinct order with a known amount; timestamp_utc as YYYY-MM-DDTHH:MM:SSZ (UTC); region in canonical spelling (North, South, East, West); amount in integer cents. |
| logs-learn | entry_count | B | wrong number of entries (got 34) |
| logs-learn | timestamps_utc | D | 0/25 timestamps match |
| logs-learn | exception_fields | D | 25 wrong `exception` values |
| logs-learn | repeat_counts | D | 25 wrong `repeat_count` values |
| logs-learn | counts_by_service | D | counts_by_service: wrong values |
| logs-learn | rule_service_names | E | RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service). |
| logs-learn | rule_sorted_errors | E | RULE: `errors` is sorted by service, then by timestamp_utc, ascending. |
| logs-learn | rule_schema_header | E | RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage". |

Nhóm lớn nhất là E (9 check), tiếp theo B (8) và D (4). Skill có thể cung cấp quy ước và nhắc kiểm chứng, nhưng không tự bảo đảm việc tính toán đúng.

Trong trace baseline data-learn, hai lệnh tính toán thất bại (SyntaxError, thiếu pandas), sau đó agent ghi các số trực tiếp mà không có phép tính thành công (B). logs-learn chỉ đọc log và ghi JSON bằng tay, không chạy parser/đối chiếu; dữ liệu thời gian, traceback và dòng lặp đều sai (D). code-learn đã đọc docstring nhưng chỉ chạy visible tests, không kiểm tra đầy đủ ví dụ/CSV escaping (B). Không có bằng chứng chắc chắn để quy thêm lỗi vào A, C hoặc F theo định nghĩa GUIDE.

Loại khỏi bảng hành vi agent: tests_not_modified của code-learn thất bại do CRLF Windows. SHA256 CRLF `efb5e7650d4f03356e8353d209fbcfe81505ce2fd648bd558d5ada6e8b92ff19`; SHA256 sau chuẩn hóa LF `79e05f4cc2e62a4f606d210b0b08a2cc21777245bc2f6ad244a126e9a2aee00d` trùng checker. Không sửa test gốc hoặc điều chỉnh điểm. Lỗi môi trường không được dùng làm bằng chứng taxonomy.

Baseline đạt 5/18 check kỹ thuật và 0/9 check quy ước. Kết quả không ủng hộ giả định model này làm đúng phần lớn yêu cầu kỹ thuật: data 0/5, code 4/7, logs 1/6. Một check kỹ thuật code bị ảnh hưởng bởi CRLF như đã nêu.

## 5. Điều kiện `subagents` (Phần 2.3)

- Vai trò: explorer khảo sát chỉ đọc; implementer thực hiện và kiểm chứng; reviewer đánh giá độc lập chỉ đọc. Description nêu thời điểm sử dụng; PATHS_NOTE được nối vào từng prompt. Subagent được hướng dẫn tự thực hiện và trả một báo cáo cuối.

| Learning task | task calls | Token | Giây | Điểm |
|---|---|---|---|---|
| code-learn | 0 | 43964 | 22.6 | 3/10 |
| data-learn | 1 | 61244 | 113.7 | 1/8 |
| logs-learn | 0 | 29620 | 221.9 | 0/9 |

code-learn và logs-learn không gọi subagent: trace cho thấy tác tử tự đọc/làm việc, dù có mô tả khuyến khích. Đây là hành vi quan sát được, không chứng minh chắc chắn nguyên nhân lựa chọn. logs-learn đọc hai phần log rồi kết thúc với final_message rỗng; errors.json không tồn tại, cả 9 check trượt, không có error API được ghi.

data-learn gọi implementer 1 lần sau hai lệnh Python thất bại. Lời giao việc có input/output path và tên metric, nhưng không nêu rõ ranh giới UTC tới 23:59:59, sentinel -999 hoặc quy tắc loại missing khỏi doanh thu. Tác tử chính dùng ngay báo cáo mà không có read_file/test xác nhận sau đó. Duplicate count đạt nhưng các số khác sai, cho thấy giao việc thiếu thông tin và thiếu kiểm chứng.

Baseline learning dùng trung bình 33.702 token; subagents dùng 44.942 token (tăng khoảng 33,35%). Thời gian trung bình tương ứng 22,97 và 119,4 giây. Điểm learning trung bình giảm từ 0,1704 xuống 0,1417; thí nghiệm này chưa cho thấy lợi ích đa tác tử. Chi phí token gồm cả implementer, trace/tool_calls chỉ luồng chính.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Curator chạy 3 lần (1 lần đầu + 2 lần chạy lại, đúng giới hạn GUIDE); 8 bản skill bị loại, còn 1 skill. Các bản bị loại lưu nguyên văn tại results/curator-attempt-1, curator-attempt-2 và curator-attempt-3-rejected.
- Lần 1: standardize-data-formatting mở rộng dấu '-' thành mọi ký tự đặc biệt, timezone chỉ định dạng; bộ 3 skill thiếu quy trình miền nên loại cả bộ và làm rõ prompt.
- Lần 2: bộ 3 skill vẫn chứa mức log/identifier/sentinel/input-format cụ thể của learning, và thiếu giá trị schema/metadata. Loại cả bộ; bổ sung prompt yêu cầu đọc đặc tả mới và bảo toàn chính xác quy ước.
- Lần 3: loại log-triage vì cố định ERROR/CRITICAL; loại tabular-analysis vì giả định CSV và thiếu meta/chi tiết làm sạch. Giữ code-repair. Nội dung của mọi skill đều là output curator, không sửa tay.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| code-repair | Quy trình bảo toàn tests, type hints, regression tests và changelog; không có id task hoặc đáp án. Có thiên hướng parsing giá tiền nhưng áp dụng được tác vụ mới cùng loại. | Không thấy chỉ dẫn gây hại; giữ tests gốc, thêm test mới và xử lý docstring. Thiếu lệnh chạy test cuối và số lượng tối thiểu test/bullet, nên chưa đủ mọi check. | 10 dòng tổng, 6 dòng body; description kích hoạt khi sửa code. skills_read development bằng 0 ở cả ba tác vụ. |

Development: code-learn 3/10 (47.456 token), data-learn 0/8 (198.550 token, GraphRecursionError ở limit 40), logs-learn 0/9 (23.776 token). Không lượt nào đọc skill; trace code bắt đầu glob workspace, không read_file skills. Kết quả đã lưu nguyên vẹn ở results/skills-auto-dev để so với lần chạy sau freeze. Không chạy curator thêm vì đã hết hai lần chạy lại được phép.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 4/10 | 3/10 | 2/10 |
| data-learn | 0/8 | 1/8 | 0/8 |
| logs-learn | 1/9 | 0/9 | 0/9 |
| code-eval | 1/11 | 1/11 | 2/11 |
| data-eval | 0/9 | 1/9 | 3/9 |
| logs-eval | 1/10 | 1/10 | 1/10 |
| **Mean score - learning tasks** | 0.17 | 0.14 | 0.07 |
| **Mean score - evaluation tasks** | 0.06 | 0.10 | 0.21 |
| **Mean tokens per run** | 46,204 | 57,093 | 60,419 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

Phân rã check (output scripts/check_breakdown.py, bỏ khoảng trắng cuối dòng):

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval      2/18         0/12          58,707      0/3
baseline      learn     5/18         0/9           33,702      0/3
subagents     eval      3/18         0/12          69,244      0/3
subagents     learn     4/18         0/9           44,942      0/3
skills-auto   eval      6/18         0/12          30,422      0/3
skills-auto   learn     2/18         0/9           90,416      0/3
```

Có 5 lượt chính đầu gặp GraphRecursionError, mỗi lượt được retry đúng một lần với cùng model, nhiệt độ và limit 40. Bảng chính dùng lượt retry, không chọn lượt điểm cao nhất; bản đầu giữ ở results/official-first-pass và log đầy đủ ở results/retry-log.json.

| Điều kiện / task | Điểm lượt đầu → retry | Lỗi sau retry |
|---|---|---|
| baseline / code-eval | 1/11 → 1/11 | GraphRecursionError (40) |
| baseline / data-eval | 0/9 → 0/9 | Không |
| subagents / code-eval | 1/11 → 1/11 | Không |
| skills-auto / code-eval | 0/11 → 2/11 | Không |
| skills-auto / data-learn | 0/8 → 0/8 | GraphRecursionError (40) |

Không tăng limit và không retry tiếp để tránh chi phí/vòng lặp không giới hạn. Hai lỗi còn lại được giữ nguyên trong kết quả; không khẳng định agent đã hoàn thành các task đó. Development data-learn cũng có lỗi, được giữ nguyên để đánh giá nhiễu, không dùng thay kết quả chính. Tất cả 18 lượt chính có skills_modified=false; verify_freeze: checked 6 runs of skill conditions: OK. Test harness: 29 passed. Kiểm tra bổ sung: protected code unchanged, 1 valid skill, 18 complete official runs, no API key pattern found. “Complete official runs” nghĩa là đủ bản ghi/trace/check cho 18 ô, không có nghĩa mọi tác vụ đạt điểm tối đa.

## 8. Phân tích

1. Learning: baseline 0,1704, subagents 0,1417, skills-auto 0,0667; không điều kiện nào cải thiện. Eval: baseline 0,0636, subagents 0,1007, skills-auto 0,2051; tăng tương ứng 0,0370 và 0,1414. Không có mẫu “learning tăng nhưng eval không tăng”; kết quả ngược H3, H1 chỉ được ủng hộ một phần (không tăng đồng đều). Điểm eval cao hơn không chứng minh tác dụng skill vì không lượt nào đọc skill và retry có thay đổi điểm code-eval.
2. Learning kỹ thuật: baseline 5/18, subagents 4/18, skills-auto 2/18; eval: 2/18, 3/18, 6/18. Quy ước đều 0/9 learning và 0/12 eval. Không có bằng chứng hỗ trợ H2. Ba rule mới rule_version_bump, rule_sorted_keys_format và rule_source_line đều không đạt; code-repair không chứa chúng và không được đọc. Học quy ước cũ không tự suy ra quy ước mới.
3. Không thể đưa ra một check được **skill giúp đạt** một cách trung thực: skills_read=0 ở cả 6 lượt chính. Ví dụ tương quan: parse_price_all_formats ở skills-auto/code-learn đạt trong khi baseline trượt, phù hợp mục xử lý accounting trong skill; nhưng trace không read_file skill, nên không quy kết nhân quả. rule_type_hints vẫn trượt dù skill nhắc rõ, thuộc trường hợp skill chưa được đọc. Trace data-eval tính bằng Python chuẩn đạt top_category, missing_total_orders, duplicate_events_removed, nhưng không chuyển timestamp sang UTC trước lọc tháng nên các metric tháng sai; đây là hành vi thực thi, không phải bằng chứng skill được áp dụng.
4. Token trung bình trên 6 lượt: baseline 46.204,7; subagents 57.093,5 (+23,57%); skills-auto 60.419,3 (+30,76%). Chỉ số mean score / mean tokens × 1.000.000 lần lượt 2,532; 2,122; 2,249: baseline tốt nhất theo định nghĩa này trên toàn bộ task. Riêng eval, skills-auto có mean score cao nhất và mean tokens thấp nhất (30.422), nhưng không đủ bằng chứng nhân quả. Chi phí đa tác tử chưa được bù bằng cải thiện ổn định trong mẫu này; vòng lặp/lượt lỗi ảnh hưởng mạnh token. Bảng trung bình không gồm chi phí lượt đầu đã archive; tổng token ghi nhận ở mục 1 có gồm chúng.
5. Curator chỉ nhận learning feedback và trace; skill cuối không có đáp án hoặc id task eval, không chỉnh tay và không đổi sau freeze. Tám bản bị loại vì hướng dẫn sai/thiếu hoặc cố định định dạng, sentinel, mức log của learning; bản cuối vẫn thiên về giá tiền nên có nguy cơ quá khớp miền. Đề eval Markdown từng được đọc khi lập checklist là hạn chế thực tế, không che giấu; việc không đưa eval vào curator và đóng băng trước khi chấm chỉ giảm, không xóa hạn chế này.
6. Cùng skill: development code-learn 3/10 → sau freeze 2/10; data-learn 0/8 → 0/8; logs-learn 0/9 → 0/9. Mean learning 0,1000 → 0,0667, giảm 0,0333. Hash skill không đổi; dao động ít nhất một check code là bằng chứng không nên diễn giải mọi chênh lệch nhỏ như cải tiến. Hai lượt data đều chạm limit (lượt chính đã retry), nên đây không phải ước lượng nhiễu thuần hay độ tin cậy thống kê.

## 9. Hạn chế và tính hợp lệ

1. Chỉ ba tác vụ mỗi vai trò, một lượt chính cho mỗi cấu hình: trung bình dễ bị chi phối bởi một bài; nhiệt độ 0 không loại bỏ nhiễu. Lặp learning với cùng skill chỉ cho dao động quan sát được, không phải khoảng tin cậy thống kê.
2. Chỉ một model gpt-4o-mini và giới hạn 40: kết luận không suy rộng sang model mạnh hơn hoặc ngân sách lớn hơn. Trace chỉ có luồng chính và mỗi khối bị cắt ở 1.500 ký tự; token có gồm subagent nhưng tool calls không gồm luồng bên trong.
3. Checkout Windows có CRLF gây false negative ở check tests_not_modified của code-learn. Hash LF trùng checker nhưng hash CRLF khác; giữ nguyên điểm gốc và không coi đây là lỗi agent sửa test.
4. Đề eval Markdown đã được đọc trong bước lập checklist trước đây, nên người hỗ trợ không hoàn toàn mù với họ tác vụ. Chưa đọc điểm/checker/đáp án eval trước freeze; curator chỉ dùng learning feedback, skill không sửa thủ công. Phải thận trọng khi diễn giải tổng quát hóa.

## 10. Kết luận

Trong mẫu này, skills-auto có điểm eval cao nhất (0,2051), nhưng mọi lượt đều không đọc skill nên chưa chứng minh lợi ích self-evolving. Subagents tăng nhẹ điểm eval nhưng giảm learning và tăng token trung bình 23,57%. Cả ba điều kiện không đạt check quy ước nào, và hai kết quả chính vẫn chạm limit sau retry. Bước tiếp theo là thiết kế một thí nghiệm mới kiểm tra trigger đọc skill, đối chiếu một model mạnh hơn và lặp nhiều lượt với ngân sách cố định; không sửa bộ skill đã freeze của thí nghiệm này.

## Phụ lục

- Lệnh đã chạy (theo thứ tự): xem [RUNBOOK.md](RUNBOOK.md). Kết quả cũ nằm ở results/previous-attempt; không tham gia bảng chính mới.
- Không thực hiện thử thách mở rộng ngoài phạm vi bắt buộc.
- Checklist bàn giao: hoàn thiện TODO harness; test 29/29; curator và development có archive; hypotheses trước freeze; đủ 18 ô chính; xác minh freeze; bảng và phân rã check; báo cáo 10 mục. Test/checker/task gốc không thay đổi. Hai lỗi runtime còn lại được công khai ở mục 7.
