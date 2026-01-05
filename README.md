# ThingsBoard + MQTT Integration
## 1. Cài đặt ThingsBoard cho Window như hướng dẫn trong tài liệu:
https://thingsboard.io/docs/user-guide/install/docker-windows/

#### Thêm cấu hình cho file yml:
services:
  postgres:
    restart: always
    image: "postgres:16"
    ports:
      - "5432"
    environment:
      POSTGRES_DB: thingsboard
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data
  thingsboard-ce:
    restart: always
    image: "thingsboard/tb-node:4.2.1.1"
    ports:
      - "8080:8080"
      - "7070:7070"
      - "1883:1883"
      - "8883:8883"
      - "5683-5688:5683-5688/udp"
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "10"
    environment:
      TB_SERVICE_ID: tb-ce-node
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/thingsboard
    depends_on:
      - postgres

volumes:
  postgres-data:
    name: tb-postgres-data
    driver: local

#### Tạo database schema và tải built-in assets bằng cách chạy lệnh: 
docker compose run --rm -e INSTALL_TB=true -e LOAD_DEMO=true thingsboard-ce

#### Khởi tạo và chạy các container được định nghĩa trong tệp docker-compose.yml, hiển thị logs: 
docker compose up -d; docker compose logs -f thingsboard-ce

#### Đăng nhập bằng tài khoản tenant (hoặc 2 loại tài khoản khác): 
tenant@thingsboard.org (username or email) / tenant (password)

## 2. Hướng dẫn chạy demo
#### Đối với DIFP-33:
- Khi chạy ThingsBoard lần đầu sẽ có sẵn Root Rule Chain nên không cần cấu hình Rule nữa
- Code chính sẽ bao gồm: thingsboard.py, mqtt_devices.py, simulator.py và script.py
- Mock data: devices.csv
- Run code: python script.py
- Log CLI ở DIFP-33 sẽ hiển thị quá trình kết nối, gửi telemetry data đến các device và sẽ hiển thị các lần mô phỏng dữ liệu gửi liên tục (file simulator) lên ThingsBoard
- Ở ThingsBoard UI: vào Entities => Deivces, click vào từng thành phần sẽ thấy được Attributes và Latest telemetry được đẩy lên từ script.
- Báo cáo kết quả: https://docs.google.com/document/d/1UWHT9UqAFkYXJtqyWry9rfz9KIOSRy0RiOpW2T8rbSs/edit?usp=sharing
#### Đối với DIFP-38:
- Mock data: devices.csv, mock_data.csv
- Trước tiên sẽ tạo Device Profile trên ThingsBoard UI, gồm: HeartRate_DeviceProfile và Temperature_DeviceProfile
- Import Rule Chain: các Rule cần thiết nằm trong thư mục "rule chain", tương ứng:
+ Root Rule Chain: root_rule_chain.json
+ Custom Rule Chain: heart_rate_rule.json và temperature.json
- Sau khi import thành công, click vào từng Rule đã import sẽ thấy được giao diện trực quan của các rule
- Run code: python script.py
- Log CLI: sẽ thấy tương tự như DIFP-33 (log này sạch hơn 1 tí vì có chỉnh sửa lại cách thể hiện dữ liệu)
- Ở ThingsBoard UI: vào Entities => Deivces, click vào từng thành phần sẽ thấy được Attributes và Latest telemetry được đẩy lên từ script. Click vào Alarms sẽ thấy được các cảnh báo CRITICAL của 3 device. Để xem được Time series data của các device, thì click vào Dashboard và import file difp-38.json thuộc thư mục "DIFP-38/dashboard", khi chạy lại script sẽ thấy được data được cập nhật real time.
- Báo cáo kết quả: https://docs.google.com/document/d/1nbYgu2jjI0RHNFYvhYKbDBk6RLhW4iF0g6rHXe-m5tg/edit?usp=sharing
#### Đối với DIFP-42:
- Mock data: tenants.csv, tenants_admin.csv, customers.csv, customer_user.csv, devices.csv
- File thingsboard.py được thiết kế với đầy đủ các chức năng hơn những DIFP lần trước, với các chức năng được thiết kế cho cả 3 role: System Admin, Tenant Admin và Customer User
- Sử dụng ThingsBoard UI đăng nhập với tài khoản System Admin để tạo Tenant và Tenant Profile. (Nếu dùng cách gửi mail thì phải kích hoạt Mail Server, bằng cách tạo mật khẩu ứng dụng của Google, dùng mật khẩu này set cho phần Password của thiết lập Mail Server trong Settings)
- Sử dụng UI ThingsBoard, đăng nhập tài khoản Tenant Admin => Tạo Customer
- File script.py chứa kịch bản theo thứ tự: 
Đăng nhập với tài khoản System Admin => Tạo tài khoản Tenant Admin
Đăng nhập với tài khoản Tenant Admin => Tạo tài khoản Customer User => Thêm Device => Gán Device và Dashboard cho Customer User
File này còn sẽ gửi telemetry data chứa dữ liệu heart_rate và temperature lên ThingsBoard UI
- Báo cáo kết quả: https://docs.google.com/document/d/1h7T3HvBCgEetfzYFXsar91N7VAgbacrUr30ri9ULpes/edit?usp=sharing