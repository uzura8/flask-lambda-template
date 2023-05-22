from email.header import Header
import boto3


def send_email_on_ses(subject, sender, recipients, text_body='', html_body='', region=None):
    msg = {
        'Subject': {
            'Data': subject,
            'Charset': 'UTF-8'
        },
        'Body': {}
    }

    if len(text_body) > 0:
        msg['Body']['Text'] =  {
            'Data': text_body,
            'Charset': 'UTF-8'
        }
    if len(html_body) > 0:
        msg['Body']['Html'] =  {
            'Data': html_body,
            'Charset': 'UTF-8'
        }

    client = boto3.client('ses', region_name=region)
    return client.send_email(
        Source='%s <%s>' % (
            Header(sender[0].encode('iso-2022-jp'),'iso-2022-jp').encode(),
            sender[1]
        ),
        Destination={
            'ToAddresses': recipients
        },
        Message=msg
        #ReplyToAddresses=[sender]
    )


def debug_email(subject, sender, recipients, text_body):
    data = '\n-----------------------------\n'
    data += 'to: {}\nfrom: {}\nsubject: {}\n'.format(', '.join(recipients),
                                                        sender, subject)
    data += '---------------\n'
    data += text_body
    data += '\n-----------------------------\n'
    f = open('./dev_tools/var/mail.log','a')
    f.write(data)
    f.close()
