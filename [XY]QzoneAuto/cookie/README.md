# QQ获取COOKIE项目 API文档

本项目支持通过API方式为机器人或其他程序提供QQ扫码登录服务，适合多用户并发，每个QQ号独立二维码。

---

## 项目简介

- 支持QQ扫码/密码登录，获取SKEY、PSKEY、superkey等关键凭证。
- 提供标准API接口，适合机器人、网站、APP等多端集成。
- 支持多用户并发，每个QQ号二维码、登录状态互不干扰。
- 提供网页登录和扫码两种方式，灵活适配不同场景。

---

## 快速开始

1. 部署本项目到支持PHP的服务器。
2. 通过API获取二维码，展示给用户扫码。
3. 轮询API获取扫码及登录结果，获取到key后完成业务逻辑。
4. 可选：直接跳转web_login_url让用户网页登录。

---

## 1. 获取专属二维码

**接口地址**：`login.php?do=apigetqrpic`

**请求方式**：GET 或 POST

**参数：**
- `uin` (string/int) 需要登录的QQ号

**返回：**
- `saveOK` (int) 0为成功，非0为失败
- `msg` (string) 提示信息
- `token` (string) 本次登录唯一标识，后续查询用
- `qrcode` (string) base64格式的二维码图片（data:image/png;base64,...）
- `qrcode_url` (string) 二维码图片直链，可直接访问
- `web_login_url` (string) 网页网页登录地址，用户可手动网页登录

**示例：**
```
GET login.php?do=apigetqrpic&uin=123456789
```
**返回：**
```
{
  "saveOK": 0,
  "msg": "二维码获取成功",
  "token": "xxxxxx",
  "qrcode": "data:image/png;base64,xxxx...",
  "qrcode_url": "https://yourdomain.com/cookie/login.php?do=apigetqrimg&token=xxxxxx",
  "web_login_url": "https://yourdomain.com/cookie/index2.html?token=xxxxxx"
}
```

---

## 1.1 获取二维码图片直链

**接口地址**：`login.php?do=apigetqrimg&token=xxxxxx`

**请求方式**：GET

**参数：**
- `token` (string) 上一步返回的token

**返回：**
- Content-Type: image/png
- 直接输出二维码图片

**示例：**
```
<img src="https://yourdomain.com/cookie/login.php?do=apigetqrimg&token=xxxxxx" />
```

---

## 1.2 网页网页登录地址

**接口返回字段**：`web_login_url`

**说明**：
- 用户可直接访问该地址，进入网页登录页面，扫码或手动操作完成登录。
- 适合不方便扫码的场景，或直接在浏览器操作。

---

## 2. 查询扫码及登录结果

**接口地址**：`login.php?do=apigetresult`

**请求方式**：GET 或 POST

**参数：**
- `token` (string) 上一步返回的token

**返回：**
- `saveOK` (int)
    - 0 登录成功
    - 1 二维码失效
    - 2 请使用QQ手机版扫描二维码
    - 3 已扫码，等待手机确认
    - -1 token无效
    - 其它为错误
- `msg` (string) 提示信息
- `uin` (string) QQ号（登录成功时）
- `keys` (object) 登录成功时返回，包含：
    - `uin` QQ号
    - `nick` QQ昵称
    - `skey` SKEY
    - `pskey` PSKEY
    - `superkey` superkey

**示例：**
```
GET login.php?do=apigetresult&token=xxxxxx
```
**返回：**
```
{
  "saveOK": 0,
  "msg": "登录成功",
  "uin": "123456789",
  "keys": {
    "uin": "123456789",
    "nick": "昵称",
    "skey": "xxxx",
    "pskey": "xxxx",
    "superkey": "xxxx"
  }
}
```

---

## 3. 典型流程

1. 机器人提交QQ号，获取二维码和token。
2. 用户扫码，机器人定时轮询apigetresult接口，直到登录成功或二维码失效。
3. 登录成功后获取到各类key。
4. 也可直接跳转web_login_url网页登录。

---

## 4. 常见问题

- Q: token 有效期多久？
  - A: 默认跟随PHP session有效期，建议自行定期清理或用数据库存储。
- Q: 二维码多久失效？
  - A: 一般3分钟左右，失效后需重新获取。
- Q: 支持多用户并发吗？
  - A: 支持，每个token、二维码、登录状态互不影响。
- Q: 支持哪些平台？
  - A: 只要能发起HTTP请求即可，常见如Python、Node.js、PHP、Shell等。

---

## 5. 接口安全建议

- 建议为API增加访问白名单或鉴权，防止被恶意刷接口。
- 生产环境建议用数据库存储token及状态，便于扩展和管理。
- 建议全站启用HTTPS，保护用户数据安全。

---

## 6. 联系方式

- 作者博客：[xun.eynet.top](https://xun.eynet.top)
- 如有问题请在博客留言或通过项目页联系。

---
