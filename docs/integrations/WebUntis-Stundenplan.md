# WebUntis timetable, homework and iCalendar

## Runtime flow

Each confirmed guardian-child pair has its own encrypted WebUntis connection.
The connection receives one runtime-only external student identifier. A sync
uses the allow-listed JSON-RPC/REST adapter and writes only normalized personal
lessons and homework rows. Raw responses, passwords and session identifiers are
not logged or stored.

The timetable importer reads a rolling window from seven days in the past to 90
days in the future. It upserts by a stable fingerprint and removes stale lessons
inside that window. Homework is upserted independently so an unavailable
homework endpoint does not discard a successful timetable update.

## Teacher and subject mapping

The local workbook has no header row. Tabelle2 columns A/B contain teacher
code/display-name pairs. Tabelle3 columns A/B contain subject code/display-name
pairs and columns C/D contain class-specific teacher pairs. Blank pairs are
skipped. The workbook and generated CSVs remain ignored local data.

The management command import_webuntis_mappings imports UTF-8 code,label CSV
files after deployment.

## Calendar options

The authenticated download route returns a one-time ICS snapshot. Imported
calendar applications do not receive later changes from that file.

The subscription route issues a high-entropy token and stores only its SHA-256
hash. Issuing a new address revokes the prior address. The feed includes lessons
and dated homework; it always reads the latest normalized database state. Treat
the address like a password.

## Schedule

SyncSchedule is enabled for 06:00, 12:00 and 18:00 Europe/Berlin. On the
Windows host, tools/Register-Klasse5eWebUntisSchedule.ps1 creates three daily
Task Scheduler entries. Each invokes tools/Invoke-Klasse5eWebUntisSync.ps1,
which runs manage.py sync_webuntis --automatic inside the existing app
container. No Redis, worker service or second application runtime is introduced.

## Verified deployment state (2026-09-01)

- Production migrations 0003 through 0005 are applied and the application,
  database and vision containers are healthy.
- The personal parent connection completed a real read-only sync and imported
  357 normalized timetable rows. A direct repeat was throttled as designed.
- The local mapping import loaded 85 teacher and 15 subject mappings. Source
  workbook, generated CSV files and raw examples remain under the ignored
  `references/webuntis/private/` directory.
- Windows Task Scheduler entries for 06:00, 12:00 and 18:00 are registered and
  ready. The runner talks directly to the named application container and does
  not need decrypted secrets in a task file.
- The public health route, login page and production CSS each return HTTP 200.
  The protected WebUntis route redirects anonymous requests to login.
- The full application suite passes with 89 tests; Ruff, Django system check,
  migration drift check, Python compilation and `git diff --check` pass.

The timetable JSON-RPC flow works with the actual parent account. The internal
homework REST route currently returns no usable rows for this account, whereas
the supplied reference uses a browser-only `/student-homework` view. Homework
therefore remains an explicitly visible open integration boundary; the system
keeps successful timetable data and does not claim a successful homework
import. Absence creation remains outside this read-only adapter.


## Update 2026-09-01: reference aliases and unified web calendar

The private timetable export uses written subject names while the WebUntis
JSON-RPC response exposes numeric element identifiers. The local importer now
joins both sources by date and exact start/end time and resolves the result
against the class-specific workbook mapping. It accepts both subject codes and
written subject labels. Room values are deliberately not used for the join
because the two sources use incompatible room identifier systems.

The production import created 12 subject aliases and 17 teacher aliases and
updated 294 existing lesson rows. All 357 stored lessons now have non-numeric
display labels. The private workbook and generated CSV files remain ignored and
were mounted read-only into a short-lived import container.

The authenticated web calendar is now one responsive month view. Personal
lessons, dated homework, class calendar entries, published events and
itslearning calendar items share one grid and one daily agenda. Appointments,
homework, lessons and learning-platform entries use distinct colors plus text
labels, so meaning does not depend on color alone.

The observed parent homework payload is normalized by joining homework.lessonId
to data.lessons. Synthetic tests cover subject resolution, dates, combined
text/remark and open/completed state. The real endpoint is still an open
authentication boundary: the working JSON-RPC session receives HTTP 500 from
the homework REST route, and no real homework rows are stored. The browser flow
also requests /api/token/new; the next task must implement or explicitly
provision this user-token context without adding a production browser scraper.
