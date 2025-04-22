import os
from argparse import ArgumentParser
from dotenv import load_dotenv

from src.analyze import get_all_comments_text, clear_text, estimate_sentiment
from src.parse import parse_vk_comments, save_to_postgres
from src.visual import make_plot, make_filtered_plot, make_ensemble_plot

load_dotenv()

DATABASE_CREDENTIALS: dict[str, str] = {
    'dbname': os.getenv("DATABASE_NAME"),
    'user': os.getenv("DATABASE_USER"),
    'password': os.getenv("DATABASE_PASSWORD"),
    'host': os.getenv("DATABASE_HOST"),
    'port': os.getenv("DATABASE_PORT")
}

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        'mode',
        type=str,
        help='script mode: login, parse, analyze',
        default="login",
        choices=["login", "parse", "analyze"],
    )

    args = parser.parse_args()
    app_mode: str = args.mode

    match app_mode:
        case "login":
            import webbrowser

            uri = (f"https://oauth.vk.com/authorize?"
                   f"client_id={os.getenv('VK_APP_ID')}&"
                   f"display=page&"
                   f"redirect_uri=https://oauth.vk.com/blank.html&"
                   f"scope=wall,offline&"
                   f"response_type=token&"
                   f"v=5.131")
            webbrowser.open(uri, new=0, autoraise=True)
        case "parse":
            VK_TOKEN = os.getenv("VK_ACCESS_TOKEN")
            GROUP_ID = int(os.getenv("VK_GROUP_ID"))
            POSTS_TO_CHECK = int(os.getenv("VK_POSTS_TO_CHECK"))
            comments_data = parse_vk_comments(VK_TOKEN, GROUP_ID, POSTS_TO_CHECK)
            save_to_postgres(comments_data, DATABASE_CREDENTIALS)
            print(f"Обработано {len(comments_data)} комментариев из {POSTS_TO_CHECK} последних постов")
        case "analyze":
            comments: list[str] = get_all_comments_text(DATABASE_CREDENTIALS)
            texts: list[str] = []
            for i, comment in enumerate(comments):
                cleared = clear_text(comment)
                print(f"{i}: cleared: {cleared}")
                texts.append(cleared)
            sentiments = estimate_sentiment(texts)
            make_plot(sentiments)
            make_filtered_plot(sentiments)
            make_ensemble_plot(sentiments)

