# Security Policy

## Supported Versions

Security fixes target the `main` branch until formal releases are cut.

## Reporting A Vulnerability

Please do not open a public issue for a suspected vulnerability. Email the maintainer or use GitHub private vulnerability reporting if it is enabled for the repository.

Include:

- affected component (`backend`, `frontend`, `mcp_server`, Docker, or docs)
- reproduction steps
- impact assessment
- any suggested fix

## Security Model

Baton Studio is local-first by default. `BATON_ENV=local` is unauthenticated and intended for trusted local development.

Production mode requires bearer auth:

- `BATON_API_KEY=<token>` creates one admin token.
- `BATON_API_KEYS=read-token:reader,ops-token:operator,admin-token:admin` enables scoped static tokens.

Roles:

- `reader`: read routes, WebSocket subscription, metrics
- `operator`: reader plus mutating mission operations
- `admin`: operator plus mission import

Production deployments should also configure:

- `BATON_CORS_ORIGINS`
- non-default secrets
- TLS termination in front of the backend
- persistent database storage and backup policy

## Dependency Audits

Run:

```bash
make audit
```

This audits backend, frontend, and MCP dependency sets.
