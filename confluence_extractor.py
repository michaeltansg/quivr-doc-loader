# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=logging-fstring-interpolation
# pylint: disable=too-few-public-methods
# pylint: disable=logging-too-many-args

import logging
import os
import json
from typing import List, Optional, Callable, Any
from atlassian import Confluence
from requests import HTTPError
from tenacity import (
    before_sleep_log,
    retry,
    stop_after_attempt,
    wait_exponential,
)
from bs4 import BeautifulSoup
from logger import get_logger

logger = get_logger(__name__)

class ConfluenceConfiguration:
    def __init__(
            self,
            sitename: str,
            username: str,
            api_key: str,
            space: str,
    ):
        self.sitename = sitename
        self.username = username
        self.api_key = api_key
        self.space = space

class RetryConfig:
    def __init__(
            self,
            number_of_retries: Optional[int]=3,
            min_retry_seconds: Optional[int]=2,
            max_retry_seconds: Optional[int]=10,
    ):
        self.number_of_retries = number_of_retries
        self.min_retry_seconds = min_retry_seconds
        self.max_retry_seconds = max_retry_seconds

class ConfluenceExtractor:
    def __init__(
            self,
            confluence_config: ConfluenceConfiguration,
            content_dir: str,
            retry_config: Optional[RetryConfig] = RetryConfig(),
            confluence_kwargs: Optional[dict] = None,
    ):
        confluence_kwargs = confluence_kwargs or {}
        self.base_url = f'https://{confluence_config.sitename}.atlassian.net/wiki'
        self.confluence = Confluence(
            url = self.base_url,
            username = confluence_config.username,
            password = confluence_config.api_key,
            **confluence_kwargs,
        )
        self.space = confluence_config.space
        self.content_dir = content_dir
        self.number_of_retries = retry_config.number_of_retries
        self.min_retry_seconds = retry_config.min_retry_seconds
        self.max_retry_seconds = retry_config.max_retry_seconds

    def extract_all_pages(
            self,
            include_attachments: bool = False,
            limit: Optional[int] = 50,
            max_pages: Optional[int] = 1000,
            ocr_languages: Optional[str] = None,
    ):
        pages = self.paginate_request(
            self.confluence.get_all_pages_from_space,
            space=self.space,
            limit=limit,
            max_pages=max_pages,
            status="current",
            expand="body.storage.value,version",
        )
        logger.info(f"Found {len(pages)} pages")
        for page in pages:
            self.process_page(
                page,
                include_attachments,
            )

    def process_page(
        self,
        page: dict,
        include_attachments: bool,
    ):
        page_id = page['id']
        file_path = f'{self.content_dir}/{page_id}.html'

        # Check if the page has been previously processed
        if not os.path.isfile(file_path):
            logger.info(f'Processing page id: {page["id"]}')
            page_title = page['title']
            page_content = self.confluence.get_page_by_id(
                page_id,
                expand='body.storage.value,version'
            )['body']['storage']['value']

            page_content = self.convert_confluence_xml_to_html(page_content)
            # logger.info(page_content)

            # Save content to a file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(page_content)

            # Extract attachments if requested
            if include_attachments:
                self.process_attachment(page["id"])

            # Saving metadata to a multi-line JSON file (https://jsonlines.org/)
            source = self.base_url.strip("/") + page["_links"]["webui"]
            version = page["version"]["when"]
            content_type = 'page'
            self.save_metadata(page_title, page_id, source, version, file_path, content_type)

    def process_attachment(
        self,
        page_id: str,
    ):
        attachments = self.confluence.get_attachments_from_content(page_id)["results"]
        for attachment in attachments:
            media_type = attachment["metadata"]["mediaType"]
            absolute_url = self.base_url + attachment["_links"]["download"]
            title = attachment["title"]
            # logger.info('===========================================')
            # logger.info(f'Title: {title}')
            # logger.info(f'Absolute URL: {absolute_url}')
            # logger.info(f'Media Type: {media_type}')
            # logger.info('===========================================')
 
            try:
                response = self.confluence.request(path=absolute_url, absolute=True)
                if response.status_code == 200:
                    file_path = f'{self.content_dir}/{title}'
                    with open(file_path, 'wb') as file:
                        file.write(response.content)
                    # Saving metadata to a multi-line JSON file (https://jsonlines.org/)
                    self.save_metadata(title, page_id, absolute_url, '', file_path, media_type)

            except HTTPError as exception:
                logger.error(f'Absolute URL: {absolute_url}')
                logger.error(f'HTTPError: {exception}')

    def save_metadata(self, page_title, page_id, source, version, file_path, content_type):
        with open(f'{self.content_dir}/__metadata__.jsonl', 'a', encoding='utf-8') as file:
            metadata = {
                    "page_title": page_title,
                    "page_id": page_id,
                    "source": source,
                    "version": version,
                    "file_path": file_path,
                    "content_type": content_type,
                }
            json.dump(metadata, file)
            file.write('\n')

    def paginate_request(self, retrieval_method: Callable, **kwargs: Any) -> List:
        max_pages = kwargs.pop("max_pages")
        docs: List[dict] = []
        while len(docs) < max_pages:
            get_pages = retry(
                reraise=True,
                stop=stop_after_attempt(
                    self.number_of_retries  # type: ignore[arg-type]
                ),
                wait=wait_exponential(
                    multiplier=1,
                    min=self.min_retry_seconds,  # type: ignore[arg-type]
                    max=self.max_retry_seconds,  # type: ignore[arg-type]
                ),
                before_sleep=before_sleep_log(logger, logging.WARNING),
            )(retrieval_method)
            batch = get_pages(**kwargs, start=len(docs))
            if not batch:
                break
            docs.extend(batch)
        return docs[:max_pages]

    def convert_confluence_xml_to_html(
            self,
            page_content: str
    ):
        soup = BeautifulSoup(page_content, 'lxml')
        # logger.info('===========================================')
        # logger.info(f'page_content: {page_content}')
        # logger.info('===========================================')

        # Convert <ac:image> tags to <img> tags
        for image in soup.find_all('ac:image'):
            img_src = None
            attachment = image.find('ri:attachment')
            if attachment:
                img_src = attachment.get('ri:filename')
            else:
                url = image.find('ri:url')
                if url:
                    img_src = url.get('ri:value')
            if img_src:
                img_tag = soup.new_tag('img', src=img_src)
                image.replace_with(img_tag)

        # Convert <ac:link> tags to <a> tags
        for link in soup.find_all('ac:link'):
            href = None
            page = link.find('ri:page')
            if page:
                href = page.get('ri:content-title')
            else:
                url = link.find('ri:url')
                if url:
                    href = url.get('ri:value')
            if href:
                a_tag = soup.new_tag('a', href=href)
                a_tag.string = href
                link.replace_with(a_tag)
            else:
                placeholder = soup.new_tag('span')
                placeholder.string = '[broken link]'
                link.replace_with(placeholder)

        # Convert <ac:structured-macro> tags to <div> tags
        for macro in soup.find_all('ac:structured-macro'):
            div_tag = soup.new_tag('div')
            div_tag.string = macro.get('ac:name', '')
            macro.replace_with(div_tag)

        # Convert <ac:plain-text-body> tags to <p> tags
        for text_body in soup.find_all('ac:plain-text-body'):
            p_tag = soup.new_tag('p')
            p_tag.string = text_body.text
            text_body.replace_with(p_tag)

        return str(soup)
