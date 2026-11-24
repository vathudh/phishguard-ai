# Security and Privacy Notes

PhishGuard AI is an educational defensive-security project. Do not use it as the only control for business email security.

- The local app saves only a 500-character email preview, result metadata, and user feedback in SQLite.
- Raw `.eml` uploads are analyzed in memory; attachments are not processed or executed.
- Public deployments should use HTTPS and a persistent encrypted database. The supplied Render template mounts a persistent disk for SQLite.
- Do not upload sensitive, confidential, or personal emails to a public deployment unless you control the hosting and have permission.
- Report code-security concerns through the repository's private security reporting option after GitHub setup.
