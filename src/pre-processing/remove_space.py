from typing import List, Tuple

def remove_space(article: str) -> Tuple:
    """
    Remove space in the article
    Return:
        article: str
        space inedex: List[str]
    """

    index = 0
    space_index = []

    for char in article:
        if char == ' ':
            space_index.append(index)
        else:
            index += 1
    article = article.replace(' ', '')
    space_index = sorted(list(set(space_index)))
    return article, space_index

if __name__ == "__main__":
    article = '江啟臣:不只譴責侵略 更要居安思危,"國民黨立委江啟臣今(8)日在     臉書表示,法國在台協會 公孫孟主任至立法院 拜訪外交及國防委員會,'
    s, space_index = remove_space(article)
    
    if(article == s):
        print('fail')
    
    print(s)
    space_index.insert(0, 0)
    print(space_index)
    
    parts = [s[i:j] for i,j in zip(space_index, space_index[1:]+[None])]
    print('\n'.join(parts))

