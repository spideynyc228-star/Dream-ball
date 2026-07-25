# Architecture

Dream Ball uses Django's app-based architecture with server-rendered templates.

- `accounts`: custom users, roles and one-time invitation codes.
- `students`: profiles, partnership requests and confirmed partnerships.
- `events`: school event information, announcements and rehearsal meetings.
- `moderation`: staff review workflows and invitation-code operations.
- `reports`: student concerns about profiles.
- `notifications`: in-app event, moderation and partnership updates.
- `blog`: Student Journal content.
- `safety`: online Safety Center and downloadable checklist.
- `dashboard`: home dashboard, event page, notification centre and error pages.

SQLite is used for development. All relationships are defined through Django's ORM and can move to PostgreSQL by changing the database configuration.
