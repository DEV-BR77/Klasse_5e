# WebUntis reference material

The original local scripts, exported timetable/homework examples and the
teacher/subject workbook are stored under references/webuntis/private/.
That directory is ignored because it contains credentials, school staff names
and a child-specific WebUntis identifier.

The checked-in scripts are sanitized technical references only. They read
credentials and the student identifier from environment variables and never
print them.

Workbook structure used for the runtime import:

- Tabelle2: teacher code in column A, display name in column B; no header row.
- Tabelle3: subject code/name in A/B and class-specific teacher code/name in
  C/D; no header row. Empty C/D pairs are intentionally skipped.
- The workbook is converted locally to UTF-8 CSV files with code,label headers.
  Only those local CSVs are imported into the database.

Production code does not depend on the reference scripts. The Django adapter
uses the existing allow-listed JSON-RPC/REST client and stores normalized,
personal data in PostgreSQL.
