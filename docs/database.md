# Database overview

`User` is the authentication model and has one role. A student normally has one `Profile`; profiles move through pending, approved and needs-changes moderation states.

`InvitationCode` is unique and connected to one user after use. `PartnershipRequest` links a sender and receiver, while `Partnership` records a confirmed pair and owns `Meeting` records.

`Event` owns `Announcement` records. `Report` links a reporting user to a profile. `Notification` is user-scoped and tracks read state. `Article` stores Student Journal content and metadata.

Database constraints prevent duplicate invitation codes, duplicate report submissions and duplicate requests between the same two users.
