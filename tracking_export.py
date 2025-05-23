import csv
import io
import json
import logging
import os
import sys
import tempfile
import codecs
import time
from dotenv import load_dotenv
import labelbox as lb
from labelbox.schema.export_task import ExportTask
from collections import defaultdict

# Force UTF-8 encoding for stdout and stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='backslashreplace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='backslashreplace')

# Set environment variable for UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Basic logging setup with UTF-8 encoding
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])


# First, check environment variables
LABELBOX_API_KEY = os.getenv("LABELBOX_API_KEY")

# Fallback to .env file (for local use)
if not LABELBOX_API_KEY:
    load_dotenv(override=True)  # Explicitly allow overriding from environment variables
    LABELBOX_API_KEY = os.getenv("LABELBOX_API_KEY")

# Raise an error if the API key is still missing
if not LABELBOX_API_KEY:
    raise ValueError("Labelbox API Key is not set in environment variables or .env file!")

# Use the API key in the client
client = lb.Client(api_key=LABELBOX_API_KEY)

DOWNLOAD_PATH = os.path.join(os.getcwd(), "exports")


def custom_encode_error_handler(error):
    return ('?', error.start + 1)

codecs.register_error('custom_encode_handler', custom_encode_error_handler)

# Patch the ExportTask class to use UTF-8 encoding in all file operations
def patched_read(self):
    for file_info, raw_data in self._stream:
        with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as temp_file:
            if isinstance(raw_data, str):
                raw_data = raw_data.encode('utf-8', errors='custom_encode_handler')
            temp_file.write(raw_data)
            temp_file.flush()
            temp_file.close()
            with open(temp_file.name, 'rb') as f:
                data = f.read().decode('utf-8', errors='replace')
                yield file_info, data

# Apply the monkey patch to the ExportTask class
ExportTask.read = patched_read

export_params = {
    "data_row_details": True,
    "metadata_fields": True,
    "attachments": True,
    "project_details": True,
    "performance_details": True,
    "label_details": True,
    "interpolated_frames": False,
    "embeddings": False
}

filters = {
}

project_categories = {
  "Key_Evidence_Fiction_Final_Round":
  [
    "cm8yl6jcb011r07x22wbo8hll",
    "cm8yl63tz00p407yja176byza",
    "cm8yl5ni900td07w60ruc7acl",
    "cm8yl58rt00tm07yk1ht539h3",
    "cm8yl4tc200le07z0hgyy30u1",
    "cm8yl4dm700ub07xi50sf1gsa",
    "cm8yl3y1r00pc07wy79pj0ir7",
    "cm8yl3idh00mf07xn1t757grj",
    "cm8yl32ae00eo07wy5hfldxcs",
    "cm8yl2o0100l207yk8qxfa307",
    "cm8yl285l01gx07xnbxqlfqpg"
  ],

  "Vocab_C_HS":
  [
    "cm8digysu0gg007yla1f24fi3",
    "cm8dig3790cd1070s9wem8it7",
    "cm8dif7wq09mz07zz1k7vd9eo",
    "cm8diee8k0c51072n9mue3wgk"
  ],
    
  "Core_Reader_E_All":
  [
    "cm7tqgq6704jy07zw3ex83467",
    "cm7tqfs1f05ru071t1yhl6n4y",
    "cm7tqelup09d3070ediyzbbed",
    "cm7tpe3bs06yg07y76jmk4mna",
    "cm7tpd7y905yq07uz5f12hhu8",
    "cm7tpc48r00q607zxfqgz08zb",
    "cm7tpayam071d070e8127a5ql",
    "cm7tpa0ng06zx07zeen8w5puz",
    "cm7tp8vf80625071g52iu08u2",
    "cm7tp6zz301xa07zwgijq9hjk"
  ],
  "Core_Reader_D_All":
  [
    "cm6tujia7077507zw9lnl9ape",
    "cm6tuitzh03gt070od3hdasx1",
    "cm6tui6e8074n07zwhkuw29rl",
    "cm6tuhgec0khj073ce83601ri",
    "cm6tugv9k072b07zwd3522k8j",
    "cm6tug3zw071107zwcgnk1v6s",
    "cm6tufguj0cmv072d418rc8ma",
    "cm6tueurg0oyx07333s2b747y",
    "cm6tudzwz0ion07098zvqf1o9",
    "cm6tud3qd04fb07yx1lhm0kxz",
    "cm6tuc3a00k91073c96d572ft"
  ],  
  "Core_Reader_C_Lower_Upper_Middle":
  [
    "cm6tu8uua07bq071e4bqv0f7t",
    "cm6tu838t07s7071e54wxa12o",
    "cm6tu74nv08wz07zm9sowgvbo",
    "cm6tu66v4077e071e1fw54u5l",
    "cm6tu5cf00c6g072dbn8p50ck",
    "cm6tu4e4403rb071b4nqf5cpt",
    "cm6tu3h490270072ubd5gg4qn",
    "cm6tu2o2a0jvm073cfsdg955i",
    "cm6tu1l2k00bq072f9qwu1y57",
    "cm6tu0mp20byh072d2yww75ix",
    "cm6ttznbk0jre073c6lya577x",
    "cm6ttyhar03u607yxhj9nez50",
    "cm6ttwt1t0feu0703grenfwrv",
    "cm6ttvnov002a072f00m94xnk"
  ],
  "Core_Reader_C_High_School":
  [
      "cm66znmw90eyx07271qgj0g71",
      "cm66zn5v10hrz071s2f2ifkzw",
      "cm66zh03c0a84073m75cw3a1c",
      "cm66zg4ad0gxq071sbbfdfcah",
      "cm66zegrg0hvy071bhlsl212f",
      "cm66zdg1h09qr071oauybdt5b",
      "cm66zcggq0hku073601v61du4",
      "cm66z7o9d09f3072tbp12frns",
  ],
  "Core_Reader_B_2nd_to_8th":
  [
      "cm66uqoll00wx07y65f7i14js",
      "cm66ups5y04ih071b8fsdb15z",
      "cm66uortn03sm071o055d40pw",
      "cm66untag0h7x0706e1fqew7r",
      "cm66umtwa0fw5072bejzm25yy",
      "cm66ulvq70fho073adzg62nf2",
      "cm66ukd0n032n070shez40b9f",
      "cm66ujg1o0fpi072b44wb9uwr",
      "cm66ui6ut03fu071sgr8q0hz7",
      "cm66uh6e00gwu07067nr4bvrs",
      "cm66ug0ez03fi071ocgt44pzv",
      "cm66uezne03zt07366rn96y9e",
      "cm66ucvcj0fmg07xbeqo26hlp",
      "cm66ubdeq0gml0706aiwk6rsb",
  ],

  "Core_Reader_A_Batch_2":
  [
      "cm56yto58029j070c8f0mb4g7",
      "cm56ystwv102c07ziftps4nw2",
      "cm56ys1d913mx07z7dxr4erxz",
      "cm56yr4jn0tgf07zhd4a7hbcv",
      "cm56yq07v0erk07xi752weo0c",
      "cm56yp5lq03bt070j9zyt4e3m",
      "cm56yoar313h807z7dcrmf7zn",
      "cm56ynh6l13xc072c5ni709vf",
      "cm56ymbcl13eb07z7hl0284qu",
      "cm56ykcsl03qf07y78dv6buqs",
      "cm56yj0oc0l22070z19md4n5j",
  ],
  "Core_Reader_A_Batch_1": [
      "cm4j0z7u601b0073tcav1flz6",
      "cm4j0xtxy01e2072q0f8gcg6r",
      "cm4j0x7i201bf072n3h825725",
      "cm4j0wb0p019r076ffqfhhnt9",
      "cm4j0vl36018o076f9oyd27mh",
      "cm4j0uroj0199072ie1hna2q3",
      "cm4j0u1jl017a07296waeavjm",
      "cm4j0t81z0169074qcdwz3has",
      "cm4j0sb5x016y072qdepx9uju",
      "cm4j0re6m011v07394fu25lgd",
      "cm4j0mw7a011r076hhm2wbwxj",
    ]
}



def sanitize_text(text):
    if isinstance(text, str):
        return text.encode('utf-8', errors='backslashreplace').decode('utf-8')
    return str(text)

def recursive_sanitize(data):
    if isinstance(data, dict):
        return {sanitize_text(k): recursive_sanitize(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [recursive_sanitize(item) for item in data]
    elif isinstance(data, str):
        return sanitize_text(data)
    else:
        return data

def export_with_retries(project, params, filters, retries=5, delay=5):
    for attempt in range(retries):
        try:
            export_task = project.export_v2(params=params, filters=None)
            export_task.wait_till_done()

            if export_task.errors:
                logging.error("Errors during data export for project %s: %s", project.uid, export_task.errors)
                return None

            if export_task.has_result():
                result = []
                for result_item in export_task.result:
                    if isinstance(result_item, dict):
                        if 'data_row' in result_item and 'projects' in result_item:
                            data = result_item
                        else:
                            logging.warning("Unexpected structure in result item: %s", result_item)
                            continue
                    else:
                        logging.warning("Unexpected result item type: %s. Item: %s", type(result_item), result_item)
                        continue
                    result.append(data)
                return recursive_sanitize(result)
            else:
                logging.error("No results found for project %s", project.uid)
                return None

        except lb.exceptions.LabelboxError as e:
            logging.warning("Attempt %d failed with error: %s", attempt + 1, e)
            if attempt < retries - 1:
                logging.info("Retrying in %d seconds...", delay)
                time.sleep(delay)
            else:
                raise
        except Exception as e:
            logging.error("Unexpected error during export: %s", str(e))
            raise

def process_data_row(data_row):
    return {
        "row_data": data_row.get("row_data", ""),
        "global_key": data_row.get("global_key", ""),
        "dataset_id": data_row.get("details", {}).get("dataset_id", None),
        "dataset_name": data_row.get("details", {}).get("dataset_name", None),
        "created_at": data_row.get("details", {}).get("created_at", None),
        "updated_at": data_row.get("details", {}).get("updated_at", None),
        "last_activity_at": data_row.get("details", {}).get("last_activity_at", None),
    }

def process_projects_with_classifications(project_data):
    processed_project = {}
    labels = project_data.get("labels", [])

    # Dictionary to store aggregated stats per rater
    rater_stats = defaultdict(lambda: {"items_labeled": 0, "total_time_seconds": 0})

    for idx, label in enumerate(labels):
        label_details = label.get("label_details", {})
        email = label_details.get("created_by", "unknown")

        # Update rater stats
        performance = label.get("performance_details", {})
        rater_stats[email]["items_labeled"] += 1
        rater_stats[email]["total_time_seconds"] += performance.get("seconds_to_create", 0)

    # Add aggregated stats to the processed project dictionary
    for idx, (email, stats) in enumerate(rater_stats.items()):
        suffix = f"_{idx + 1}"
        processed_project[f"labeller{suffix}_email"] = email
        processed_project[f"labeller{suffix}_items_labeled"] = stats["items_labeled"]
        processed_project[f"labeller{suffix}_time_minutes"] = round(stats["total_time_seconds"] / 60, 2)

    return processed_project

def map_metadata_fields(metadata):
    mapped_data = {}
    for field in metadata:
        schema_name = field.get('schema_name', '').replace(" ", "_")
        mapped_data[f'{schema_name}_schema_ID'] = field.get('schema_id', None)
        mapped_data[f'{schema_name}_schema_kind'] = field.get('schema_kind', None)
        mapped_data[f'{schema_name}_value'] = field.get('value', None)
    return mapped_data

def generate_headers():
    base_headers = [
        "dataset_name", "row_data", "created_at", "dataset_id",
        "Sentence_Count_schema_ID", "Sentence_Count_schema_kind", "Sentence_Count_value",
        "Word_Count_schema_ID", "Word_Count_value", "Word_Count_schema_kind",
        "Dale_Chall_Grade_schema_kind", "Dale_Chall_Grade_schema_ID", "Dale_Chall_Grade_value",
        "Flesch_Kincaid_Grade_schema_ID", "Flesch_Kincaid_Grade_schema_kind", "Flesch_Kincaid_Grade_value",
        "Spache_Grade_value", "Spache_Grade_schema_kind", "Spache_Grade_schema_ID",
        "Final_Score_schema_kind", "Final_Score_value", "Final_Score_schema_ID",
        "UUID_schema_ID", "UUID_value", "UUID_schema_kind", "embeddings"
    ]

    # Add dynamic fields for raters (assuming a max of 10 raters for simplicity)
    for i in range(1, 11):
        base_headers.extend([
            f"labeller_{i}_email",
            f"labeller_{i}_items_labeled",
            f"labeller_{i}_time_minutes"
        ])

    return base_headers

def process_ndjson(ndjson_file_path, csv_file_name):
    headers = generate_headers()

    with codecs.open(csv_file_name, 'w', encoding='utf-8-sig', errors='backslashreplace') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=headers)
        csv_writer.writeheader()

        with codecs.open(ndjson_file_path, 'r', encoding='utf-8', errors='replace') as ndjson_file:
            for line in ndjson_file:
                try:
                    data = json.loads(line)
                    flattened_item = {}

                    if 'data_row' in data:
                        flattened_item.update(process_data_row(data['data_row']))

                    if 'metadata_fields' in data:
                        flattened_item.update(map_metadata_fields(data['metadata_fields']))

                    if 'projects' in data:
                        for project_key, project_data in data['projects'].items():
                            flattened_item.update(process_projects_with_classifications(project_data))

                    if 'embeddings' in data:
                        flattened_item['embeddings'] = str(data['embeddings'])

                    sanitized_row = {field: sanitize_text(str(flattened_item.get(field, ''))) for field in headers}
                    csv_writer.writerow(sanitized_row)

                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding JSON: {e}")
                    logging.error(f"Problematic line: {line}")
                except Exception as e:
                    logging.error(f"Error processing line: {e}")
                    logging.error(f"Problematic line: {line}")

def main():
    for category, project_ids in project_categories.items():
        category_path = os.path.join(DOWNLOAD_PATH, sanitize_text(category.replace(" ", "_")))

        # Ensure the category folder exists
        os.makedirs(category_path, exist_ok=True)

        for project_id in project_ids:
            try:
                project = client.get_project(project_id)
                project_name = sanitize_text(project.name.replace(" ", "_"))

                logging.info(f"Processing project: {project_name} in category: {category}")

                export_json = export_with_retries(project, export_params, filters)

                if export_json is None:
                    logging.error(f"Failed to export data for project {project_id}")
                    continue

                ndjson_file_name = os.path.join(category_path, f'{project_name}_export.ndjson')
                csv_file_name = os.path.join(category_path, f'{project_name}_export.csv')

                try:
                    # Write NDJSON file
                    with codecs.open(ndjson_file_name, 'w', encoding='utf-8', errors='custom_encode_handler') as ndjson_file:
                        for item in export_json:
                            json.dump(item, ndjson_file, ensure_ascii=False)
                            ndjson_file.write('\n')
                    logging.info(f"NDJSON file saved locally at {ndjson_file_name}")
                except IOError as e:
                    logging.error(f"Failed to save NDJSON file: {e}")

                try:
                    # Process to CSV
                    process_ndjson(ndjson_file_name, csv_file_name)
                    logging.info(f"CSV file saved locally at {csv_file_name}")
                except IOError as e:
                    logging.error(f"Failed to save CSV file: {e}")

            except Exception as e:
                logging.error(f"An error occurred with project ID {project_id}: {str(e)}")
                logging.exception("Exception details:")

    logging.info("Processing completed for all projects.")

if __name__ == "__main__":
    main()
