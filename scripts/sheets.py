"""Read and write Google Sheets through the Sheets API.

Credentials live outside the repo, in ~/.config/claude-sheets/ (override with
CLAUDE_SHEETS_DIR):
  credentials.json  OAuth "Desktop app" client from Google Cloud Console
  token.json        created by `auth`; refreshes itself

Scope is spreadsheets only: no access to Gmail, Calendar or other Drive files.

Usage:
  python scripts/sheets.py auth
  python scripts/sheets.py tabs   <spreadsheet>
  python scripts/sheets.py get    <spreadsheet> <A1 range> [--formulas]
  python scripts/sheets.py set    <spreadsheet> <A1 range> (--json JSON | --file PATH) [--raw]
  python scripts/sheets.py append <spreadsheet> <A1 range> (--json JSON | --file PATH) [--raw]
  python scripts/sheets.py clear  <spreadsheet> <A1 range>
  python scripts/sheets.py add-tab    <spreadsheet> <title>
  python scripts/sheets.py delete-tab <spreadsheet> <title>
  python scripts/sheets.py batch  <spreadsheet> (--json JSON | --file PATH)

<spreadsheet> is a spreadsheet ID or its full docs.google.com URL.
Values for set/append are a JSON list of rows, e.g. '[["Name","City"],["Ana","Montreal"]]'.
By default values are parsed like typing into the UI (USER_ENTERED, so formulas
work); pass --raw to store text exactly as given.
`batch` takes a list of batchUpdate requests (formatting, validation, etc.).
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CONFIG_DIR = Path(os.environ.get("CLAUDE_SHEETS_DIR", Path.home() / ".config" / "claude-sheets"))
CREDENTIALS = CONFIG_DIR / "credentials.json"
TOKEN = CONFIG_DIR / "token.json"


def get_credentials(interactive=False):
    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not interactive:
            sys.exit("Not signed in. Run: python scripts/sheets.py auth")
        if not CREDENTIALS.exists():
            sys.exit(f"Missing {CREDENTIALS}")
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)
    TOKEN.write_text(creds.to_json())
    return creds


def service():
    return build("sheets", "v4", credentials=get_credentials(), cache_discovery=False).spreadsheets()


def spreadsheet_id(value):
    m = re.search(r"/spreadsheets/d/([A-Za-z0-9_-]+)", value)
    return m.group(1) if m else value


def load_json(args):
    if args.json is not None:
        return json.loads(args.json)
    if args.file:
        return json.loads(Path(args.file).read_text(encoding="utf-8"))
    return json.load(sys.stdin)


def sheet_id(svc, sid, title):
    meta = svc.get(spreadsheetId=sid, fields="sheets.properties").execute()
    for s in meta["sheets"]:
        if s["properties"]["title"] == title:
            return s["properties"]["sheetId"]
    sys.exit(f"No tab named {title!r}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("auth")
    for name in ("tabs", "get", "set", "append", "clear", "add-tab", "delete-tab", "batch"):
        sp = sub.add_parser(name)
        sp.add_argument("spreadsheet")
        if name in ("get", "set", "append", "clear"):
            sp.add_argument("range")
        if name in ("add-tab", "delete-tab"):
            sp.add_argument("title")
        if name in ("set", "append", "batch"):
            sp.add_argument("--json")
            sp.add_argument("--file")
        if name in ("set", "append"):
            sp.add_argument("--raw", action="store_true")
        if name == "get":
            sp.add_argument("--formulas", action="store_true")
    args = p.parse_args()

    if args.cmd == "auth":
        get_credentials(interactive=True)
        print(f"Signed in. Token saved to {TOKEN}")
        return

    svc = service()
    sid = spreadsheet_id(args.spreadsheet)
    values = svc.values()

    if args.cmd == "tabs":
        meta = svc.get(spreadsheetId=sid, fields="properties.title,sheets.properties").execute()
        out = {
            "title": meta["properties"]["title"],
            "tabs": [
                {
                    "title": s["properties"]["title"],
                    "sheetId": s["properties"]["sheetId"],
                    "rows": s["properties"]["gridProperties"]["rowCount"],
                    "cols": s["properties"]["gridProperties"]["columnCount"],
                }
                for s in meta["sheets"]
            ],
        }
    elif args.cmd == "get":
        render = "FORMULA" if args.formulas else "FORMATTED_VALUE"
        out = values.get(spreadsheetId=sid, range=args.range, valueRenderOption=render).execute()
    elif args.cmd in ("set", "append"):
        body = {"values": load_json(args)}
        opt = "RAW" if args.raw else "USER_ENTERED"
        if args.cmd == "set":
            out = values.update(spreadsheetId=sid, range=args.range, valueInputOption=opt, body=body).execute()
        else:
            out = values.append(
                spreadsheetId=sid, range=args.range, valueInputOption=opt,
                insertDataOption="INSERT_ROWS", body=body,
            ).execute()
    elif args.cmd == "clear":
        out = values.clear(spreadsheetId=sid, range=args.range, body={}).execute()
    elif args.cmd == "add-tab":
        out = svc.batchUpdate(
            spreadsheetId=sid, body={"requests": [{"addSheet": {"properties": {"title": args.title}}}]}
        ).execute()
    elif args.cmd == "delete-tab":
        out = svc.batchUpdate(
            spreadsheetId=sid,
            body={"requests": [{"deleteSheet": {"sheetId": sheet_id(svc, sid, args.title)}}]},
        ).execute()
    elif args.cmd == "batch":
        out = svc.batchUpdate(spreadsheetId=sid, body={"requests": load_json(args)}).execute()

    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
