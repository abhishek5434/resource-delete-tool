# Resource Delete Automation Tool  
A lightweight Python-based automation tool used to delete resources in bulk using the Zeta Delete Resource API.  
The tool reads a CSV containing `resource_id`, performs authenticated DELETE calls with retry logic, generates a results file, and uploads it to an SFTP `/file_share` directory.

This project demonstrates:
- API integration (Basic Auth, headers, retry handling)
- Data engineering workflow (CSV ingestion → processing → result generation)
- SFTP file delivery
- Error handling & logging
- Command-line interface design

## Features

### Bulk Delete via API  
Reads a CSV of `resource_id` values and triggers deletion using the Zeta Delete API.

### Retry Logic  
If a delete call fails, the tool automatically retries **one additional time**.

### Basic Authentication Support  
The tool supports APIs that require:

Authorization: Basic <base64(username:password)>
Content-Type: application/json
Accept: application/json

###  Result File Generation  
Produces an output CSV containing:

```
resource_id,site_id,response_code,response_text
```

### SFTP Upload  
Automatically uploads the result file to:

```
/file_share/<output_filename>
````

### CLI-based  
Easily run the tool with command-line arguments.

---

## Input CSV Format

Input file must contain **only one column**:

```csv
resource_id
12345
67890
11111
```

## Usage

Run the script with:

```bash
python resource_delete_tool.py input.csv \
  --site_id mysite \
  --username myUser \
  --password myPass \
  --sftp_host sftp.example.com \
  --sftp_user my_sftp_user \
  --sftp_pass my_sftp_password \
  --output results_mysite.csv
```

### Arguments

| Argument      | Required | Description                                     |
| ------------- | -------- | ----------------------------------------------- |
| `input_csv`   | Yes      | Path to CSV file containing `resource_id`       |
| `--site_id`   | Yes      | Site identifier logged in output                |
| `--username`  | Yes      | Username for Basic Auth                         |
| `--password`  | Yes      | Password for Basic Auth                         |
| `--sftp_host` | Yes      | SFTP hostname                                   |
| `--sftp_user` | Yes      | SFTP username                                   |
| `--sftp_pass` | Yes      | SFTP password                                   |
| `--output`    | No       | Output filename (default: `output_results.csv`) |


## 📤 Output File Example

```csv
resource_id,site_id,response_code,response_text
12345,mysite,200,OK
67890,mysite,404,Not Found
11111,mysite,500,Internal Server Error
```

Uploaded automatically to:

```
/file_share/<output_filename>
```


## 🙌 Author

Abhishek Raj
Lead Senior Business Systems Analyst | Aspiring Solutions Architect

GitHub: [https://github.com/abhishek5434](https://github.com/abhishek5434)
LinkedIn: [https://www.linkedin.com/in/abhishek-raj-2991851b7/](https://www.linkedin.com/in/abhishek-raj-2991851b7/)
