#!/usr/bin/env python3


import requests
from bs4 import BeautifulSoup as bs
import time
import csv


def sf():

    homepage = 'https://sfmagazine.com'
    
    # Set web browser user agent
    headers = {
        'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5)' +
            'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15'
    }

    # This part is to deal with the exception: connection error-max retries exceeded
    # https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
    session = requests.Session()
    retry = requests.packages.urllib3.util.retry.Retry(connect=3, backoff_factor=0.2)
    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    response = session.get(homepage, headers=headers, timeout=None)

    soup = bs(response.content, 'html.parser')
    header = soup.find('header')

    # Get url of each topic
    topic_urls = [
        link.get('href')
        for link in header.select('ul a')
        if (len(link.get('href')) > 9) and
        ('topic' in link.get('href'))
    ]

    csv.register_dialect('comma', delimiter=',')
    # Loop through each topic, get url of each article then get its content
    with open('SF.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='comma')

        # use tab line as a delimiter
        writer.writerow((
            'Topic',
            'Article',
            'Article_link',
            'Content'
            ))

        for url in topic_urls:

            # try to get topic name from the urls
            topic = url[29:-1]
            
            topic_resp = session.get(url, headers=headers, timeout=None)
            topic_soup = bs(topic_resp.content, 'html.parser')
            topic_soup_body = topic_soup.find('body')
            article_title_tags = topic_soup_body.select('h2 a')
            article_titles = [i.text for i in article_title_tags]
            article_links = [link.get('href') for link in article_title_tags]

            article_title_index = 0
            for article_link in article_links:

                # track status purpose
                print('Topic:', topic)
                print('No.', article_title_index + 1)

                article_title = article_titles[article_title_index]

                # track status purpose
                print('Article:', article_title)
                print('Url:', article_link)

                content_resp = session.get(article_link, headers=headers, timeout=None)

                # track status purpose
                print('Status code:', content_resp.status_code)

                content_soup = bs(content_resp.content, 'html.parser')
                content_soup_body = content_soup.find('body')
                content_tag = content_soup_body.select('p')

                # Just take relevant content, exclude non-relevant one like \xa0
                content_texts = [
                    i.text for i in content_tag
                    if not i.text.startswith('\xa0') and (i.text != '')
                ]
                content = ''.join(content_texts)

                # track status purpose
                print('Brief content:', content[:30], '...', '\n')

                # use tab as a delimiter
                writer.writerow((
                    topic,
                    article_title,
                    article_link,
                    content
                ))
                article_title_index += 1

                # I tried to set it to 3s, but it will lead to connection timeout soon
                # 5s is fine
                time.sleep(5)


def main():
    return sf()


if __name__ == '__main__':
    main()

