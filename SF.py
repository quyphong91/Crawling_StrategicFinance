#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup as bs
import time

def SF():

    homepage = 'https://sfmagazine.com'
    
    # Set web browser user agent
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15'}
    
    response = requests.get(homepage, headers=headers)

    soup = bs(response.content, 'html.parser')
    header = soup.find('header')

    # Get url of each topic
    topic_urls = [
        link.get('href')
        for link in header.select('ul a')
        if (len(link.get('href')) > 9) and
        ('topic' in link.get('href'))
    ]

    # Loop through each topic, get url of each article then get its content
    with open('SF.txt', 'w') as f:

        # use tab line as a delimiter
        f.write('Topic \t Article \t Article_link \t Content \n')

        for url in topic_urls:

            # try to get topic name from the urls
            topic = url[29:-1]
            
            topic_resp = requests.get(url, headers=headers)
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
                print('Article_url:', article_link)

                content_resp = requests.get(article_link, headers=headers)

                # track status purpose
                print('Status code:', content_resp.status_code)

                content_soup = bs(content_resp.content, 'html.parser')
                content_soup_body = content_soup.find('body')
                content_tag = content_soup_body.select('p')
                content_texts = [
                    i.text for i in content_tag
                    if not i.text.startswith('\xa0') and (i.text != '')
                ]
                content = ''.join(content_texts)
                
                # track status purpose
                print('Brief content:', content[:30], '...', '\n')

                # use tab as a delimiter
                f.write(
                    str(topic) + '\t' +
                    str(article_title) + '\t' +
                    str(article_link) + '\t' +
                    str(content) + '\n'
                )
                article_title_index += 1

                # avoid getting blocked by the server
                time.sleep(5)

def main():
    return SF()

if __name__ == '__main__':
    main()

