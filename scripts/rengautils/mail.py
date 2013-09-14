#!/usr/bin/python

"""Send the contents of a directory as a MIME message."""

import os
import sys
import smtplib
# For guessing MIME type based on file name extension
import mimetypes

from optparse import OptionParser

from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

COMMASPACE = ', '


def send_mail(sender, to, subject=None, message=None, atachment_path=None):
    outer = MIMEMultipart()
    outer['Subject'] = subject
    outer['To'] = COMMASPACE.join(to)
    outer['From'] = sender
    outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'
    if atachment_path:
        filename = os.path.basename(atachment_path)
        ctype, encoding = mimetypes.guess_type(atachment_path)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'text':
            fp = open(atachment_path)
            # Note: we should handle calculating the charset
            msg = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == 'image':
            fp = open(atachment_path, 'rb')
            msg = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == 'audio':
            fp = open(atachment_path, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(atachment_path, 'rb')
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(fp.read())
            fp.close()
            # Encode the payload using Base64
            encoders.encode_base64(msg)
        # Set the filename parameter
        msg.add_header('Content-Disposition', 'attachment', filename=filename)

    # add msg text to body
    if message:
        msg_text = MIMEText(message, 'plain')
        outer.attach(msg_text)
    outer.attach(msg)
    # Now send the message
    composed = outer.as_string()

    s = smtplib.SMTP('smtp.live.com', 587)
    s.ehlo()
    s.starttls()
    s.login('rengabit@outlook.com', 'Atzmon83')
    s.sendmail(sender, to, composed)
    s.quit()


def main():
    parser = OptionParser(usage="""\
Send the contents of a directory as a MIME message.

Usage: %prog [options]

Unless the -o option is given, the email is sent by forwarding to your local
SMTP server, which then does the normal delivery process.  Your local machine
must be running an SMTP server.
""")
    parser.add_option('-f', '--file',
                      type='string', action='store',
                      help="""Mail the given file as an attachment.""")
    parser.add_option('-s', '--sender',
                      type='string', action='store', metavar='SENDER',
                      help='The value of the From: header (required)')
    parser.add_option('-r', '--recipient',
                      type='string', action='append', metavar='RECIPIENT',
                      default=[], dest='recipients',
                      help='A To: header value (at least one required)')
    opts, args = parser.parse_args()
    if not opts.sender or not opts.recipients or not opts.file:
        parser.print_help()
        sys.exit(1)
    # Create the enclosing (outer) message
    send_mail(opts.sender, opts.recipients, 'A Renga has been shared with you', 'Hi!\nHow are you?\n\n{0} would like to share this Renga with you\nIf you don\'t have RengaBit app installed you can get it at rengabit.com\n\nGood day :)'.format(
        opts.sender), opts.file)


if __name__ == '__main__':
    main()
