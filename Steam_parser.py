import requests
from bs4 import BeautifulSoup
from typing import List


class Badges:
    def __init__(self, id: int, title: str, achievements: str):
        self.id = id
        self.title = title
        self.achievements = achievements

    def __str__(self):
        return f"Badge(ID={self.id}, Title={self.title}, Achievements={self.achievements})"


class User:
    def __init__(self, steam_id: int, username: str, level: int, badges: List[Badges]):
        self.steam_id = steam_id
        self.username = username
        self.level = level
        self.badges = badges

    def __str__(self):
        return f"User(SteamID={self.steam_id}, Username={self.username}, Level={self.level}, Badges={len(self.badges)})"


class Friend:
    def __init__(self, friend_id: int, username: str):
        self.friend_id = friend_id
        self.username = username

    def __str__(self):
        return f"Friend(ID={self.friend_id}, Username={self.username})"


class SteamParser:
    def __init__(self):
        self.badges_list = []
        self.users_list = []
        self.friends_list = []

    def parse_badges(self, url: str):
        """Метод для парсинга данных о значках."""
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск значков
        badges = soup.find_all('div', class_='badge_row is_link')

        for badge in badges:
            title_element = badge.find('div', class_='badge_info_title')
            title = title_element.text.strip() if title_element else "Unknown"

            achievements_element = badge.find('div', class_='badge_info_unlocked')
            # print(achievements_element)
            achievements = str(achievements_element.text.strip() if achievements_element else "0")
            # print(achievements)

            new_badge = Badges(
                id=len(self.badges_list) + 1,
                title=title,
                achievements=achievements,
            )

            self.badges_list.append(new_badge)

    def parse_user(self, steam_id: int, url: str):
        """Метод для парсинга данных о пользователе."""
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Парс пользователя
        username_element = soup.find('span', class_='actual_persona_name')
        username = username_element.text.strip() if username_element else "Unknown"

        # Парс уровня
        level_element = soup.find('span', class_='friendPlayerLevelNum')
        level = int(level_element.text.strip()) if level_element else 0

        # Парс значков
        badges = []
        badge_items = soup.find_all('div', class_='badge_card')

        for item in badge_items:
            title_element = item.find('div', class_='badge_info')
            title = title_element.text if title_element else "Unknown"

            achievements_element = item.find('div', class_='badge_info_unlocked')
            achievements = achievements_element.text.strip() if achievements_element else "0"

            badge = Badges(
                id=len(self.badges_list) + 1,
                title=title,
                achievements=achievements,
            )
            badges.append(badge)

        new_user = User(
            steam_id=steam_id,
            username=username,
            level=level,
            badges=badges,
        )
        self.users_list.append(new_user)

    def parse_friends(self, steam_id: int, url: str):
        # Парс друзей пользователя.
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск всех друзей
        friends = soup.find_all('div', class_='selectable')

        for friend in friends:
            friend_id = friend.get('data-steamid')

            username_element = friend.find('div', class_='friend_block_content')
            username = username_element.text.strip() if username_element else "Unknown"

            new_friend = Friend(
                friend_id=int(friend_id),
                username=username,
            )
            self.friends_list.append(new_friend)

class Report:
    def __init__(self, badges_list: list, users_list: list, friends_list: list):

        self.badges_list = badges_list
        self.users_list = users_list
        self.friends_list = friends_list

    def generate(self) -> dict:

        return {
            "total_badges": len(self.badges_list),
            "total_users": len(self.users_list),
            "total_friends": len(self.friends_list),
            "badges": [str(badge) for badge in self.badges_list],
            "users": [str(user) for user in self.users_list],
            "friends": [str(friend) for friend in self.friends_list],
        }
if __name__ == "__main__":
    parser = SteamParser()

    # Парсинг данных
    parser.parse_badges("https://steamcommunity.com/profiles/76561198807849076/badges/")
    parser.parse_user(76561198807849076, "https://steamcommunity.com/profiles/76561198807849076")
    parser.parse_friends(76561198807849076, "https://steamcommunity.com/profiles/76561198807849076/friends/")

    # Создание отчета
    report = Report(parser.badges_list, parser.users_list, parser.friends_list)
    report_dict = report.generate()

    # Вывод отчета
    print(report_dict)