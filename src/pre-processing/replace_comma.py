def replace_comma(article: str) -> str:
    """
    Replace comma in the article
    Return:
        article: str
    """
    article = article.replace(',', '，')
    return article