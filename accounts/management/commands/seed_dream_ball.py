from datetime import date, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import InvitationCode, User
from blog.models import Article
from events.models import Announcement, Event
from notifications.models import Notification
from reports.models import Report
from students.models import Partnership, PartnershipRequest, Profile


class Command(BaseCommand):
    help = "Create idempotent Dream Ball sample data for local development."

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(username="dream_admin", defaults={"email": "admin@dreamball.local", "first_name": "Avery", "last_name": "Morgan", "role": User.Role.ADMIN, "is_staff": True})
        admin.role = User.Role.ADMIN; admin.is_staff = True; admin.set_password("DreamBall2026!"); admin.save()
        moderator, _ = User.objects.get_or_create(username="dream_moderator", defaults={"email": "moderator@dreamball.local", "first_name": "Jordan", "last_name": "Lee", "role": User.Role.USER})
        moderator.role = User.Role.USER; moderator.set_password("DreamBall2026!"); moderator.save()
        teacher, _ = User.objects.get_or_create(username="dream_teacher", defaults={"email": "teacher@dreamball.local", "first_name": "Casey", "last_name": "Wilson", "role": User.Role.USER})
        teacher.role = User.Role.USER; teacher.set_password("DreamBall2026!"); teacher.save()
        for number in range(1, 11):
            InvitationCode.objects.get_or_create(code=f"DREAM-2026-{number:02}", defaults={"role": User.Role.USER})

        event, _ = Event.objects.get_or_create(title="Dream Ball 2026", defaults={
            "description": "A school celebration created for the graduating class - with music, thoughtful traditions and a beautiful shared evening.",
            "theme": "A night beneath the stars", "date": date.today() + timedelta(days=45), "time": time(18, 0),
            "location": "The Grand Hall", "address": "18 Academy Lane, City Centre", "dress_code": "Formal - your own expression",
            "program": "18:00 - Opening ceremony\n18:30 - Celebration dinner\n20:00 - Dance and music\n22:00 - Class awards\n22:45 - Closing ceremony",
            "rules": "Respect personal boundaries. Follow staff guidance. Keep the celebration welcoming for every classmate.",
            "preparation_tips": "Plan your journey in advance. Confirm arrival details. Keep a trusted adult informed.",
            "hero_image_url": "https://images.unsplash.com/photo-1670529776286-f426fb7ba42c?auto=format&fit=crop&w=1800&q=82", "is_active": True,
        })
        Announcement.objects.get_or_create(event=event, title="Arrival opens at 17:30", defaults={"body": "Please arrive through the main entrance and check in with the welcome team."})
        Announcement.objects.get_or_create(event=event, title="Photo zone is ready", defaults={"body": "The photo zone will be open throughout the evening near the east hall."})

        people = [("Amelia", "Reed"), ("Noah", "Kim"), ("Sofia", "Patel"), ("Ethan", "Brooks"), ("Olivia", "Nguyen"), ("Lucas", "Bennett"), ("Maya", "Carter"), ("Leo", "Davis"), ("Emma", "Rivera"), ("Daniel", "Foster"), ("Grace", "Murphy"), ("Alex", "Price"), ("Lily", "Ward"), ("Max", "Turner"), ("Ella", "Gray"), ("Ryan", "Cole"), ("Chloe", "Wright"), ("Sam", "Parker"), ("Ava", "Hughes"), ("Ben", "Kelly")]
        students = []
        for index, (first, last) in enumerate(people, start=1):
            user, _ = User.objects.get_or_create(username=f"student_{index:02}", defaults={"email": f"student{index:02}@dreamball.local", "first_name": first, "last_name": last, "role": User.Role.USER})
            user.first_name, user.last_name, user.role = first, last, User.Role.USER; user.set_password("DreamBall2026!"); user.save()
            status = Profile.Status.PENDING if index in {18, 19} else Profile.Status.REJECTED if index == 20 else Profile.Status.APPROVED
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.grade = "11"; profile.class_letter = chr(64 + ((index - 1) % 4) + 1); profile.height = 158 + index
            profile.bio = "Looking forward to a kind, memorable school celebration and preparing thoughtfully with the community."
            profile.dance_experience = ["Beginner", "Some experience", "Intermediate", "Experienced"][index % 4]
            profile.personality = ["Calm", "Creative", "Thoughtful", "Outgoing"][index % 4]
            profile.preferred_rehearsal_time = ["After school", "Weekends", "Early evening"][index % 3]
            profile.agreed_to_rules = True; profile.status = status
            profile.moderation_note = "Please add a little more detail to your bio before approval." if status == Profile.Status.REJECTED else ""
            profile.save(); students.append(user)

        partnership, _ = Partnership.objects.get_or_create(student_one=students[0], student_two=students[1], defaults={"shared_notes": "We plan to meet after school next week to practise the opening steps."})
        PartnershipRequest.objects.get_or_create(sender=students[2], receiver=students[3], defaults={"status": PartnershipRequest.Status.PENDING})
        PartnershipRequest.objects.get_or_create(sender=students[4], receiver=students[5], defaults={"status": PartnershipRequest.Status.DECLINED})
        Report.objects.get_or_create(reporter=students[6], profile=students[7].profile, defaults={"reason": Report.Reason.OTHER, "details": "Please review this profile for accuracy."})
        for student in students[:10]:
            Notification.objects.get_or_create(user=student, message="Dream Ball event details are now available in your dashboard.")
        Notification.objects.get_or_create(user=students[2], message="You have a new partnership request to review.")

        articles = [
            ("Why Student Safety Matters", "why-student-safety-matters", "Safety", "A thoughtful event starts when every student knows where to find support and how to respect shared boundaries.", 4),
            ("How Dream Ball Works", "how-dream-ball-works", "Getting started", "From a personal invitation to a confirmed partnership, every step is designed for calm and clarity.", 3),
            ("Preparing for Your First School Ball", "preparing-for-your-first-school-ball", "Preparation", "Simple planning can make the evening feel exciting rather than overwhelming.", 5),
            ("Digital Privacy for Students", "digital-privacy-for-students", "Privacy", "A practical guide to sharing thoughtfully and protecting classmates online.", 4),
            ("Building Respectful School Communities", "building-respectful-school-communities", "Community", "Small everyday choices can help every classmate feel welcome at a shared celebration.", 4),
        ]
        covers = ["https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=1000&q=80", "https://images.unsplash.com/photo-1670529776286-f426fb7ba42c?auto=format&fit=crop&w=1000&q=80", "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=1000&q=80", "https://images.unsplash.com/photo-1478146896981-b80fe463b330?auto=format&fit=crop&w=1000&q=80", "https://images.unsplash.com/photo-1507504031003-b417219a0fde?auto=format&fit=crop&w=1000&q=80"]
        for (title, slug, category, excerpt, minutes), cover in zip(articles, covers):
            Article.objects.get_or_create(slug=slug, defaults={"title": title, "category": category, "excerpt": excerpt, "body": f"{excerpt}\n\nDream Ball is an official school event platform. It gives students a clear, supported way to prepare while keeping respect, privacy and wellbeing at the centre of every interaction.\n\nIf you have a concern, use the report tool or speak with a trusted school adult.", "author": "Dream Ball Team", "reading_time": minutes, "cover_image_url": cover})
        self.stdout.write(self.style.SUCCESS("Dream Ball sample data is ready."))
