# Qliqy Mailer Service

![CI](https://github.com/QliqyService/mailer/actions/workflows/mail-build.yml/badge.svg)
![Status](https://img.shields.io/badge/status-active%20development-b4492f)

Email notification worker for Qliqy.

## What It Does

- receives notification events from `webapi`
- builds outbound email messages
- delivers comment notifications to configured user email addresses

## How It Works

When a public comment is created, `webapi` publishes an event through RabbitMQ. If email notifications are enabled for the owner, `mailer` processes that event and sends the email notification.

## Product Note

Public registration is intentionally disabled while the product is still being validated.

Test account:

```json
{
  "email": "admin@admin.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "admin123"
}
```

- Developer: Ilia Fedorenko
- Developer: Ernest Berezin
