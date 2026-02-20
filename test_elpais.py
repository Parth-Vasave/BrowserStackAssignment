from scraper import run_scraper


class TestElPaisScraper:

    def test_scrape_opinion_articles(self, driver):
        print("\nStarting scraper... This may take a few minutes, please wait. DO NOT CLOSE\n")
        results = run_scraper(driver)

        articles = results["articles"]
        translated_titles = results["translated_titles"]

        assert len(articles) == 5, f"Expected 5 articles, got {len(articles)}"

        for i, article in enumerate(articles):
            assert article["title"], f"Article {i+1} has an empty title"
            print(f"Article {i+1}: {article['title']}")

        for i, article in enumerate(articles):
            if article["content"]:
                print(f"Article {i+1} content: {len(article['content'])} chars")
            else:
                print(f"Article {i+1} has no body text")

        assert len(translated_titles) == 5, f"Expected 5 translations, got {len(translated_titles)}"

        for i, title in enumerate(translated_titles):
            assert title, f"Translated title {i+1} is empty"
            print(f"Translated {i+1}: {title}")

        repeated = results["repeated_words"]
        if repeated:
            print("\nRepeated words (>2):")
            for word, count in sorted(repeated.items(), key=lambda x: -x[1]):
                print(f"  '{word}': {count}")
        else:
            print("\nNo words repeated more than twice.")

        print("\nAll assertions passed!")
