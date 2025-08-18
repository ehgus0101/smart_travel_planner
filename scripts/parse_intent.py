import argparse, json
from app.chat.intent_parser import rule_parse

p = argparse.ArgumentParser()
p.add_argument("--msg", required=True, help="자연어 질의")
args = p.parse_args()

print(json.dumps(rule_parse(args.msg), ensure_ascii=False, indent=2))
