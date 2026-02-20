import os, re, time
from collections import Counter

import requests
from deep_translator import GoogleTranslator
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def ensure_spanish(driver):
    lang = driver.find_element(By.TAG_NAME, "html").get_attribute("lang")
    print(f"Page language: {lang}")

    if lang and lang.startswith("es"):
        print("Website is in Spanish")
        return True

    if "elpais.com" in driver.current_url and "english" not in driver.current_url:
        print("Website is the Spanish edition.")
        return True

    print("Website may not be in Spanish.")
    return False


def get_article_links(driver, max_articles=5):
    driver.get("https://elpais.com/opinion/")
    time.sleep(3)

    try:
        cookie_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        cookie_btn.click()
        print("Accepted cookie consent")
        time.sleep(1)
    except Exception:
        pass

    ensure_spanish(driver)

    articles = driver.find_elements(By.CSS_SELECTOR, "article a[href*='/opinion/']")

    seen = set()
    links = []
    for a in articles:
        href = a.get_attribute("href")
        if href and href not in seen and "/opinion/" in href and href.endswith(".html"):
            seen.add(href)
            links.append(href)
            if len(links) >= max_articles:
                break

    print(f"Found {len(links)} article links")
    return links


def scrape_article(driver, url, retries=2):
    driver.set_page_load_timeout(60)

    for attempt in range(retries + 1):
        try:
            driver.get(url)
            time.sleep(2)
            break
        except Exception:
            if attempt < retries:
                print(f"Page load timed out, retrying ({attempt + 1}/{retries})...")
                time.sleep(3)
            else:
                print(f"Failed to load {url} after {retries + 1} attempts")
                return {"url": url, "title": "Failed to load", "content": "", "image_url": None}

    data = {"url": url, "title": "", "content": "", "image_url": None}

    # title
    try:
        title_el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.a_t"))
        )
        data["title"] = title_el.text.strip()
    except Exception:
        try:
            data["title"] = driver.find_element(By.TAG_NAME, "h1").text.strip()
        except Exception:
            data["title"] = "Title not found"

    # content
    try:
        paragraphs = driver.find_elements(By.CSS_SELECTOR, "div.a_c p")
        if not paragraphs:
            paragraphs = driver.find_elements(By.CSS_SELECTOR, "article p, .article_body p, .a_b p")

        content_parts = [p.text.strip() for p in paragraphs if p.text.strip()]
        data["content"] = "\n".join(content_parts)

        if not data["content"]:
            fallback = []
            try:
                subtitle = driver.find_element(By.CSS_SELECTOR, "h2.a_st")
                if subtitle.text.strip():
                    fallback.append(subtitle.text.strip())
            except Exception:
                pass
            for cap in driver.find_elements(By.CSS_SELECTOR, "figcaption"):
                if cap.text.strip():
                    fallback.append(cap.text.strip())
            data["content"] = "\n".join(fallback)
    except Exception:
        data["content"] = "Content not found"

    # cover image
    try:
        img = driver.find_element(By.CSS_SELECTOR, "article img, .a_m_w img, figure img")
        data["image_url"] = img.get_attribute("src")
    except Exception:
        data["image_url"] = None

    return data


def download_image(url, save_dir="images", filename=None):
    if not url:
        return None

    os.makedirs(save_dir, exist_ok=True)

    if not filename:
        filename = url.split("/")[-1].split("?")[0]
        if not filename or len(filename) > 100:
            filename = f"article_image_{hash(url) % 10000}.jpg"

    filepath = os.path.join(save_dir, filename)

    try:
        resp = requests.get(url, timeout=15, stream=True)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        print(f"Image saved: {filepath} 📷")
        return filepath
    except Exception as e:
        print(f"Failed to download image: {e}")
        return None


def translate_titles(titles):
    translator = GoogleTranslator(source="es", target="en")
    translated = []

    for title in titles:
        try:
            translated.append(translator.translate(title))
        except Exception as e:
            print(f"Translation failed for '{title}': {e}")
            translated.append(title)

    return translated


def analyze_repeated_words(translated_titles):
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "to", "of", "in",
        "for", "on", "with", "at", "by", "from", "as", "into", "through",
        "during", "before", "after", "above", "below", "between", "out",
        "off", "over", "under", "and", "but", "or", "nor", "not", "so",
        "yet", "both", "either", "neither", "each", "every", "all", "any",
        "few", "more", "most", "other", "some", "such", "no", "only", "own",
        "same", "than", "too", "very", "just", "because", "if", "when",
        "where", "how", "what", "which", "who", "whom", "this", "that",
        "these", "those", "it", "its", "he", "she", "they", "them", "his",
        "her", "their", "our", "your", "my", "about",
    }

    all_words = []
    for title in translated_titles:
        words = re.findall(r"[a-zA-Z]+", title.lower())
        all_words.extend(w for w in words if w not in stop_words and len(w) > 1)

    counts = Counter(all_words)
    return {word: count for word, count in counts.items() if count > 2}


def run_scraper(driver):
    """Run the full scraping pipeline: fetch articles, translate, and analyze."""
    print("=" * 60)
    print(" EL PAÍS OPINION SECTION SCRAPER")
    print("=" * 60)

    print("\nNavigating to Opinion section...")
    article_links = get_article_links(driver, max_articles=5)

    if not article_links:
        print("No articles found!")
        return {"articles": [], "translated_titles": [], "repeated_words": {}}

    print("\nScraping articles...\n")
    articles = []
    for i, link in enumerate(article_links, 1):
        print(f"--- Article {i} ---")
        print(f"URL: {link}")
        article = scrape_article(driver, link)
        articles.append(article)

        print(f"Title (ES): {article['title']}")
        print(f"Content (ES): {article['content'][:300]}...\n")

        if article["image_url"]:
            download_image(article["image_url"], filename=f"article_{i}.jpg")
        else:
            print("No cover image available\n")

    print("\nTranslating titles to English...\n")
    spanish_titles = [a["title"] for a in articles]
    translated_titles = translate_titles(spanish_titles)

    for i, (es, en) in enumerate(zip(spanish_titles, translated_titles), 1):
        print(f"  {i}. {es}")
        print(f"     → {en}")

    print("\nAnalyzing repeated words...\n")
    repeated_words = analyze_repeated_words(translated_titles)

    if repeated_words:
        for word, count in sorted(repeated_words.items(), key=lambda x: -x[1]):
            print(f"  '{word}' — {count} times")
    else:
        print("No words repeated more than twice.")

    print("\n" + "=" * 60)
    print("  DONE")
    print("=" * 60)

    return {
        "articles": articles,
        "translated_titles": translated_titles,
        "repeated_words": repeated_words,
    }


if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        run_scraper(driver)
    finally:
        driver.quit()
