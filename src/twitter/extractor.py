import ast
import json
import os
import re
import tempfile
from datetime import datetime
from functools import lru_cache

import emoji
import ijson
from openpyxl import Workbook


SUPPORTED_OUTPUT_FORMATS = {"csv", "xlsx"}
DEFAULT_CHUNK_SIZE = 5000


def extract_twitter_features(input_file, selected_features, output_format="xlsx"):
    """Extract selected features from a tweets file using low-memory streaming."""
    if output_format not in SUPPORTED_OUTPUT_FORMATS:
        raise ValueError(f"Unsupported output format: {output_format}")

    if not selected_features:
        raise ValueError("At least one feature must be selected")

    file_ext = input_file.rsplit(".", 1)[1].lower()
    output_path = os.path.join(tempfile.gettempdir(), f"tweets_extracted.{output_format}")

    writer = _RowWriter(output_path, output_format, selected_features)
    try:
        for record in _iter_records(input_file, file_ext, DEFAULT_CHUNK_SIZE):
            row = [_extract_feature(record, feature) for feature in selected_features]
            writer.write_row(row)
        writer.close()
    except Exception:
        writer.close()
        raise

    return output_path


class _RowWriter:
    """Progressively write rows to CSV or XLSX without storing full dataset in memory."""

    def __init__(self, output_path, output_format, headers):
        self.output_path = output_path
        self.output_format = output_format
        self.closed = False

        if output_format == "csv":
            self._file = open(output_path, "w", encoding="utf-8", newline="")
            self._writer = csv.writer(self._file)
            self._writer.writerow(headers)
        else:
            self._workbook = Workbook(write_only=True)
            self._sheet = self._workbook.create_sheet("tweets")
            self._sheet.append(headers)

    def write_row(self, row):
        if self.output_format == "csv":
            self._writer.writerow(row)
        else:
            self._sheet.append(row)

    def close(self):
        if self.closed:
            return

        if self.output_format == "csv":
            self._file.close()
        else:
            self._workbook.save(self.output_path)

        self.closed = True


def _iter_records(input_file, file_ext, chunk_size):
    """Twitter JS files only."""
    if file_ext != "js":
        raise ValueError(f"Only .js format is supported, got: {file_ext}")
    yield from _iter_js_records(input_file)


def _iter_js_records(file_path):
    temp_json_path = _convert_twitter_js_to_json_file(file_path)
    try:
        with open(temp_json_path, "r", encoding="utf-8") as f:
            for item in ijson.items(f, "item"):
                yield _normalize_record(item)
    finally:
        if os.path.exists(temp_json_path):
            os.remove(temp_json_path)


def _convert_twitter_js_to_json_file(js_path):
    """Convert 'window.YTD.tweets.partX = [...]' file to a temporary pure JSON array file."""
    temp_fd, temp_path = tempfile.mkstemp(suffix=".json")
    os.close(temp_fd)

    with open(js_path, "r", encoding="utf-8", errors="ignore") as src, open(
        temp_path, "w", encoding="utf-8"
    ) as dst:
        first_line_processed = False

        for line in src:
            if not first_line_processed:
                if "=" in line:
                    line = line.split("=", 1)[1]
                first_line_processed = True

            dst.write(line)

    _trim_trailing_semicolon(temp_path)
    return temp_path


def _trim_trailing_semicolon(file_path):
    with open(file_path, "rb+") as f:
        f.seek(0, os.SEEK_END)
        pos = f.tell() - 1

        while pos >= 0:
            f.seek(pos)
            byte = f.read(1)

            if byte in b" \t\r\n":
                pos -= 1
                continue

            if byte == b";":
                f.seek(pos)
                f.truncate()
            break


def _normalize_record(item):
    if isinstance(item, dict) and "tweet" in item and isinstance(item["tweet"], dict):
        return item["tweet"]
    return item if isinstance(item, dict) else {}


def _extract_feature(record, feature):
    if feature == "content":
        return _extract_content(record)
    if feature == "date":
        return _extract_date(record)
    if feature == "hashtags":
        return _extract_hashtags(record)
    if feature == "mentions":
        return _extract_mentions(record)
    if feature == "favorite_count":
        return _extract_favorite_count(record)
    if feature == "retweet_count":
        return _extract_retweet_count(record)
    if feature == "has_media":
        return _extract_has_media(record)
    if feature == "mention_count":
        return _extract_mention_count(record)
    if feature == "emojis":
        return _extract_emojis(record)
    return ""


def _extract_content(record):
    for key in ["full_text", "text", "content", "tweet", "message", "body"]:
        val = record.get(key)
        if val is not None and str(val).strip() != "":
            return str(val)
    return ""


def _extract_date(record):
    for key in ["created_at", "date", "timestamp", "time"]:
        raw = record.get(key)
        if raw is None or str(raw).strip() == "":
            continue

        normalized = _normalize_date_fast(str(raw))
        if normalized:
            return normalized

    return ""


@lru_cache(maxsize=20000)
def _normalize_date_fast(raw):
    """Normalize common date formats with low overhead for large datasets."""
    value = raw.strip()
    if not value:
        return ""

    # Fast path for already normalized/ISO-like strings.
    if len(value) >= 19 and value[4:5] == "-" and value[7:8] == "-":
        candidate = value[:19].replace("T", " ")
        if candidate[10:11] == " " and candidate[13:14] == ":" and candidate[16:17] == ":":
            return candidate

    # Native Twitter format: Sat Oct 01 18:01:20 +0000 2016
    try:
        dt = datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass

    # ISO fallback (e.g. 2024-01-02T10:00:00Z)
    try:
        iso_value = value.replace("Z", "+00:00") if value.endswith("Z") else value
        dt = datetime.fromisoformat(iso_value)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return ""


def _extract_hashtags(record):
    entities = _parse_entities(record.get("entities"))
    hashtags = entities.get("hashtags") if isinstance(entities, dict) else None

    if isinstance(hashtags, list):
        tags = [h.get("text", "") for h in hashtags if isinstance(h, dict) and h.get("text")]
        if tags:
            return ", ".join(tags)

    return ", ".join(re.findall(r"#\w+", _extract_content(record)))


def _extract_mentions(record):
    entities = _parse_entities(record.get("entities"))
    mentions = entities.get("user_mentions") if isinstance(entities, dict) else None

    if isinstance(mentions, list):
        names = [
            m.get("screen_name", "")
            for m in mentions
            if isinstance(m, dict) and m.get("screen_name")
        ]
        if names:
            return ", ".join(names)

    return ", ".join(re.findall(r"@\w+", _extract_content(record)))


def _extract_favorite_count(record):
    for key in ["favorite_count", "likes", "fav_count", "favorites"]:
        val = record.get(key)
        if val is not None and str(val).strip() != "":
            try:
                return int(float(val))
            except (ValueError, TypeError):
                return 0
    return 0


def _extract_retweet_count(record):
    for key in ["retweet_count", "retweets", "rt_count"]:
        val = record.get(key)
        if val is not None and str(val).strip() != "":
            try:
                return int(float(val))
            except (ValueError, TypeError):
                return 0
    return 0


def _extract_has_media(record):
    entities = _parse_entities(record.get("entities"))
    if isinstance(entities, dict):
        media = entities.get("media")
        if isinstance(media, list) and media:
            return True

    for key in ["media", "has_media", "media_url", "image_url", "video_url"]:
        val = record.get(key)
        if val in [None, "", "nan", "NaN"]:
            continue
        if isinstance(val, bool):
            return val
        return True

    return False


def _extract_mention_count(record):
    mentions = _extract_mentions(record)
    if not mentions.strip():
        return 0
    return len([x for x in mentions.split(",") if x.strip()])


def _extract_emojis(record):
    text = _extract_content(record)
    emojis_found = [c for c in text if c in emoji.EMOJI_DATA]
    return ", ".join(emojis_found)


def _parse_entities(raw_entities):
    if isinstance(raw_entities, dict):
        return raw_entities

    if raw_entities is None:
        return {}

    if not isinstance(raw_entities, str):
        return {}

    text = raw_entities.strip()
    if not text:
        return {}

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, dict):
            return parsed
    except (ValueError, SyntaxError):
        pass

    return {}
