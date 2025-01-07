import os
import boto3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_email(email_subject, html_body, email_from, email_to, smtp_server_ip, attachment=None):
    smtp_server = smtp_server_ip
    msg = MIMEMultipart()
    msg['Subject'] = email_subject
    msg['From'] = email_from
    recipients = email_to.split(',') if "," in email_to else [email_to]
    msg['To'] = ", ".join(recipients)
    msg.attach(MIMEText(html_body, 'html'))
    if attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.encode())  # Convert text to bytes
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="pipeline_log.txt"')
        msg.attach(part)
    try:
        server = smtplib.SMTP(smtp_server, 587)
        server.starttls()
        server.sendmail(email_from, recipients, msg.as_string())
        server.quit()
        print(f"Email sent to {', '.join(recipients)}.")
    except Exception as e:
        print(f"Error sending email: {e}")

def fetch_logs(project_name, build_id):
    logs_client = boto3.client('logs')
    log_group_name = f"/aws/codebuild/{project_name}"
    log_stream_name = build_id
    try:
        response = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            startFromHead=True
        )
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return None

    log_messages = 'Logs for build {0}:\n'.format(build_id)
    for log_event in response.get('events', []):
        log_messages += log_event['message'] + '\n'
    return log_messages

def get_build_status(build_id):
    codebuild_client = boto3.client('codebuild')
    try:
        response = codebuild_client.batch_get_builds(ids=[build_id])
        builds = response['builds']
        if builds:
            return builds[0]['buildStatus']
        else:
            print(f"No builds found for build ID: {build_id}")
            return None
    except Exception as e:
        print(f"Error fetching build status: {e}")
        return None

def main():
    email_from = "harikarn10@gmail.com"
    email_to = "harikrishnatangelapally@gmail.com"
    smtp_server_ip = "587"

    # Get actual values from environment variables
    env = os.environ.get('ENV', 'np')  # Default environment
    project_name = os.environ.get('CODEBUILD_PROJECT', f"cms-spares-codebuild-Lab1--Access-and-Setups-{env}")
    build_id = os.environ.get('CODEBUILD_BUILD_ID', 'your-build-id')  # Update with actual build ID

    print(f"Using Project Name: {project_name}")
    print(f"Using Build ID: {build_id}")

    # Check if the project name is in the monitored list
    if project_name not in [f"codebuildtest-{env}"]:
        print(f"Project {project_name} is not in the monitored list.")
        return

    # Fetch the build status dynamically
    build_status = get_build_status(build_id)
    if not build_status:
        print("Could not determine build status.")
        return

    print(f"Using Build Status: {build_status}")

    log_messages = fetch_logs(project_name, build_id)

    # Prepare the email body
    html_body = f"""
    <p>Hi Team,</p>
    <p>Below is the CodeBuild alert notification.</p>
    <p>Project Name: {project_name}</p>
    <p>Status: {build_status}</p>
    """
    email_subject = f"CodeBuild Alert for project {project_name}"

    # Check the build status and send emails accordingly
    if build_status == 'IN_PROGRESS':
        print(f'Sending email for project: {project_name} with status: {build_status}')
        send_email(email_subject, html_body, email_from, email_to, smtp_server_ip)
    elif build_status in ['SUCCEEDED', 'FAILED', 'STOPPED']:
        if log_messages:
            html_body += f"<p>Logs:</p><pre>{log_messages}</pre>"
            print(f'Sending email with log for project: {project_name} with status: {build_status}')
            send_email(email_subject, html_body, email_from, email_to, smtp_server_ip, attachment=log_messages)
        else:
            print(f'No logs found for project: {project_name}')
    else:
        print(f'Build status {build_status} is not in the list of statuses to process.')

if __name__ == '__main__':
    main()
