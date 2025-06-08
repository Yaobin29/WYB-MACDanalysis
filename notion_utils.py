# notion_utils.py

from notion_client import Client
import os

notion = Client(auth=os.environ.get("NOTION_TOKEN"))
database_id = os.environ.get("NOTION_DATABASE_ID")

def write_macd_to_notion(ticker, date_str, crossover, position, category, reason):
    properties = {
        "股票代码": {
            "title": [
                {
                    "text": {
                        "content": ticker
                    }
                }
            ]
        },
        "日期": {
            "date": {
                "start": date_str
            }
        },
        "金叉/死叉": {
            "select": {
                "name": crossover
            }
        },
        "位置": {
            "select": {
                "name": position
            }
        },
        "类型": {
            "select": {
                "name": category
            }
        },
        "理由": {
            "rich_text": [
                {
                    "text": {
                        "content": reason
                    }
                }
            ]
        }
    }

    notion.pages.create(
        parent={"database_id": database_id},
        properties=properties
    )
