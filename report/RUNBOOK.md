# Tái lập lab sau setup môi trường

Chạy từ PowerShell tại gốc repository. Docker Desktop cần chạy Linux containers.
File `.env` dùng `LAB_MODEL=openai:gpt-4o-mini`, `OPENAI_API_KEY` và `LAB_TEMPERATURE=0`;
để trống ba biến Azure khi dùng cấu hình này. Không đưa `.env` lên git.

```powershell
docker build -t lab-deepagents .
docker run --rm -v "${PWD}:/lab" lab-deepagents python -m pytest tests
docker run --rm -v "${PWD}:/lab" lab-deepagents python scripts/tour.py
```

Test dùng mô hình giả và không tốn API token. Các lệnh sau có gọi API; chạy tuần tự.
Giới hạn đệ quy 40 được dùng thống nhất cho thí nghiệm mới.
Mỗi lượt tạo sandbox Linux riêng ngoài repository và chỉ sao chép workspace gốc vào đó.

```powershell
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents python -m lab.runner --condition baseline --tasks data-learn --recursion-limit 40
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents python -m lab.runner --condition baseline --tasks code-learn logs-learn --recursion-limit 40
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents python -m lab.runner --condition subagents --tasks learn --recursion-limit 40
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents python -m lab.curator
```

Đọc từng skill do curator sinh, đánh giá tính đúng/tổng quát, ghi nhận trong báo cáo.
Không sửa nội dung `skills/auto/` bằng tay. Sau đó chạy kiểm tra trên tập học:

```powershell
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents python -m lab.runner --condition skills-auto --tasks learn --recursion-limit 40
Move-Item -LiteralPath results/skills-auto -Destination results/skills-auto-dev
```

Điền H1–H3 vào báo cáo trước khi đọc kết quả eval. Commit đúng phạm vi bài lab:

```powershell
git add -- src/lab/agent.py src/lab/subagents.py src/lab/runner.py src/lab/curator.py report results skills/auto
git commit -m "hypotheses"
git commit --allow-empty -m "freeze skills"
git tag freeze
```

Chỉ thực hiện freeze một lần cho thí nghiệm chính; không thay tag sau khi đã có điểm eval.

```powershell
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents python -m lab.runner --condition baseline --tasks eval --recursion-limit 40
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents python -m lab.runner --condition subagents --tasks eval --recursion-limit 40
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents python -m lab.runner --condition skills-auto --tasks all --recursion-limit 40
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents python report/retry_failed.py
docker build -t lab-deepagents-verify -f report/Dockerfile.verify .
docker run --rm -v "${PWD}:/lab" lab-deepagents-verify python scripts/verify_freeze.py
docker run --rm -v "${PWD}:/lab" lab-deepagents-verify python -m lab.compare
docker run --rm -v "${PWD}:/lab" lab-deepagents-verify python scripts/check_breakdown.py
docker run --rm -v "${PWD}:/lab" lab-deepagents-verify python report/verify_submission.py
```

Hoàn thiện báo cáo dựa trên số liệu thật. Bảng so sánh lấy từ `lab.compare`.
Chạy verify_freeze trong Linux, cùng hệ điều hành của runner: hash_dir/hash_skills có dùng
chuỗi đường dẫn tương đối, nên dấu phân cách Windows/Linux ảnh hưởng hash.
Lượt cũ trước khi bắt đầu lại nằm ở `results/previous-attempt/` và không tham gia bảng chính.
Nếu chạy lại một lượt lỗi, giữ bản lỗi trong thư mục lưu trữ và ghi lý do/tham số trong báo cáo.
Trong lần nộp này, mỗi lượt có error được chạy lại đúng một lần, cùng limit 40;
script retry_failed.py lưu lượt đầu ở results/official-first-pass và log ở results/retry-log.json.
Không chạy lại script này trên bộ kết quả đã có archive trùng tên: nó từ chối ghi đè archive.
