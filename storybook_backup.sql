-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: storybook_db
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `books`
--

DROP TABLE IF EXISTS `books`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `books` (
  `id` int NOT NULL AUTO_INCREMENT,
  `slug` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `category_id` int DEFAULT NULL,
  `category` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Bedtime Story',
  `cover` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `author` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Once Upon a Page',
  `description` text COLLATE utf8mb4_unicode_ci,
  `target_age` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '3-7 years',
  `pages` int NOT NULL DEFAULT '16',
  `duration` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '5 mins',
  `rating` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT '5.0',
  `is_published` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `idx_category` (`category_id`),
  KEY `idx_published` (`is_published`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `books`
--

LOCK TABLES `books` WRITE;
/*!40000 ALTER TABLE `books` DISABLE KEYS */;
INSERT INTO `books` VALUES (1,'twinkle','Twinkle',1,'Bedtime Story','uploads/covers/d61859e11c_Twinkle.png','Once Upon a Page','The heartwarming tale of a tiny star named Twinkle who discovers that you don\'t have to be the brightest star in the sky to make someone\'s night beautiful.','3-7 years',16,'5 mins','5.0',1,'2026-11-21 10:32:07','2026-11-21 12:36:34'),(2,'fairy-and-firefly','The Fairy and the Tiny Bug',2,'Magic & Wonder','uploads/covers/bd8d72235a_fairy_and_tiny_bug.png','Once Upon a Page','Follow Pip the lost firefly and Petal the fairy on an illuminated quest through the moonlit Whispering Woods.','3-7 years',18,'5 mins','4.9',1,'2026-11-21 10:32:07','2026-11-22 12:21:36'),(5,'moons-secret','The Moon\'s Secret',5,'Night Sky','images/books/book_moon.jpg','Aurelia Night','Why does the crescent moon wear a sleepy smile? An ancient sky secret whispered only to children ready for slumber.','3-7 years',12,'4 mins','4.9',0,'2026-11-21 10:32:07','2026-11-21 13:27:46'),(20,'the-little-picnic-adventure','The Little Picnic Adventure',10,'Adventure','uploads/covers/32d860d6bd_The_Little_Picnic_Adventure.png','Once Upon a Page','A fun picnic adventure filled with friendship, surprises and sweet moments! ?','3-7 years',14,'5 mins','5.0',1,'2026-11-21 13:25:38','2026-11-21 13:25:38'),(25,'vihu-her-aayiiiiiiii','Vihu & Her Aayiiiiiiii!',7,'Classic Tale','uploads/covers/98f5869434_Vihu_and_Her_Aayiiiiiiii.png','Once Upon a Page','','3-7 years',18,'5 mins','5.0',1,'2026-11-21 19:41:39','2026-11-21 19:41:39');
/*!40000 ALTER TABLE `books` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Bedtime Story','bedtime-story','Gentle, comforting stories to help children drift off to sleep.','2026-11-21 10:32:06'),(2,'Magic & Wonder','magic-wonder','Enchanting tales of fairies, spells, and wondrous realms.','2026-11-21 10:32:06'),(3,'Dream Tale','dream-tale','Imaginative journeys through starry night skies and sleepy clouds.','2026-11-21 10:32:06'),(4,'Nature Fantasy','nature-fantasy','Stories celebrating forests, flowers, seasons, and natural magic.','2026-11-21 10:32:06'),(5,'Night Sky','night-sky','Adventures with the moon, stars, constellations, and celestial wonders.','2026-11-21 10:32:06'),(6,'Animal Friends','animal-friends','Heartwarming escapades of bunnies, bears, mice, and woodland creatures.','2026-11-21 10:32:06'),(7,'Classic Tale','classic-tale','Timeless fables and folklore adapted for young bedtime dreamers.','2026-11-21 10:32:06'),(8,'Nature Tale','nature-tale','Curious transformations, little insects, and tiny wonders of the earth.','2026-11-21 10:32:06'),(9,'Fairytale','fairytale','Beloved traditional fairy tales full of cozy cottages and happily ever afters.','2026-11-21 10:32:06'),(10,'Adventure','adventure','Exciting quests with brave young heroes, beanstalks, and castles.','2026-11-21 10:32:06');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `character_overlays`
--

DROP TABLE IF EXISTS `character_overlays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `character_overlays` (
  `id` int NOT NULL AUTO_INCREMENT,
  `book_id` int NOT NULL,
  `story_page_id` int NOT NULL,
  `spread_number` int NOT NULL DEFAULT '1',
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Character Overlay',
  `image_path` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pos_x` float NOT NULL DEFAULT '50',
  `pos_y` float NOT NULL DEFAULT '50',
  `scale` float NOT NULL DEFAULT '1',
  `width_pct` float NOT NULL DEFAULT '35',
  `z_index` int NOT NULL DEFAULT '10',
  `animation_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'popout',
  `animation_duration` float NOT NULL DEFAULT '3',
  `movement_intensity` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'medium',
  `animation_delay` float NOT NULL DEFAULT '0',
  `extra_settings` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_book_page` (`book_id`,`story_page_id`),
  KEY `idx_spread` (`book_id`,`spread_number`),
  KEY `fk_char_overlay_page` (`story_page_id`),
  CONSTRAINT `fk_char_overlay_book` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_char_overlay_page` FOREIGN KEY (`story_page_id`) REFERENCES `story_pages` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `character_overlays`
--

LOCK TABLES `character_overlays` WRITE;
/*!40000 ALTER TABLE `character_overlays` DISABLE KEYS */;
INSERT INTO `character_overlays` VALUES (3,1,247,1,'twinkle transprnt','uploads/character_overlays/261d4451b3_twinkle_transprnt.png',52.1,51.1,2.22857,78,10,'float',3,'medium',0,NULL,'2026-11-22 08:03:48','2026-11-22 08:03:48');
/*!40000 ALTER TABLE `character_overlays` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reading_history`
--

DROP TABLE IF EXISTS `reading_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reading_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `book_id` int NOT NULL,
  `last_read_page` int NOT NULL DEFAULT '1',
  `total_pages` int NOT NULL DEFAULT '16',
  `last_opened_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_history` (`user_id`,`book_id`),
  CONSTRAINT `fk_user_history` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=311 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reading_history`
--

LOCK TABLES `reading_history` WRITE;
/*!40000 ALTER TABLE `reading_history` DISABLE KEYS */;
INSERT INTO `reading_history` VALUES (17,7,1,15,16,'2026-11-22 10:08:28','2026-11-21 10:59:21'),(52,90,1,11,16,'2026-11-22 08:39:33','2026-11-21 11:25:31'),(55,90,2,13,18,'2026-11-21 13:27:31','2026-11-21 11:33:28'),(94,7,2,13,18,'2026-11-22 10:08:05','2026-11-21 11:49:29'),(133,90,20,5,14,'2026-11-22 08:47:08','2026-11-21 13:25:49'),(169,7,20,11,14,'2026-11-22 10:08:44','2026-11-21 19:06:28'),(180,90,25,1,18,'2026-11-22 08:47:06','2026-11-21 19:43:06'),(302,7,25,17,18,'2026-11-22 10:53:09','2026-11-22 10:52:07');
/*!40000 ALTER TABLE `reading_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `site_settings`
--

DROP TABLE IF EXISTS `site_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `site_settings` (
  `setting_key` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `setting_value` text COLLATE utf8mb4_unicode_ci,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`setting_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `site_settings`
--

LOCK TABLES `site_settings` WRITE;
/*!40000 ALTER TABLE `site_settings` DISABLE KEYS */;
INSERT INTO `site_settings` VALUES ('login_bg_image','uploads/login/bcec4fc42c_test_login_fairy.png','2026-11-22 10:54:03'),('login_bg_type','plain','2026-11-22 12:07:44'),('login_bg_video','uploads/login/dbc73588b0_gemini_generated_video_b860dc8.mp4','2026-11-22 10:52:43'),('welcome_bg_image','uploads/welcome/9047303ef0_Magical_Childrens_Stories_That.jpg','2026-11-22 10:52:36'),('welcome_bg_type','video','2026-11-22 10:52:36'),('welcome_bg_video','uploads/welcome/819d6f2f67_gemini_generated_video_df5bd85.mp4','2026-11-22 10:52:43'),('welcome_button_text','Enter the Story World ✨','2026-11-22 10:52:33'),('welcome_heading','Welcome to a World of Little Stories','2026-11-22 10:52:33'),('welcome_label','Cozy Bedtime Stories','2026-11-22 10:52:33'),('welcome_subtitle','Every little story holds a little magic. Come, let\'s explore!','2026-11-22 10:52:33');
/*!40000 ALTER TABLE `site_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `story_pages`
--

DROP TABLE IF EXISTS `story_pages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `story_pages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `book_id` int NOT NULL,
  `spread_number` int NOT NULL DEFAULT '1',
  `page_number` int NOT NULL DEFAULT '1',
  `page_side` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'left',
  `title` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `text` text COLLATE utf8mb4_unicode_ci,
  `image_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dialogue` text COLLATE utf8mb4_unicode_ci,
  `final_message` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_book_spread` (`book_id`,`spread_number`),
  CONSTRAINT `fk_story_pages_book` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `story_pages`
--

LOCK TABLES `story_pages` WRITE;
/*!40000 ALTER TABLE `story_pages` DISABLE KEYS */;
INSERT INTO `story_pages` VALUES (153,20,1,1,'left','A Sunny Morning',NULL,'uploads/story_pages/3dda9a9f18_Screenshot_2026-11-21_184532.png',NULL,NULL,'2026-11-21 13:25:38'),(154,20,1,2,'right',NULL,'One beautiful morning, a little girl named Mia woke up with a big smile.\r\n\r\n\"Today is perfect for a picnic!\" she cheered.\r\n\r\nShe packed some apples, sandwiches and yummy cookies.',NULL,'',NULL,'2026-11-21 13:25:38'),(155,20,2,3,'left','A Sleepy Bear',NULL,'uploads/story_pages/418bad7133_Screenshot_2026-11-21_184542.png',NULL,NULL,'2026-11-21 13:25:38'),(156,20,2,4,'right',NULL,'Nearby, Benny the bear was enjoying his morning nap.\r\n\r\nSuddenly...\r\n\r\nKNOCK! KNOCK!\r\n\r\n\"Wake up, Benny! Let\'s go on a picnic!\" shouted Mia.\r\n\r\nBenny opened one sleepy eye.',NULL,'',NULL,'2026-11-21 13:25:38'),(157,20,3,5,'left','Off We Go!',NULL,'uploads/story_pages/3c21d43bd0_Screenshot_2026-11-21_184603.png',NULL,NULL,'2026-11-21 13:25:38'),(158,20,3,6,'right',NULL,'Benny finally agreed.\r\n\r\nThey walked through the beautiful forest, singing happy songs.\r\n\r\nMia skipped, Benny carried the basket, and everything was wonderful!',NULL,'',NULL,'2026-11-21 13:25:38'),(159,20,4,7,'left','Oh No! The Cookies!',NULL,'uploads/story_pages/091e3f49d3_Screenshot_2026-11-21_184615.png',NULL,NULL,'2026-11-21 13:25:38'),(160,20,4,8,'right',NULL,'When they reached a lovely spot, Benny opened the basket.\r\n\r\nBut... the cookies were missing!\r\n\r\n\"Where did they go?\" asked Mia.\r\n\r\nSuddenly, they heard a little giggle behind a bush.',NULL,'',NULL,'2026-11-21 13:25:38'),(161,20,5,9,'left','A Little Surprise',NULL,'uploads/story_pages/e33ec91016_Screenshot_2026-11-21_184644.png',NULL,NULL,'2026-11-21 13:25:38'),(162,20,5,10,'right',NULL,'Mia spotted the naughty squirrel.\r\n\r\n\"Hey, little friend! Those are our cookies!\"\r\n\r\nThe squirrel looked shy.\r\n\r\nMia smiled and shared the cookies with him.\r\n\r\nSoon, everyone was happily munching together!',NULL,'',NULL,'2026-11-21 13:25:38'),(163,20,6,11,'left','The Sweetest Picnic',NULL,'uploads/story_pages/03bcda0e00_Screenshot_2026-11-21_184659.png',NULL,NULL,'2026-11-21 13:25:38'),(164,20,6,12,'right',NULL,'The sun slowly began to set.\r\n\r\nMia hugged Benny and whispered,\r\n\r\n\"This was the best picnic ever!\"\r\n\r\nBenny smiled.\r\n\r\nAnd together, they walked home, dreaming about their next adventure.',NULL,'',NULL,'2026-11-21 13:25:38'),(165,20,7,13,'left','The Little Lesson',NULL,'uploads/story_pages/b47a14f818_Screenshot_2026-11-21_184711.png',NULL,NULL,'2026-11-21 13:25:38'),(166,20,7,14,'right',NULL,'\"Sharing makes every adventure sweeter!\"',NULL,'',NULL,'2026-11-21 13:25:38'),(227,25,1,1,'left','A Little Baby on the Way',NULL,'uploads/story_pages/a25382ec6a_Screenshot_2026-11-22_011843.png',NULL,NULL,'2026-11-21 19:59:36'),(228,25,1,2,'right',NULL,'Once upon a time, a little baby was growing inside her Mummy\'s tummy.\r\n\r\nEveryone was excited to meet her.\r\n\r\nAnd someone special was already waiting for her arrival.\r\n\r\nHer very own Aayi!\r\n\r\nFrom the very beginning, Aayi was there, sharing the excitement and waiting to welcome the little one.',NULL,'',NULL,'2026-11-21 19:59:36'),(229,25,2,3,'left','Hello, Little Vihu!',NULL,'uploads/story_pages/6f2ed8c255_Screenshot_2026-11-22_011918.png',NULL,NULL,'2026-11-21 19:59:36'),(230,25,2,4,'right',NULL,'One beautiful day, a tiny baby girl arrived.\r\n\r\nHer name was Vihu!\r\n\r\nAayi was overjoyed to meet her little princess.\r\n\r\nFrom that day onwards, there were cuddles, kisses, giggles and endless playtime.\r\n\r\nAayi loved spending time with little Vihu, playing with her and taking care of her.\r\n\r\nTheir beautiful bond had just begun!',NULL,'',NULL,'2026-11-21 19:59:36'),(231,25,3,5,'left','A Special Name',NULL,'uploads/story_pages/d37c87b80b_Screenshot_2026-11-22_011927.png',NULL,NULL,'2026-11-21 19:59:36'),(232,25,3,6,'right',NULL,'When Vihu was very little, she couldn\'t quite say \"Aunty\".\r\n\r\nInstead, she started calling out...\r\n\r\n\"AAYIIII!\"\r\n\r\nAnd that became Aayi\'s favourite name in the whole world.\r\n\r\nNo matter how many times she called, Aayi would always answer with a big smile.\r\n\r\n\"Aayiiii is here!\"\r\n\r\nAnd just like that, Aayi got the sweetest name ever!',NULL,'',NULL,'2026-11-21 19:59:36'),(233,25,4,7,'left','The Little Red Car',NULL,'uploads/story_pages/30433caa84_aayis_swift.png',NULL,NULL,'2026-11-21 19:59:36'),(234,25,4,8,'right',NULL,'Whenever Aayi came to visit, Vihu would see that familiar red car arriving outside.\r\n\r\nSoon, something adorable happened.\r\n\r\nEvery time Vihu spotted ANY red car on the road, she would excitedly shout...\r\n\r\n\"AAYIIIIIIII CAR!\"\r\n\r\nBecause in Vihu\'s little world, every red car meant Aayi!',NULL,'',NULL,'2026-11-21 19:59:36'),(235,25,5,9,'left','Miles Away, Hearts Together',NULL,'uploads/story_pages/a987f2e3cc_Screenshot_2026-11-22_011951.png',NULL,NULL,'2026-11-21 19:59:36'),(236,25,5,10,'right',NULL,'One day, Vihu travelled far away to Dubai with her Mummy.\r\n\r\nThere were tall buildings, beautiful lights and so many colourful cars!\r\n\r\nBut Aayi was back home.\r\n\r\nEven though they were far apart, Aayi never stopped missing her little Vihu.\r\n\r\nAnd whenever Vihu spotted a red car, she still remembered her favourite person.\r\n\r\n\"AAYIIIIIIII CAR!\"\r\n\r\nSome memories are so special that even miles cannot take them away.',NULL,'',NULL,'2026-11-21 19:59:36'),(237,25,6,11,'left','Aayi\'s Everyday Hello!',NULL,'uploads/story_pages/19bf74052b_Screenshot_2026-11-22_012002.png',NULL,NULL,'2026-11-21 19:59:36'),(238,25,6,12,'right',NULL,'Even though Vihu was far away in Dubai, Aayi was never missing from her days.\r\n\r\nEvery day, Mummy would video-call Aayi.\r\n\r\nAnd the moment Vihu saw Aayi\'s face on the phone, she would become super excited!\r\n\r\n\"AAYIIIIIIII!\"\r\n\r\nSometimes she would wave, sometimes blow kisses, and sometimes just keep looking at Aayi with her big happy eyes.\r\n\r\nAayi would smile and say,\r\n\r\n\"My little Vihu! I miss you so much!\"\r\n\r\nDistance didn\'t matter. Their little everyday calls kept their bond as special as ever.',NULL,'',NULL,'2026-11-21 19:59:36'),(239,25,7,13,'left','A Little Red Surprise!',NULL,'uploads/story_pages/a3f9a45e04_Screenshot_2026-11-22_012014.png',NULL,NULL,'2026-11-21 19:59:36'),(240,25,7,14,'right',NULL,'One special day, Mummy and Daddy brought Vihu a surprise.\r\n\r\nIt was a tiny, shiny RED TOY CAR!\r\n\r\nVihu\'s eyes sparkled with excitement.\r\n\r\nShe picked it up, held it tightly and ran to Mummy.\r\n\r\n\"Aayiiii CAR! Aayiiii CAR! Look!\"\r\n\r\nMummy started a video call.\r\n\r\nThe moment Aayi appeared on the screen, Vihu proudly showed her little red car.\r\n\r\n\"AAYIIIIIIII CAR!\"\r\n\r\nAayi burst into laughter.\r\n\r\n\"Oh my goodness! You have your very own Aayi car now!\"\r\n\r\nVihu giggled and hugged her little car.\r\n\r\nFinally, she had a red car of her very own!',NULL,'',NULL,'2026-11-21 19:59:36'),(241,25,8,15,'left','Forever Aayi\'s Little Vihu',NULL,'uploads/story_pages/69af9ca3f9_Red_Toy_Car.png',NULL,NULL,'2026-11-21 19:59:36'),(242,25,8,16,'right',NULL,'And so, Vihu had her very own little red car.\r\n\r\nNow, whenever she played with it, she remembered Aayi.\r\n\r\nAayi might be far away, but she would always be Vihu\'s favourite person.\r\n\r\nAnd no matter how big Vihu grows, one thing will never change...\r\n\r\nShe will always have someone waiting to hear that sweet little voice shouting...\r\n\r\n\"AAYIIIIIIII!\"',NULL,'',NULL,'2026-11-21 19:59:36'),(243,25,9,17,'left','❤️ Special',NULL,'uploads/story_pages/7bc424e597_last_page_vihu_Aayi.png',NULL,NULL,'2026-11-21 19:59:36'),(244,25,9,18,'right',NULL,'To my little Vihu,\r\n\r\nFrom the days you were in Mummy\'s tummy to all our precious giggles, cuddles and memories, you have filled my heart with endless love.\r\n\r\nAnd to your Mummy, my bestest sister at heart, thank you for giving me the sweetest little happiness in my life.\r\n\r\nMiles may separate us, but every red car will remind me of you, and every \"AAYIIIIIIII!\" will remain my favourite sound.\r\n\r\nNo matter how big you grow, you\'ll always be my little Vihu.\r\n\r\nForever yours,  \r\nYour Aayiiiiiiii! ❤️',NULL,'',NULL,'2026-11-21 19:59:36'),(247,1,1,1,'left','Meet Twinkle',NULL,'uploads/story_pages/bfa11f620d_Screenshot_2026-11-21_190726.png',NULL,NULL,'2026-11-21 20:42:23'),(248,1,1,2,'right',NULL,'Once upon a time, there was a tiny star named Twinkle.',NULL,'',NULL,'2026-11-21 20:42:23'),(249,1,2,3,'left','The Little Star Who Couldn\'t Shine',NULL,'uploads/story_pages/bde94cec8e_Screenshot_2026-11-21_190804.png',NULL,NULL,'2026-11-21 20:42:23'),(250,1,2,4,'right',NULL,'Every night, all the stars would shine brightly. But Twinkle couldn\'t shine, no matter how hard she tried.',NULL,'',NULL,'2026-11-21 20:42:23'),(251,1,3,5,'left','Twinkle\'s Sadness',NULL,'uploads/story_pages/536c60ce71_Screenshot_2026-11-21_190816.png',NULL,NULL,'2026-11-21 20:42:23'),(252,1,3,6,'right',NULL,'\'I\'m too small. Nobody will ever notice me,\' she whispered sadly.',NULL,'',NULL,'2026-11-21 20:42:23'),(253,1,4,7,'left','The Little Girl',NULL,'uploads/story_pages/5084dea9ad_Screenshot_2026-11-21_190826.png',NULL,NULL,'2026-11-21 20:42:23'),(254,1,4,8,'right',NULL,'One night, she looked down and saw a little girl sitting by her bedroom window, crying.',NULL,'',NULL,'2026-11-21 20:42:23'),(255,1,5,9,'left','Gathering Courage',NULL,'uploads/story_pages/d26f3acf03_Screenshot_2026-11-21_190835.png',NULL,NULL,'2026-11-21 20:42:23'),(256,1,5,10,'right',NULL,'Twinkle wanted to help, but she was afraid. Still, she gathered her courage and tried one more time.',NULL,'',NULL,'2026-11-21 20:42:23'),(257,1,6,11,'left','A Little Golden Light',NULL,'uploads/story_pages/dadd941209_Screenshot_2026-11-21_190847.png',NULL,NULL,'2026-11-21 20:42:23'),(258,1,6,12,'right',NULL,'A tiny golden light appeared around her. It wasn\'t very bright, but it reached the little girl\'s window.',NULL,'',NULL,'2026-11-21 20:42:23'),(259,1,7,13,'left','Someone Notices Twinkle',NULL,'uploads/story_pages/688aa58770_Screenshot_2026-11-21_191148.png',NULL,NULL,'2026-11-21 20:42:23'),(260,1,7,14,'right',NULL,'The girl smiled and whispered, \'Look! My little star is here!\'',NULL,'The Moon smiled and said, \"You don\'t have to be the brightest star in the sky to make someone\'s night beautiful.\"',NULL,'2026-11-21 20:42:23'),(261,1,8,15,'left','Twinkle\'s Happy Ending',NULL,'uploads/story_pages/9043f29040_Screenshot_2026-11-21_190913.png',NULL,NULL,'2026-11-21 20:42:23'),(262,1,8,16,'right',NULL,'From that night onwards, Twinkle never worried about being small again. She shone every night, just for the little girl.',NULL,'Sometimes, the smallest lights make the biggest difference. ?',NULL,'2026-11-21 20:42:23'),(283,2,1,1,'left','A Tiny Little Bug',NULL,'uploads/story_pages/3f1e31d924_Dreamy_Firefly_on_a_Spotted_Mu.png',NULL,NULL,'2026-11-22 12:21:36'),(284,2,1,2,'right',NULL,'Once upon a time, deep inside a beautiful forest, lived a tiny little bug.\r\n\r\nHe was small, cute and loved exploring the forest during the day.\r\n\r\nBut there was just one little problem...\r\n\r\nHe was terribly afraid of the dark!',NULL,'',NULL,'2026-11-22 12:21:36'),(285,2,2,3,'left','When Night Falls',NULL,'uploads/story_pages/d22dc5469e_Screenshot_2026-11-21_170812.png',NULL,NULL,'2026-11-22 12:21:36'),(286,2,2,4,'right',NULL,'Every evening, when the sun went down and the forest became dark, the little bug started to worry.\r\n\r\nThe tall trees looked like scary monsters.\r\n\r\nThe dancing leaves looked like spooky creatures.\r\n\r\nEven the little branches looked like long, creepy fingers!\r\n\r\n\"Oh no! What if something catches me?\" he whispered.',NULL,'',NULL,'2026-11-22 12:21:36'),(287,2,3,5,'left','Another Sleepless Night',NULL,'uploads/story_pages/38986e921a_Screenshot_2026-11-21_170827.png',NULL,NULL,'2026-11-22 12:21:36'),(288,2,3,6,'right',NULL,'Every night, the little bug would run around, looking for a safe place to hide.\r\n\r\nHe cried, trembled and couldn\'t sleep.\r\n\r\nMeanwhile, all the other little animals in the forest were sleeping peacefully.\r\n\r\nThe rabbits were cuddled up in their burrows.\r\n\r\nThe birds were resting in their nests.\r\n\r\nAnd the squirrels were fast asleep in their cosy little homes.\r\n\r\n\"Why can\'t I sleep like everyone else?\" sighed the little bug.',NULL,'',NULL,'2026-11-22 12:21:36'),(289,2,4,7,'left','A Little Fairy Appears',NULL,'uploads/story_pages/5a9c54a33e_Screenshot_2026-11-21_170839.png',NULL,NULL,'2026-11-22 12:21:36'),(290,2,4,8,'right',NULL,'Just then, a tiny fairy appeared from behind a glowing flower.\r\n\r\nShe had sparkling wings and carried a little magical light.\r\n\r\n\"Hello, little one! Why are you still awake?\" she asked sweetly.\r\n\r\nThe little bug looked up and said,\r\n\r\n\"I\'m afraid of the dark. I can\'t sleep when everything looks so scary!\"',NULL,'May your dreams be filled with magic and wonder. ?',NULL,'2026-11-22 12:21:36'),(291,2,5,9,'left','A Little Secret',NULL,'uploads/story_pages/768e6620a1_Screenshot_2026-11-21_170839.png',NULL,NULL,'2026-11-22 12:21:36'),(292,2,5,10,'right',NULL,'The fairy smiled gently.\r\n\r\n\"Oh, little bug! You don\'t have to be afraid of the dark.\"\r\n\r\n\"But I am!\" said the bug.\r\n\r\nThe fairy giggled and said,\r\n\r\n\"Don\'t you know? You have something very special inside you. You just haven\'t discovered it yet!\"\r\n\r\n\"Something special? What is it?\" asked the curious little bug.',NULL,'',NULL,'2026-11-22 12:21:36'),(293,2,6,11,'left','The Magical Gift',NULL,'uploads/story_pages/11eb1c670b_Screenshot_2026-11-21_170850.png',NULL,NULL,'2026-11-22 12:21:36'),(294,2,6,12,'right',NULL,'With a wave of her sparkling wand, the fairy whispered a little magic spell.\r\n\r\n✨ \"Twinkle, sparkle, shine so bright, let this little bug glow tonight!\" ✨\r\n\r\nSuddenly, a warm golden light appeared on the little bug\'s tummy!\r\n\r\n\"Wowww! I\'m glowing!\" he squealed with excitement.\r\n\r\nThe fairy smiled.\r\n\r\n\"Now you have your very own little light!\"',NULL,'',NULL,'2026-11-22 12:21:36'),(295,2,7,13,'left','A New Little Light',NULL,'uploads/story_pages/d077485caf_Screenshot_2026-11-21_170900.png',NULL,NULL,'2026-11-22 12:21:36'),(296,2,7,14,'right',NULL,'The little bug couldn\'t believe his eyes!\r\n\r\nHe flew up, down and all around the forest.\r\n\r\nHis tiny golden light sparkled through the darkness.\r\n\r\nAs he flew past the tall trees, he stopped.\r\n\r\n\"Wait a minute! Those aren\'t monsters!\"\r\n\r\nThey were just trees!\r\n\r\nAnd those scary shadows?\r\n\r\nThey were only leaves dancing in the wind!\r\n\r\n\"Oh! There\'s nothing to be afraid of!\" he laughed.',NULL,'',NULL,'2026-11-22 12:21:36'),(297,2,8,15,'left','The Happiest Little Bug',NULL,'uploads/story_pages/09f4030794_Screenshot_2026-11-21_170912.png',NULL,NULL,'2026-11-22 12:21:36'),(298,2,8,16,'right',NULL,'From that night onwards, everything changed.\r\n\r\nThe little bug loved the nighttime!\r\n\r\nHe danced with the fireflies, played hide-and-seek among the flowers and flew beneath the beautiful moon.\r\n\r\nHe was no longer afraid of the dark.\r\n\r\nAnd when morning arrived, he snuggled into his cosy little home and slept peacefully.\r\n\r\nThe tiny little bug had become a beautiful little **LIGHTNING BUG!** ✨',NULL,'',NULL,'2026-11-22 12:21:36'),(299,2,9,17,'left','The Moral',NULL,'uploads/story_pages/e084895c40_Screenshot_2026-11-21_170920.png',NULL,NULL,'2026-11-22 12:21:36'),(300,2,9,18,'right',NULL,'\"Sometimes, the light we are looking for is already inside us.\"\r\n\r\nAnd remember...\r\n\r\nEven the tiniest little light can make the darkest night beautiful. ✨',NULL,'',NULL,'2026-11-22 12:21:36');
/*!40000 ALTER TABLE `story_pages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_favorites`
--

DROP TABLE IF EXISTS `user_favorites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_favorites` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `book_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_fav` (`user_id`,`book_id`),
  CONSTRAINT `fk_user_fav` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_favorites`
--

LOCK TABLES `user_favorites` WRITE;
/*!40000 ALTER TABLE `user_favorites` DISABLE KEYS */;
INSERT INTO `user_favorites` VALUES (5,7,1,'2026-11-21 10:13:18'),(22,90,25,'2026-11-21 20:03:04');
/*!40000 ALTER TABLE `user_favorites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_preferences`
--

DROP TABLE IF EXISTS `user_preferences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_preferences` (
  `user_id` int NOT NULL,
  `theme` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'light',
  `night_sky` tinyint(1) NOT NULL DEFAULT '1',
  `page_turn_whispers` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `fk_user_pref` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_preferences`
--

LOCK TABLES `user_preferences` WRITE;
/*!40000 ALTER TABLE `user_preferences` DISABLE KEYS */;
INSERT INTO `user_preferences` VALUES (7,'light',1,1,'2026-11-22 10:05:15','2026-11-22 10:50:36');
/*!40000 ALTER TABLE `user_preferences` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'user',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=386 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (7,'abc','abc@gmail.com','pbkdf2:sha256:1000000$J3tBGhHymtUhGtGG$4e8fb68102d5f983fa96bace7055ce79e4c65b21c297c45fb000ff7108fcee47','2026-11-21 08:27:38','user',1),(90,'Head Scribe','admin@onceuponapage.com','pbkdf2:sha256:1000000$Xh6aX0XaoQEuEPkm$7c41eb81b67b7c9b62d8b994896b05d35fa35e29db023ce382fd61f5fca2343d','2026-11-21 10:33:21','admin',1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=utf8mb4 */;


-- Dump completed on 2026-11-22 17:54:41
