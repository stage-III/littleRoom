import sys
from django.core.mail.backends.base import BaseEmailBackend


class DevConsoleEmailBackend(BaseEmailBackend):
    """Prints email body directly to stdout — no MIME/quoted-printable encoding."""

    def send_messages(self, email_messages):
        for message in email_messages:
            print('\n' + '─' * 60, file=sys.stdout)
            print(f'To:      {", ".join(message.to)}', file=sys.stdout)
            print(f'Subject: {message.subject}', file=sys.stdout)
            print('─' * 60, file=sys.stdout)
            print(message.body, file=sys.stdout)
            print('─' * 60 + '\n', file=sys.stdout)
        sys.stdout.flush()
        return len(email_messages)
