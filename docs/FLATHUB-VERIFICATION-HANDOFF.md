# Flathub domain verification handoff

The application ID uses the project's controlled domain: `com.jwcalendar.JWCalendar` and `jwcalendar.com`. No verification token has been requested or fabricated.

After a human submission is accepted and the app is present in the Flathub Developer Portal:

1. Obtain the unique token issued for this application from the portal.
2. Re-read Flathub's current verification instructions.
3. Publish the token using one of the then-supported methods, such as `https://jwcalendar.com/.well-known/org.flathub.VerifiedApps.txt` or a `_flathub.jwcalendar.com` TXT record, if Flathub still supports that method.
4. Verify the public response or DNS answer before marking the domain verified.

Never publish a placeholder or guessed token.
