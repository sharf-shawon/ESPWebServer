# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.x     | ✅        |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Email: security@espwebdeployer.dev (or open a [private security advisory](https://github.com/sharf-shawon/ESPWebServer/security/advisories/new))

Include: description, reproduction steps, impact, suggested fix.

We'll respond within 48 hours and aim to patch within 7 days.

## Security Features

- HTTPS required for Web Serial API
- Content Security Policy headers
- Rate limiting (5 builds/min per IP via Redis)
- Board ID validated against explicit allowlist
- HTML content sanitized via DOMPurify before preview
- Max bundle size enforced server-side (512KB)
- No secrets in source code; use environment variables
