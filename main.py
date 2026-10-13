
import boto3
import json
import csv
import re
import os
from datetime import datetime
from botocore.exceptions import ClientError

# ================= AWS CONFIGURATION =================
REGION = "ap-south-1"
BUCKET_NAME = "shita-automation-project-2026-unique123"
LAMBDA_NAME = "MyAutomationFunction"
DYNAMODB_TABLE = "S3UploadRecords"

SNS_TOPIC_ARN = (
    "arn:aws:sns:ap-south-1:143853720612:"
    "AWSAutomationUploadReport"
)

# Connect to AWS services
s3 = boto3.client("s3", region_name=REGION)
lam = boto3.client("lambda", region_name=REGION)
sns = boto3.client("sns", region_name=REGION)
dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(DYNAMODB_TABLE)


# ================= FEATURE 1 =================
def upload_file():
    filename = input(
        "Enter local file name (default sample.txt): "
    ).strip() or "sample.txt"

    if not os.path.isfile(filename):
        print("Error: Local file not found:", filename)
        return

    try:
        s3.upload_file(
            filename, BUCKET_NAME, os.path.basename(filename)
        )
        print("File uploaded successfully!")
        print("Bucket:", BUCKET_NAME)
        print("File:", os.path.basename(filename))
    except (ClientError, OSError) as e:
        print("Upload error:", e)


# ================= FEATURE 2 =================
def list_files():
    try:
        paginator = s3.get_paginator("list_objects_v2")
        found = False

        print("\nFiles in S3 bucket:", BUCKET_NAME)

        for page in paginator.paginate(Bucket=BUCKET_NAME):
            for item in page.get("Contents", []):
                found = True
                print(
                    item["Key"],
                    "| Size:", item["Size"], "bytes",
                    "| Modified:", item["LastModified"]
                )

        if not found:
            print("No files found in the bucket.")

    except ClientError as e:
        print("List error:", e)


# ================= FEATURE 3 =================
def invoke_lambda():
    try:
        payload = {
            "project": "AWS Automation",
            "action": "test from Python"
        }

        response = lam.invoke(
            FunctionName=LAMBDA_NAME,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload).encode("utf-8")
        )

        result = json.loads(
            response["Payload"].read().decode("utf-8")
        )

        if response.get("FunctionError"):
            print("Lambda execution failed.")
        else:
            print("Lambda invoked successfully!")

        print(json.dumps(result, indent=2))

    except (ClientError, ValueError) as e:
        print("Lambda error:", e)


# ================= FEATURE 4 =================
def list_buckets():
    try:
        response = s3.list_buckets()
        buckets = response.get("Buckets", [])

        if not buckets:
            print("No S3 buckets found.")
            return

        print("\nYour S3 buckets:")
        for bucket in buckets:
            print("-", bucket["Name"])

    except ClientError as e:
        print("Bucket listing error:", e)


# ================= FEATURE 5 =================
def create_bucket():
    bucket_name = input(
        "Enter a unique lowercase S3 bucket name: "
    ).strip().lower()

    if not re.fullmatch(
        r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?",
        bucket_name
    ):
        print("Invalid bucket name format.")
        return

    if not 3 <= len(bucket_name) <= 63:
        print("Bucket name must contain 3 to 63 characters.")
        return

    if (
        ".." in bucket_name
        or ".-" in bucket_name
        or "-." in bucket_name
    ):
        print("Bucket name cannot contain these adjacent characters.")
        return

    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                "LocationConstraint": REGION
            }
        )
        print("Bucket created successfully:", bucket_name)

    except ClientError as e:
        print("Bucket creation error:", e)


# ================= FEATURE 6 =================
def download_file():
    object_name = input(
        "Enter S3 file name to download: "
    ).strip()

    if not object_name:
        print("File name cannot be empty.")
        return

    local_name = input(
        "Enter local destination file name: "
    ).strip()

    if not local_name:
        print("Local destination cannot be empty.")
        return

    try:
        s3.download_file(BUCKET_NAME, object_name, local_name)
        print("Download successful. Saved as:", local_name)

    except (ClientError, OSError) as e:
        print("Download error:", e)


# ================= FEATURE 7 =================
def delete_file():
    object_name = input(
        "Enter exact S3 file name to delete: "
    ).strip()

    if not object_name:
        print("File name cannot be empty.")
        return

    confirm = input(
        f"Delete '{object_name}' permanently? Type YES to confirm: "
    ).strip()

    if confirm != "YES":
        print("Deletion cancelled.")
        return

    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=object_name)
        s3.delete_object(Bucket=BUCKET_NAME, Key=object_name)
        print("File deleted successfully.")

    except ClientError as e:
        print("File deletion error:", e)


# ================= FEATURE 8 =================
def file_details():
    object_name = input(
        "Enter exact S3 file name: "
    ).strip()

    if not object_name:
        print("File name cannot be empty.")
        return

    try:
        response = s3.head_object(
            Bucket=BUCKET_NAME, Key=object_name
        )

        print("\n===== S3 FILE DETAILS =====")
        print("Bucket:", BUCKET_NAME)
        print("File:", object_name)
        print("Size:", response["ContentLength"], "bytes")
        print("Last modified:", response["LastModified"])
        print("Content type:", response.get("ContentType", "Unknown"))

    except ClientError as e:
        print("File details error:", e)


# ================= DYNAMODB HELPER =================
def get_upload_records():
    records = []
    scan_kwargs = {}

    while True:
        response = table.scan(**scan_kwargs)
        records.extend(response.get("Items", []))

        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break

        scan_kwargs["ExclusiveStartKey"] = last_key

    return records


# ================= FEATURE 9 =================
def view_upload_records():
    try:
        records = get_upload_records()

        if not records:
            print("No upload records found.")
            return

        print("\n===== DYNAMODB UPLOAD RECORDS =====")

        for record in records:
            print("File ID:", record.get("file_id", "N/A"))
            print("Bucket:", record.get("bucket_name", "N/A"))
            print("File:", record.get("file_name", "N/A"))
            print("Upload time:", record.get("event_time", "N/A"))
            print("-" * 40)

        print("Total records:", len(records))

    except ClientError as e:
        print("DynamoDB error:", e)


# ================= FEATURE 10 =================
def generate_upload_report():
    try:
        records = get_upload_records()

        if not records:
            print("No records available for reporting.")
            return

        bucket_counts = {}

        for record in records:
            name = record.get("bucket_name", "Unknown")
            bucket_counts[name] = bucket_counts.get(name, 0) + 1

        print("\n===== UPLOAD REPORT =====")
        print("Total upload records:", len(records))

        for name, count in sorted(bucket_counts.items()):
            print(f"{name}: {count} record(s)")

        print("=========================")

    except ClientError as e:
        print("Report error:", e)


# ================= CSV REPORT HELPER =================
def write_records_csv(filename, records):
    fields = [
        "file_id", "bucket_name", "file_name", "event_time"
    ]

    with open(
        filename, "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=fields,
            extrasaction="ignore"
        )
        writer.writeheader()

        for record in records:
            writer.writerow({
                field: record.get(field, "")
                for field in fields
            })


# ================= FEATURE 11 =================
def export_upload_records_csv():
    try:
        records = get_upload_records()

        if not records:
            print("No records available to export.")
            return

        filename = "s3_upload_report.csv"
        write_records_csv(filename, records)

        print("CSV report exported:", filename)
        print("Total records exported:", len(records))

    except (ClientError, OSError) as e:
        print("CSV export error:", e)


# ================= FEATURE 12 =================
def search_upload_records_by_date():
    search_date = input("Enter date (YYYY-MM-DD): ").strip()

    try:
        datetime.strptime(search_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date. Example: 2026-10-09")
        return

    try:
        records = get_upload_records()
        matches = [
            record for record in records
            if str(record.get("event_time", "")).startswith(search_date)
        ]

        if not matches:
            print("No records found for date:", search_date)
            return

        print("\n===== DATE SEARCH RESULTS =====")

        for record in matches:
            print("File:", record.get("file_name", "N/A"))
            print("Bucket:", record.get("bucket_name", "N/A"))
            print("Upload time:", record.get("event_time", "N/A"))
            print("-" * 35)

        print("Matching records:", len(matches))

    except ClientError as e:
        print("Date search error:", e)


# ================= FEATURE 13 =================
def search_upload_records_by_filename():
    search_name = input("Enter file name to search: ").strip()

    if not search_name:
        print("File name cannot be empty.")
        return

    try:
        records = get_upload_records()
        matches = [
            record for record in records
            if search_name.lower() in str(
                record.get("file_name", "")
            ).lower()
        ]

        if not matches:
            print("No upload records found for:", search_name)
            return

        print("\n===== FILE SEARCH RESULTS =====")

        for record in matches:
            print("File ID:", record.get("file_id", "N/A"))
            print("Bucket:", record.get("bucket_name", "N/A"))
            print("File:", record.get("file_name", "N/A"))
            print("Upload time:", record.get("event_time", "N/A"))
            print("-" * 35)

        print("Matching records:", len(matches))

    except ClientError as e:
        print("File search error:", e)


# ================= FEATURE 14 =================
def delete_empty_bucket():
    bucket_name = input(
        "Enter exact bucket name to delete: "
    ).strip()

    if not bucket_name:
        print("Bucket name cannot be empty.")
        return

    if bucket_name == BUCKET_NAME:
        print("Deletion is blocked for your configured project bucket.")
        return

    confirm = input(
        f"Type DELETE to delete empty bucket '{bucket_name}': "
    ).strip()

    if confirm != "DELETE":
        print("Bucket deletion cancelled.")
        return

    try:
        response = s3.list_objects_v2(
            Bucket=bucket_name, MaxKeys=1
        )

        if response.get("KeyCount", 0) > 0:
            print("Bucket is not empty. Delete its objects first.")
            return

        s3.delete_bucket(Bucket=bucket_name)
        print("Empty bucket deleted successfully:", bucket_name)

    except ClientError as e:
        print("Bucket deletion error:", e)


# ================= FEATURE 16 =================
def automatic_upload_report():
    try:
        records = get_upload_records()

        if not records:
            print("No upload records found. Report not generated.")
            return

        filename = "automatic_upload_report.csv"
        write_records_csv(filename, records)

        print("\n===== AUTOMATIC UPLOAD REPORT =====")
        print("Report generated:", filename)
        print(
            "Report generation time:",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        print("Total upload records:", len(records))
        print("Report saved in your project folder.")
        print("===================================")

    except (ClientError, OSError) as e:
        print("Automatic report error:", e)


# ================= FEATURE 17 =================
def upload_report_to_s3():
    filename = "automatic_upload_report.csv"

    if not os.path.isfile(filename):
        print("Report not found. Run option 16 first.")
        return

    try:
        s3.upload_file(filename, BUCKET_NAME, filename)

        print("\nReport uploaded successfully to S3!")
        print("Bucket:", BUCKET_NAME)
        print("S3 file:", filename)

    except (ClientError, OSError) as e:
        print("Report upload error:", e)


# ================= FEATURE 18 =================
def email_upload_report():
    try:
        records = get_upload_records()

        if not records:
            print("No upload records found. Email not sent.")
            return

        filename = "automatic_upload_report.csv"
        write_records_csv(filename, records)

        bucket_counts = {}
        for record in records:
            bucket_name = record.get("bucket_name", "Unknown")
            bucket_counts[bucket_name] = (
                bucket_counts.get(bucket_name, 0) + 1
            )

        message_lines = [
            "AWS AUTOMATION PROJECT - UPLOAD REPORT",
            "",
            "Report generated: "
            + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            f"Total upload records: {len(records)}",
            "",
            "Uploads by bucket:"
        ]

        for bucket_name, count in sorted(bucket_counts.items()):
            message_lines.append(
                f"{bucket_name}: {count} upload record(s)"
            )

        message_lines.extend([
            "",
            f"CSV report created locally: {filename}",
            "The CSV file is not attached to this email."
        ])

        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="AWS Automation - Upload Report",
            Message="\n".join(message_lines)
        )

        print("\nEmail notification submitted to Amazon SNS!")
        print("Total upload records:", len(records))
        print("SNS Message ID:", response["MessageId"])
        print("Check your confirmed email subscription.")

    except (ClientError, OSError) as e:
        print("Email report error:", e)


# ================= MAIN MENU =================
def main():
    while True:
        print("\n===== AWS AUTOMATION PROJECT =====")
        print("1. Upload file to S3")
        print("2. List S3 files")
        print("3. Invoke Lambda")
        print("4. List S3 buckets")
        print("5. Create S3 bucket")
        print("6. Download S3 file")
        print("7. Delete S3 file")
        print("8. View S3 file details")
        print("9. View DynamoDB upload records")
        print("10. Generate upload report")
        print("11. Export records to CSV")
        print("12. Search records by date")
        print("13. Search records by file name")
        print("14. Delete an empty S3 bucket")
        print("15. Exit")
        print("16. Automatic upload report")
        print("17. Upload report to S3")
        print("18. Email upload report using SNS")

        choice = input("Enter your choice: ").strip()

        try:
            if choice == "1":
                upload_file()
            elif choice == "2":
                list_files()
            elif choice == "3":
                invoke_lambda()
            elif choice == "4":
                list_buckets()
            elif choice == "5":
                create_bucket()
            elif choice == "6":
                download_file()
            elif choice == "7":
                delete_file()
            elif choice == "8":
                file_details()
            elif choice == "9":
                view_upload_records()
            elif choice == "10":
                generate_upload_report()
            elif choice == "11":
                export_upload_records_csv()
            elif choice == "12":
                search_upload_records_by_date()
            elif choice == "13":
                search_upload_records_by_filename()
            elif choice == "14":
                delete_empty_bucket()
            elif choice == "15":
                print("Goodbye!")
                break
            elif choice == "16":
                automatic_upload_report()
            elif choice == "17":
                upload_report_to_s3()
            elif choice == "18":
                email_upload_report()
            else:
                print("Invalid choice. Enter a number from 1 to 18.")

        except ClientError as e:
            print("AWS service error:", e)


if __name__ == "__main__":
    main()

