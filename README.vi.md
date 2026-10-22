# OTTPlay dành cho Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[Kiến trúc](docs/architecture.md) · [Bảo mật](SECURITY.md) · [Đóng góp](CONTRIBUTING.md)

Điều khiển các trình phát OTTPlay đã đăng ký từ Home Assistant thông qua [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server) hiện có. Một kết nối cung cấp cho mỗi trình phát một thực thể `media_player` và một thực thể `remote`. TV chủ động gửi yêu cầu đến bộ điều khiển; Home Assistant không cần cổng lắng nghe trên TV, máy chủ trung gian MQTT hay một tiến trình cầu nối thứ hai.

![Cách hoạt động](docs/diagrams/architecture.svg)

## Các tính năng

- Đọc trạng thái phát từ trình phát đang chạy, đánh dấu rõ những thiết bị không khả dụng.
- Phát/tạm dừng, kênh trước/tiếp theo, tua đến vị trí và điều chỉnh âm lượng nếu trình phát hỗ trợ.
- Chọn kênh theo số hoặc tên qua `media_player.play_media`.
- Điều hướng qua `remote.send_command`: phím mũi tên, OK, Quay lại và các phím được hỗ trợ khác.
- Cấu hình qua giao diện, thay thông tin xác thực, bản dịch giao diện tiếng Anh/tiếng Nga và dữ liệu chẩn đoán đã che thông tin nhạy cảm.
- Định danh thực thể ổn định, kể cả khi trình phát khởi động lại.

Khả năng hỗ trợ tùy thuộc vào bản dựng trình phát, chế độ phát và kết nối. Không cung cấp nút dừng và nút nguồn phần cứng: chờ/đánh thức có thể mang ý nghĩa khác nhau trên từng trình phát và không được dùng thay cho dừng/tiếp tục phát. Tích hợp không tự tạo ra tên nội dung hiện tại, ảnh minh họa hay trạng thái nguồn phần cứng. Xác nhận từ bộ điều khiển chỉ có nghĩa là bộ xử lý đã trả lời; không chứng minh được hình ảnh đang hiển thị hay âm thanh có thể nghe thấy. Trạng thái được lấy từ lần đọc tiếp theo.

## Cài đặt

Yêu cầu **Home Assistant 2026.10.0 trở lên**, cùng OTTPlay Control Server và trình phát phiên bản hiện hành có hỗ trợ API yêu cầu/phản hồi. Đây là tích hợp tùy chỉnh, không thuộc Home Assistant Core và không phải kho mặc định của HACS.

**HACS:** thêm `ha-homelab/ha-ottplay` làm kho tùy chỉnh loại **Integration**, cài **OTTPlay**, rồi khởi động lại Home Assistant. Bật bản phát hành thử trong HACS khi cài phiên bản beta.

**Thủ công:** tải `ha-ottplay.zip` từ [bản phát hành](https://github.com/ha-homelab/ha-ottplay/releases), xác minh tổng kiểm tra, rồi giải nén thư mục `custom_components/ottplay` bên trong vào thư mục cấu hình HA. Giữ nguyên các tệp HA hiện có. Khởi động lại Home Assistant.

Vào **Cài đặt → Thiết bị & dịch vụ → Thêm tích hợp → OTTPlay**. Sử dụng URL mà chính Home Assistant có thể truy cập, bao gồm cả tiền tố đường dẫn của bộ điều khiển nếu có. Ví dụ: `https://controller.example.net/ott-control`.

Có hai chế độ cấp quyền:

1. **Người vận hành có quyền hạn chế (khuyến nghị):** sử dụng token riêng cho người vận hành lệnh và liệt kê các ID trình phát mà token đó được phép truy cập trong biểu mẫu cấu hình. Lấy ID bằng `ott devices`. Đăng ký trình phát mới không tự động mở rộng quyền này; hãy chủ động cập nhật quyền trên máy chủ và cấu hình tích hợp.
2. **Danh mục tự động:** để trống ID trình phát và sử dụng token quản trị viên máy chủ. Tích hợp đọc danh mục đăng ký của máy chủ và phát hiện thiết bị mới. Thông tin xác thực này cấp quyền truy cập rộng hơn nhiều. Chỉ sử dụng với một phiên bản HA đáng tin cậy.

Không thể dùng token thiết bị hoặc token người vận hành chỉ dành cho chẩn đoán ở đây. Xem [cấu hình và quyền hạn](docs/configuration.md).

## Dùng trong tự động hóa

```yaml
action: media_player.play_media
target:
  entity_id: media_player.ottplay_living_room
data:
  media_content_type: channel
  media_content_id: "12"
```

```yaml
action: remote.send_command
target:
  entity_id: remote.ottplay_living_room
data:
  command: [ok, down, back]
```

Thay ID thực thể trong ví dụ bằng các ID đã được tạo trên hệ thống của bạn. Việc chọn kênh sử dụng nhà cung cấp hiện tại của trình phát; không tải lên URL phương tiện tùy ý. Cấu hình không bắt đầu phát hoặc điều khiển nguồn vật lý của TV.

## Phát triển và phát hành

Dùng Python 3.14 và `uv sync --locked`, sau đó chạy `uv run pytest -q`, `uv run ruff check .` và `uv run ruff format --check .`. Các bài kiểm thử kiểm tra lỗi giao thức, thông tin xác thực, vòng đời và các dịch vụ thực thể HA thực tế mà không kết nối với thiết bị trong nhà. Xem [quy trình phát hành](docs/releasing.md).

Cài đặt kho công khai được quản lý bằng [Terraform](https://github.com/4alvit/terraform-github-ha-homelab). CI sử dụng các quy trình dùng chung được ghim vào bản sửa đổi cụ thể từ [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit).
