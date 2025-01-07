import os
import boto3
import smtplib
from email.mime.text import MIMEText

def send_email(message):
    smtp_server = "email-smtp.us-east-1.amazonaws.com"
    smtp_port = 587
    smtp_username = "AKIAS74TLYHELKOX7D74"
    smtp_password = "BOnvUFr8KQHsryZa3a/r2NRXSASK6UbhSpRIwLamvEZD"
    from_email = "harikarn10@gmail.com"
    to_email = "harikrishnatangelapally@gmail.com"

    msg = MIMEText(message)
    msg['Subject'] = 'AWS CodeBuild Notification'
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())

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

    # Get actual values from environment variables
    env = os.environ.get('ENV', 'np')  # Default environment
    project_name = os.environ.get('CODEBUILD_PROJECT', f"codebuildtest-{env}")
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
        send_email(html_body)
    elif build_status in ['SUCCEEDED', 'FAILED', 'STOPPED']:
        print(f'Sending email for project: {project_name} with status: {build_status}')
        send_email(html_body)
    else:
        print(f'Build status {build_status} is not in the list of statuses to process.')

if __name__ == '__main__':
    main()
