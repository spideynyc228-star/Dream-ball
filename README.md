# Dream Ball

Dream Ball is a secure, invitation-only Django platform for coordinating school celebrations such as prom, graduation balls and winter dances. It supports safe student partnership planning while keeping moderation, privacy and school oversight at the centre of the product.

> Screenshots: add exported landing, student-dashboard and moderation-centre screenshots here when preparing a portfolio case study.

## Product features

- Personal, one-time invitation codes and role-aware authentication
- Staff-moderated student profiles and a searchable approved directory
- Considerate partnership requests, confirmed partnerships and rehearsal planning
- Moderator operations centre for profiles, reports and invitation codes
- Event information, announcements, countdown, venue gallery and preparation tips
- In-app notification centre, Student Journal and Safety Center
- Downloadable [Digital Safety Checklist](docs/Digital_Safety_Checklist.pdf)
- Custom 403, 404 and 500 experiences

## Technology

Python 3.13, Django 5, SQLite (PostgreSQL-ready ORM design), Django Templates, HTML5, CSS3, JavaScript, Pillow, python-dotenv and django-filter.

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py seed_dream_ball
python3 manage.py runserver
```

Open `http://127.0.0.1:8000/`.

### Sample accounts

All seeded accounts use password `DreamBall2026!`:

- Administrator: `dream_admin`
- Moderator: `dream_moderator`
- Teacher: `dream_teacher`
- Students: `student_01` through `student_20`

The seed command also creates ten invitation codes: `DREAM-2026-01` through `DREAM-2026-10`.

## Project structure

```text
accounts/       authentication, roles, invitations and sample-data command
students/       profiles, requests and partnerships
events/         event information, announcements and meetings
moderation/     role-safe moderation operations
reports/        profile concerns and resolution workflows
notifications/  user notification centre
blog/           Student Journal
safety/         Safety Center and PDF download
dashboard/      dashboards, event page and error pages
docs/           product, architecture and deployment documentation
```

## Database overview

The application uses a custom `User` model. One-time `InvitationCode` records connect to a user once used. Student `Profile`, `PartnershipRequest`, `Partnership`, `Meeting`, `Event`, `Announcement`, `Report`, `Notification` and `Article` models cover the core product workflows. See [database.md](docs/database.md) for details.

## Configuration

Copy `.env.example` to `.env`, set a unique `SECRET_KEY`, and update `ALLOWED_HOSTS` for production. SQLite is the local default; configure Django's database environment values for PostgreSQL deployment.

## Future improvements

See [future_improvements.md](docs/future_improvements.md) for the planned roadmap.
