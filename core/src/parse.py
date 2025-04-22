from time import sleep
import psycopg2
import requests


def get_recent_posts(access_token: str, group_id: int, count: int) -> list[int]:
    """Получение ID последних N постов группы"""
    url = "https://api.vk.com/method/wall.get"
    version = "5.199"
    posts = []
    offset = 0

    while len(posts) < count:
        params = {
            "access_token": access_token,
            "v": version,
            "owner_id": f"-{group_id}",
            "offset": offset,
            "count": min(100, count - len(posts)),
            "filter": "owner"
        }

        response = requests.get(url, params=params)
        data = response.json()

        if 'error' in data:
            raise Exception(f"Ошибка получения постов: {data['error']['error_msg']}")

        posts.extend([post['id'] for post in data['response']['items']])
        offset += 100
        sleep(0.5)

        if len(data['response']['items']) < 100:
            break

    return posts[:count]


def parse_vk_comments(access_token: str, group_id: int, posts_count: int, comments_limit: int = 1000) -> list[dict]:
    """Основная функция для парсинга"""
    post_ids = get_recent_posts(access_token, group_id, posts_count)
    all_comments = []

    for post_id in post_ids:
        url = "https://api.vk.com/method/wall.getComments"
        version = "5.199"
        offset = 0

        while offset < comments_limit:
            params = {
                "access_token": access_token,
                "v": version,
                "owner_id": f"-{group_id}",
                "post_id": post_id,
                "offset": offset,
                "count": 100,
                "thread_items_count": 0
            }

            response = requests.get(url, params=params)
            data = response.json()

            if 'error' in data:
                print(f"Ошибка для поста {post_id}: {data['error']['error_msg']}")
                break

            comments = data['response']['items']
            all_comments.extend([{
                "post_id": post_id,
                "comment_id": c['id'],
                "text": c['text'],
                "author_id": c['from_id'],
                "date": c['date']
            } for c in comments])

            offset += 100
            sleep(0.5)

            if len(comments) < 100:
                break

    return all_comments


def save_to_postgres(comments: list[dict], db_params: dict) -> None:
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    for comment in comments:
        cursor.execute('''
            INSERT INTO vk_comments (comment_id, text, author_id, date)
            VALUES (%s, %s, %s, to_timestamp(%s))
            ON CONFLICT (comment_id) DO NOTHING
        ''', (comment['comment_id'],
              comment['text'],
              comment['author_id'],
              comment['date']))

    conn.commit()
    cursor.close()
    conn.close()
