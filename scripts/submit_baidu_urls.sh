#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SITEMAP_FILE="${ROOT_DIR}/sitemap-full.xml"
SITE="${BAIDU_SITE:-mitaojun.com}"
TOKEN="${BAIDU_TOKEN:-}"
BATCH_SIZE="${BAIDU_BATCH_SIZE:-200}"

usage() {
  cat <<'EOF'
Usage:
  submit_baidu_urls.sh --token <token> [--site <domain>] [--sitemap <path>] [--batch-size <n>]

Examples:
  scripts/submit_baidu_urls.sh --token dDODIHx5iul9rQRx
  scripts/submit_baidu_urls.sh --token xxx --site mitaojun.com --sitemap sitemap-full.xml --batch-size 200

Environment variables (optional):
  BAIDU_TOKEN, BAIDU_SITE, BAIDU_BATCH_SIZE
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --token)
      TOKEN="${2:-}"
      shift 2
      ;;
    --site)
      SITE="${2:-}"
      shift 2
      ;;
    --sitemap)
      SITEMAP_FILE="${2:-}"
      shift 2
      ;;
    --batch-size)
      BATCH_SIZE="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "${TOKEN}" ]]; then
  echo "Error: missing token. Provide --token or BAIDU_TOKEN." >&2
  exit 1
fi

if [[ ! -f "${SITEMAP_FILE}" ]]; then
  echo "Error: sitemap file not found: ${SITEMAP_FILE}" >&2
  exit 1
fi

if ! [[ "${BATCH_SIZE}" =~ ^[0-9]+$ ]] || [[ "${BATCH_SIZE}" -le 0 ]]; then
  echo "Error: --batch-size must be a positive integer." >&2
  exit 1
fi

TMP_URLS="$(mktemp)"
TMP_BATCH="$(mktemp)"
cleanup() {
  rm -f "${TMP_URLS}" "${TMP_BATCH}"
}
trap cleanup EXIT

# Extract <loc> URLs from sitemap XML.
sed -n 's:.*<loc>\(.*\)</loc>.*:\1:p' "${SITEMAP_FILE}" > "${TMP_URLS}"

TOTAL="$(wc -l < "${TMP_URLS}" | tr -d ' ')"
if [[ "${TOTAL}" -eq 0 ]]; then
  echo "No URLs found in ${SITEMAP_FILE}"
  exit 0
fi

API="http://data.zz.baidu.com/urls?site=${SITE}&token=${TOKEN}"
echo "Submitting ${TOTAL} URLs to: ${API}"

attempted=0
success_total=0
remain_total=0
not_same_site_total=0
not_valid_total=0
quota_errors=0
other_errors=0
batch_no=0

while IFS= read -r _; do
  :
done < /dev/null

while [[ "${attempted}" -lt "${TOTAL}" ]]; do
  : > "${TMP_BATCH}"
  start=$((attempted + 1))
  end=$((attempted + BATCH_SIZE))
  if [[ "${end}" -gt "${TOTAL}" ]]; then
    end="${TOTAL}"
  fi

  sed -n "${start},${end}p" "${TMP_URLS}" > "${TMP_BATCH}"
  count_this_batch="$(wc -l < "${TMP_BATCH}" | tr -d ' ')"
  batch_no=$((batch_no + 1))

  response="$(
    curl -sS -H 'Content-Type:text/plain' --data-binary @"${TMP_BATCH}" "${API}"
  )"

  success="$(printf '%s' "${response}" | sed -n 's/.*"success":[[:space:]]*\([0-9][0-9]*\).*/\1/p')"
  remain="$(printf '%s' "${response}" | sed -n 's/.*"remain":[[:space:]]*\([0-9][0-9]*\).*/\1/p')"
  not_same_site="$(printf '%s' "${response}" | sed -n 's/.*"not_same_site":[[:space:]]*\([0-9][0-9]*\).*/\1/p')"
  not_valid="$(printf '%s' "${response}" | sed -n 's/.*"not_valid":[[:space:]]*\([0-9][0-9]*\).*/\1/p')"
  error_code="$(printf '%s' "${response}" | sed -n 's/.*"error":[[:space:]]*\([0-9][0-9]*\).*/\1/p')"
  error_msg="$(printf '%s' "${response}" | sed -n 's/.*"message":"\([^"]*\)".*/\1/p')"

  success="${success:-0}"
  remain="${remain:-0}"
  not_same_site="${not_same_site:-0}"
  not_valid="${not_valid:-0}"

  success_total=$((success_total + success))
  remain_total=$((remain_total + remain))
  not_same_site_total=$((not_same_site_total + not_same_site))
  not_valid_total=$((not_valid_total + not_valid))

  if [[ -n "${error_code}" ]]; then
    if [[ "${error_msg}" == "over quota" ]]; then
      quota_errors=$((quota_errors + 1))
    else
      other_errors=$((other_errors + 1))
    fi
  fi

  echo "Batch #${batch_no} (${count_this_batch} URLs): ${response}"
  attempted=$((attempted + count_this_batch))
done

echo "Done. Attempted ${attempted}/${TOTAL} URLs."
echo "Accepted by Baidu: success=${success_total}, remain=${remain_total}, not_same_site=${not_same_site_total}, not_valid=${not_valid_total}"
echo "Errors: over_quota_batches=${quota_errors}, other_error_batches=${other_errors}"
