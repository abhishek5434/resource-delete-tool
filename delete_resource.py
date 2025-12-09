import csv
import requests
import time
import argparse
import paramiko
import base64


DELETE_API_URL = "https://api.zetaglobal.net/ver2/"  # Append resource_id


# -------------------------------------------------------------------
# BUILD BASIC AUTH HEADERS + Content-Type + Accept
# -------------------------------------------------------------------
def build_headers(username, password):
    token = base64.b64encode(f"{username}:{password}".encode()).decode()

    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


# -------------------------------------------------------------------
# DELETE RESOURCE API (single attempt)
# -------------------------------------------------------------------
def delete_resource(resource_id: str,site_id: str, headers: dict):
    """
    Sends DELETE request to Zeta API.
    Returns (status_code, response_text)
    """
    endpoint = f"{DELETE_API_URL}{site_id}/resources/{resource_id}"
    try:
        response = requests.delete(
            endpoint,
            headers=headers
        )
        return response.status_code, response.text
    except Exception as e:
        return None, str(e)


# -------------------------------------------------------------------
# DELETE WITH RETRY (1 additional attempt)
# -------------------------------------------------------------------
def delete_with_retry(resource_id: str,site_id: str, headers: dict):
    code, text = delete_resource(resource_id, site_id,headers)

    # Accept any 2xx status code as success
    if code is not None and 200 <= code < 300:
        return code, text

    print(f"[Retry] First attempt failed for resource_id={resource_id}. Retrying...")
    time.sleep(1)

    return delete_resource(resource_id, site_id, headers)


# -------------------------------------------------------------------
# SFTP UPLOAD FUNCTION
# -------------------------------------------------------------------
def upload_to_sftp(host, username, password, local_path, remote_filename):
    """
    Uploads output CSV file to SFTP: /file_share/<filename>
    """
    try:
        transport = paramiko.Transport((host, 22))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        remote_path = f"/file_share/{remote_filename}"
        sftp.put(local_path, remote_path)

        sftp.close()
        transport.close()
        print(f"[SFTP] File uploaded to {remote_path}")

    except Exception as e:
        print(f"[SFTP ERROR] {e}")


# -------------------------------------------------------------------
# MAIN PROCESSOR
# -------------------------------------------------------------------
def process_file(
    input_csv: str,
    output_csv: str,
    site_id: str,
    username: str,
    password: str,
    sftp_host: str,
    sftp_user: str,
    sftp_pass: str
):
    headers = build_headers(username, password)

    total = 0
    success = 0
    failed = 0

    # Create output CSV on disk
    with open(output_csv, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["resource_id", "site_id", "response_code", "response_text"])

        # Process input CSV
        with open(input_csv, "r") as infile:
            reader = csv.DictReader(infile)

            if "resource_id" not in reader.fieldnames:
                raise ValueError("Input CSV must contain a 'resource_id' column.")

            for row in reader:
                total += 1
                resource_id = row["resource_id"]

                # DELETE with retry
                code, text = delete_with_retry(resource_id, site_id,headers)

                # Count success if any 2xx
                if code is not None and 200 <= code < 300:
                    success += 1
                else:
                    failed += 1

                # Clean text for CSV (remove commas/newlines)
                safe_text = str(text).replace("\n", " ").replace(",", ";")

                writer.writerow([resource_id, site_id, code, safe_text])

                print(f"[Processed] resource_id={resource_id}, status={code}")

    # Summary
    print("\n===== SUMMARY =====")
    print(f"Site ID:           {site_id}")
    print(f"Total Records:     {total}")
    print(f"Successful (2xx):  {success}")
    print(f"Failed:            {failed}")
    print(f"Output File Saved: {output_csv}")

    # Upload the saved file to SFTP
    print("\n[SFTP] Uploading output file...")
    upload_to_sftp(sftp_host, sftp_user, sftp_pass, output_csv, output_csv)


# -------------------------------------------------------------------
# CLI ARGUMENTS
# -------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk Delete Resources via Zeta Delete API")

    parser.add_argument("input_csv", help="Input CSV with 'resource_id' column")

    parser.add_argument(
        "--output",
        default="output_results.csv",
        help="Name of output CSV file (default: output_results.csv)"
    )

    parser.add_argument(
        "--site_id",
        required=True,
        help="Site ID used for this deletion run (logged in the output file)"
    )

    parser.add_argument(
        "--username",
        required=True,
        help="Basic Auth username"
    )

    parser.add_argument(
        "--password",
        required=True,
        help="Basic Auth password"
    )

    parser.add_argument(
        "--sftp_host",
        required=True,
        help="SFTP host for uploading the result file"
    )

    parser.add_argument(
        "--sftp_user",
        required=True,
        help="SFTP username"
    )

    parser.add_argument(
        "--sftp_pass",
        required=True,
        help="SFTP password"
    )

    args = parser.parse_args()

    process_file(
        args.input_csv,
        args.output,
        args.site_id,
        args.username,
        args.password,
        args.sftp_host,
        args.sftp_user,
        args.sftp_pass
    )
