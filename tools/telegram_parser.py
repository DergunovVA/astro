"""
Telegram Channel Parser для анализа конкурентов

Анализирует публичные Telegram каналы астрологов:
- Частота публикаций
- Типы контента
- Популярность постов
- Темы и стиль
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# Конфигурация (создайте файл .env или передайте переменные)
API_ID = os.getenv("TELEGRAM_API_ID")  # Получить на my.telegram.org
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")  # Ваш номер телефона

# Каналы для анализа
ASTRO_CHANNELS = {
    "chayka": "@astro_chayka",  # Константин Дараган (Чайка)
    "kulkov": "@alexeykoulkov",  # Алексей Кульков
    "andreev": "@astrolaboratory",  # Павел Андреев (примерный)
    "bunyakova": "@astrologforyou",  # Инна Бунякова
    "globa": "@globa_astro",  # Павел Глоба (если есть)
}


class TelegramChannelAnalyzer:
    """Анализатор Telegram каналов астрологов"""

    def __init__(self, api_id: str, api_hash: str, phone: str):
        self.client = TelegramClient("astro_competitor_session", api_id, api_hash)
        self.phone = phone
        self.data_dir = Path("data/competitors")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def connect(self):
        """Подключение к Telegram"""
        await self.client.start(phone=self.phone)
        print("✅ Подключено к Telegram")

    async def get_channel_info(self, channel_username: str):
        """Получить информацию о канале"""
        try:
            entity = await self.client.get_entity(channel_username)
            return {
                "id": entity.id,
                "title": entity.title,
                "username": entity.username,
                "participants_count": getattr(entity, "participants_count", "N/A"),
                "description": getattr(entity, "about", "N/A"),
            }
        except Exception as e:
            print(f"❌ Ошибка получения info для {channel_username}: {e}")
            return None

    async def parse_channel_posts(
        self, channel_username: str, limit: int = 100, days_back: int = 30
    ):
        """
        Парсинг постов канала

        Args:
            channel_username: @username канала
            limit: максимум постов
            days_back: сколько дней назад смотреть
        """
        print(f"\n📊 Анализ канала: {channel_username}")

        try:
            entity = await self.client.get_entity(channel_username)
            posts = []
            offset_date = datetime.now() - timedelta(days=days_back)

            # Получаем историю сообщений
            offset_id = 0
            while len(posts) < limit:
                history = await self.client(
                    GetHistoryRequest(
                        peer=entity,
                        offset_id=offset_id,
                        offset_date=offset_date,
                        add_offset=0,
                        limit=100,
                        max_id=0,
                        min_id=0,
                        hash=0,
                    )
                )

                if not history.messages:
                    break

                for message in history.messages:
                    if message.date < offset_date:
                        break

                    post_data = self._extract_post_data(message)
                    if post_data:
                        posts.append(post_data)

                offset_id = history.messages[-1].id

                if len(history.messages) < 100:
                    break

            print(f"✅ Собрано постов: {len(posts)}")
            return posts

        except Exception as e:
            print(f"❌ Ошибка парсинга {channel_username}: {e}")
            return []

    def _extract_post_data(self, message):
        """Извлечь данные из поста"""
        if not message or not message.message:
            return None

        return {
            "id": message.id,
            "date": message.date.isoformat(),
            "text": message.message,
            "text_length": len(message.message),
            "views": message.views or 0,
            "forwards": message.forwards or 0,
            "replies": message.replies.replies if message.replies else 0,
            "reactions": self._extract_reactions(message),
            "media_type": self._get_media_type(message),
            "links": self._extract_links(message),
            "hashtags": self._extract_hashtags(message),
        }

    def _extract_reactions(self, message):
        """Извлечь реакции на пост"""
        if not hasattr(message, "reactions") or not message.reactions:
            return {}

        reactions = {}
        for reaction in message.reactions.results:
            emoji = getattr(reaction.reaction, "emoticon", "unknown")
            reactions[emoji] = reaction.count

        return reactions

    def _get_media_type(self, message):
        """Определить тип медиа в посте"""
        if not message.media:
            return "text"

        if isinstance(message.media, MessageMediaPhoto):
            return "photo"
        elif isinstance(message.media, MessageMediaDocument):
            if message.media.document.mime_type.startswith("video"):
                return "video"
            return "document"

        return "other"

    def _extract_links(self, message):
        """Извлечь ссылки из текста"""
        import re

        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        return re.findall(url_pattern, message.message)

    def _extract_hashtags(self, message):
        """Извлечь хештеги"""
        import re

        hashtag_pattern = r"#\w+"
        return re.findall(hashtag_pattern, message.message)

    def analyze_posts(self, posts: list, channel_name: str):
        """Анализ собранных постов"""
        if not posts:
            print("⚠️ Нет постов для анализа")
            return None

        print(f"\n📈 Анализ контента канала {channel_name}:")

        # Базовая статистика
        total_posts = len(posts)
        total_views = sum(p["views"] for p in posts)
        avg_views = total_views / total_posts if total_posts > 0 else 0

        # Типы контента
        media_types = Counter(p["media_type"] for p in posts)

        # Длина постов
        avg_length = sum(p["text_length"] for p in posts) / total_posts

        # Популярные посты
        top_posts = sorted(posts, key=lambda x: x["views"], reverse=True)[:5]

        # Частота публикаций
        dates = [datetime.fromisoformat(p["date"]).date() for p in posts]
        date_counts = Counter(dates)
        avg_posts_per_day = len(posts) / len(set(dates)) if dates else 0

        # Реакции
        all_reactions = {}
        for post in posts:
            for emoji, count in post["reactions"].items():
                all_reactions[emoji] = all_reactions.get(emoji, 0) + count

        # Хештеги
        all_hashtags = []
        for post in posts:
            all_hashtags.extend(post["hashtags"])
        top_hashtags = Counter(all_hashtags).most_common(10)

        analysis = {
            "channel_name": channel_name,
            "period_days": (max(dates) - min(dates)).days if dates else 0,
            "statistics": {
                "total_posts": total_posts,
                "total_views": total_views,
                "avg_views_per_post": round(avg_views, 0),
                "avg_length_chars": round(avg_length, 0),
                "avg_posts_per_day": round(avg_posts_per_day, 2),
            },
            "content_types": dict(media_types),
            "top_reactions": dict(
                sorted(all_reactions.items(), key=lambda x: x[1], reverse=True)[:5]
            ),
            "top_hashtags": dict(top_hashtags),
            "top_posts": [
                {
                    "id": p["id"],
                    "date": p["date"],
                    "views": p["views"],
                    "text_preview": p["text"][:200] + "..."
                    if len(p["text"]) > 200
                    else p["text"],
                    "media": p["media_type"],
                }
                for p in top_posts
            ],
        }

        # Вывод
        print(f"  📊 Всего постов: {total_posts}")
        print(f"  👁️ Средние просмотры: {avg_views:,.0f}")
        print(f"  📝 Средняя длина: {avg_length:.0f} символов")
        print(f"  📅 Постов в день: {avg_posts_per_day:.1f}")
        print(f"  📷 Типы контента: {dict(media_types)}")
        print(f"  ❤️ Топ реакции: {dict(list(all_reactions.items())[:3])}")

        return analysis

    def analyze_content_themes(self, posts: list):
        """Анализ тем контента (ключевые слова)"""
        print("\n🔍 Анализ тем контента:")

        # Ключевые слова астрологии
        keywords = {
            "хорарная": 0,
            "натальная": 0,
            "транзит": 0,
            "прогноз": 0,
            "ретроград": 0,
            "меркурий": 0,
            "венера": 0,
            "марс": 0,
            "юпитер": 0,
            "сатурн": 0,
            "луна": 0,
            "солнце": 0,
            "аспект": 0,
            "дом": 0,
            "знак": 0,
            "консультация": 0,
            "курс": 0,
            "обучение": 0,
            "вопрос": 0,
            "ответ": 0,
        }

        for post in posts:
            text_lower = post["text"].lower()
            for keyword in keywords:
                if keyword in text_lower:
                    keywords[keyword] += 1

        # Топ темы
        top_themes = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]

        for theme, count in top_themes:
            percentage = (count / len(posts)) * 100
            print(f"  • {theme}: {count} постов ({percentage:.1f}%)")

        return dict(top_themes)

    async def save_results(self, channel_name: str, analysis: dict, posts: list):
        """Сохранить результаты анализа"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Сохранить анализ
        analysis_file = self.data_dir / f"{channel_name}_analysis_{timestamp}.json"
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

        # Сохранить сырые данные
        posts_file = self.data_dir / f"{channel_name}_posts_{timestamp}.json"
        with open(posts_file, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)

        print("\n💾 Результаты сохранены:")
        print(f"  • {analysis_file}")
        print(f"  • {posts_file}")

    async def compare_channels(self, channels_data: dict):
        """Сравнение нескольких каналов"""
        print("\n🔄 Сравнение каналов:\n")

        comparison = []
        for name, data in channels_data.items():
            comparison.append(
                {
                    "channel": name,
                    "posts": data["statistics"]["total_posts"],
                    "avg_views": data["statistics"]["avg_views_per_post"],
                    "posts_per_day": data["statistics"]["avg_posts_per_day"],
                    "avg_length": data["statistics"]["avg_length_chars"],
                }
            )

        # Сортировка по просмотрам
        comparison.sort(key=lambda x: x["avg_views"], reverse=True)

        print("┌─────────────┬────────┬─────────────┬──────────────┬────────────┐")
        print("│ Канал       │ Постов │ Ср.просмотры│ Пост/день    │ Ср.длина   │")
        print("├─────────────┼────────┼─────────────┼──────────────┼────────────┤")

        for ch in comparison:
            print(
                f"│ {ch['channel']:11} │ {ch['posts']:6} │ {ch['avg_views']:11,.0f} │ {ch['posts_per_day']:12.2f} │ {ch['avg_length']:10.0f} │"
            )

        print("└─────────────┴────────┴─────────────┴──────────────┴────────────┘")

        return comparison

    async def disconnect(self):
        """Отключение от Telegram"""
        await self.client.disconnect()
        print("\n✅ Отключено от Telegram")


async def main():
    """Основная функция анализа"""

    # Проверка API ключей
    if not all([API_ID, API_HASH, PHONE]):
        print("❌ Ошибка: Установите переменные окружения:")
        print("   TELEGRAM_API_ID - получить на https://my.telegram.org")
        print("   TELEGRAM_API_HASH")
        print("   TELEGRAM_PHONE - ваш номер телефона")
        return

    # Создать анализатор
    analyzer = TelegramChannelAnalyzer(API_ID, API_HASH, PHONE)

    try:
        # Подключение
        await analyzer.connect()

        # Анализ каждого канала
        all_analyses = {}

        for name, username in ASTRO_CHANNELS.items():
            print(f"\n{'=' * 60}")
            print(f"Анализ канала: {name} ({username})")
            print("=" * 60)

            # Получить информацию о канале
            info = await analyzer.get_channel_info(username)
            if info:
                print(f"📢 {info['title']}")
                print(f"👥 Подписчиков: {info.get('participants_count', 'N/A')}")

            # Парсинг постов (последние 30 дней, до 200 постов)
            posts = await analyzer.parse_channel_posts(
                username, limit=200, days_back=30
            )

            if posts:
                # Анализ
                analysis = analyzer.analyze_posts(posts, name)
                themes = analyzer.analyze_content_themes(posts)

                if analysis:
                    analysis["themes"] = themes
                    analysis["channel_info"] = info
                    all_analyses[name] = analysis

                    # Сохранить результаты
                    await analyzer.save_results(name, analysis, posts)

            # Пауза между запросами
            await asyncio.sleep(2)

        # Сравнение всех каналов
        if len(all_analyses) > 1:
            comparison = await analyzer.compare_channels(all_analyses)

            # Сохранить сравнение
            comparison_file = (
                analyzer.data_dir
                / f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(comparison_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"comparison": comparison, "full_data": all_analyses},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            print(f"\n💾 Сравнение сохранено: {comparison_file}")

        # Выводы
        print("\n" + "=" * 60)
        print("📊 ВЫВОДЫ ДЛЯ ПРОДУКТА:")
        print("=" * 60)

        if all_analyses:
            # Самый популярный канал
            best = max(
                all_analyses.items(),
                key=lambda x: x[1]["statistics"]["avg_views_per_post"],
            )
            print(f"\n🏆 Самый популярный: {best[0]}")
            print(
                f"   Средние просмотры: {best[1]['statistics']['avg_views_per_post']:,.0f}"
            )

            # Самый активный
            most_active = max(
                all_analyses.items(),
                key=lambda x: x[1]["statistics"]["avg_posts_per_day"],
            )
            print(f"\n⚡ Самый активный: {most_active[0]}")
            print(
                f"   Постов в день: {most_active[1]['statistics']['avg_posts_per_day']:.2f}"
            )

            # Общие темы
            all_themes = {}
            for analysis in all_analyses.values():
                for theme, count in analysis.get("themes", {}).items():
                    all_themes[theme] = all_themes.get(theme, 0) + count

            print("\n🔥 Топ темы (что работает):")
            for theme, count in sorted(
                all_themes.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                print(f"   • {theme}: {count} упоминаний")

    finally:
        await analyzer.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
