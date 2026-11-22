"""
Safe MySQL Database Migration for Once Upon a Page:
- Extends users table with role and is_active
- Creates categories, books, story_pages, site_settings tables
- Safely seeds default categories, initial books, Twinkle story pages, and site settings
"""

import pymysql
from config import Config

def migrate():
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
    
    with conn.cursor() as cur:
        # 1. Update users table with role and is_active
        cur.execute("DESCRIBE users;")
        user_cols = [c['Field'] for c in cur.fetchall()]
        if 'role' not in user_cols:
            print("Adding 'role' column to users table...")
            cur.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user';")
        if 'is_active' not in user_cols:
            print("Adding 'is_active' column to users table...")
            cur.execute("ALTER TABLE users ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1;")

        # 2. Create categories table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                slug VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # 3. Create books table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                slug VARCHAR(100) NOT NULL UNIQUE,
                title VARCHAR(255) NOT NULL,
                category_id INT NULL,
                category VARCHAR(100) NOT NULL DEFAULT 'Bedtime Story',
                cover VARCHAR(255) NOT NULL,
                author VARCHAR(150) NOT NULL DEFAULT 'Once Upon a Page',
                description TEXT,
                target_age VARCHAR(50) DEFAULT '3-7 years',
                pages INT NOT NULL DEFAULT 16,
                duration VARCHAR(50) DEFAULT '5 mins',
                rating VARCHAR(10) DEFAULT '5.0',
                is_published TINYINT(1) NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_category (category_id),
                INDEX idx_published (is_published)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # 4. Create story_pages table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS story_pages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                book_id INT NOT NULL,
                spread_number INT NOT NULL DEFAULT 1,
                page_number INT NOT NULL DEFAULT 1,
                page_side VARCHAR(10) NOT NULL DEFAULT 'left',
                title VARCHAR(255) NULL,
                text TEXT NULL,
                image_url VARCHAR(255) NULL,
                dialogue TEXT NULL,
                final_message TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_book_spread (book_id, spread_number),
                CONSTRAINT fk_story_pages_book FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # 5. Create site_settings table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS site_settings (
                setting_key VARCHAR(100) PRIMARY KEY,
                setting_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # 6. Seed categories if empty
        cur.execute("SELECT COUNT(*) AS cnt FROM categories;")
        if cur.fetchone()['cnt'] == 0:
            print("Seeding default categories...")
            cats = [
                ('Bedtime Story', 'bedtime-story', 'Gentle, comforting stories to help children drift off to sleep.'),
                ('Magic & Wonder', 'magic-wonder', 'Enchanting tales of fairies, spells, and wondrous realms.'),
                ('Dream Tale', 'dream-tale', 'Imaginative journeys through starry night skies and sleepy clouds.'),
                ('Nature Fantasy', 'nature-fantasy', 'Stories celebrating forests, flowers, seasons, and natural magic.'),
                ('Night Sky', 'night-sky', 'Adventures with the moon, stars, constellations, and celestial wonders.'),
                ('Animal Friends', 'animal-friends', 'Heartwarming escapades of bunnies, bears, mice, and woodland creatures.'),
                ('Classic Tale', 'classic-tale', 'Timeless fables and folklore adapted for young bedtime dreamers.'),
                ('Nature Tale', 'nature-tale', 'Curious transformations, little insects, and tiny wonders of the earth.'),
                ('Fairytale', 'fairytale', 'Beloved traditional fairy tales full of cozy cottages and happily ever afters.'),
                ('Adventure', 'adventure', 'Exciting quests with brave young heroes, beanstalks, and castles.')
            ]
            for name, slug, desc in cats:
                cur.execute("INSERT IGNORE INTO categories (name, slug, description) VALUES (%s, %s, %s);", (name, slug, desc))

        # 7. Automatic dummy books seeding removed (books are managed via Admin Dashboard / Storybook Builder)

        # 8. Seed Twinkle story_pages if empty
        cur.execute("SELECT COUNT(*) AS cnt FROM story_pages WHERE book_id = 1;")
        if cur.fetchone()['cnt'] == 0:
            print("Seeding Twinkle story spreads into story_pages...")
            from app import TWINKLE_SPREADS
            for sp in TWINKLE_SPREADS:
                # Left page: Illustration
                cur.execute("""
                    INSERT INTO story_pages (book_id, spread_number, page_number, page_side, title, text, image_url, dialogue, final_message)
                    VALUES (%s, %s, %s, 'left', %s, NULL, %s, NULL, NULL);
                """, (
                    1, sp['spread_number'], sp['page_num_left'], sp['title'], sp['illustration']
                ))
                # Right page: Text
                cur.execute("""
                    INSERT INTO story_pages (book_id, spread_number, page_number, page_side, title, text, image_url, dialogue, final_message)
                    VALUES (%s, %s, %s, 'right', %s, %s, NULL, %s, %s);
                """, (
                    1, sp['spread_number'], sp['page_num_right'], sp['title'], sp['text'],
                    sp.get('dialogue'), sp.get('final_message')
                ))

        # 9. Seed site_settings if empty
        defaults = {
            'welcome_label': 'Cozy Bedtime Stories',
            'welcome_heading': 'Welcome to a World of Little Stories',
            'welcome_subtitle': "Every little story holds a little magic. Come, let's explore!",
            'welcome_button_text': 'Enter the Story World ✨',
            'welcome_bg_image': 'images/welcome_bg.jpg'
        }
        for k, v in defaults.items():
            cur.execute("""
                INSERT IGNORE INTO site_settings (setting_key, setting_value)
                VALUES (%s, %s);
            """, (k, v))

    conn.close()
    print("Database migration completed successfully!")

if __name__ == '__main__':
    migrate()
