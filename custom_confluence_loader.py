from langchain.document_loaders import ConfluenceLoader
from langchain.docstore.document import Document
from typing import Optional
from enum import Enum

class CustomConfluenceLoader(ConfluenceLoader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # override a method
    def load(self, *args, **kwargs):
        # Extract the parameters
        space_key = kwargs.get('space_key')
        limit = kwargs.get('limit')
        max_pages = kwargs.get('max_pages')
        include_archived_content = kwargs.get('include_archived_content')
        include_restricted_content = kwargs.get('include_restricted_content')
        include_attachments = kwargs.get('include_attachments')
        include_comments = kwargs.get('include_comments')
        ocr_languages = kwargs.get('ocr_languages')

        docs = []
        if space_key:
            pages = self.paginate_request(
                self.confluence.get_all_pages_from_space,
                space=space_key,
                limit=limit,
                max_pages=max_pages,
                status="any" if include_archived_content else "current",
                expand="body.storage.value,version", # content_format.value,
            )
            docs += self.process_pages(
                pages,
                include_restricted_content,
                include_attachments,
                include_comments,
                ocr_languages,
            )
        else:
            docs = super().load(*args, **kwargs)

        return docs

    # override a method
    def process_page(
        self,
        page: dict,
        include_attachments: bool,
        include_comments: bool,
        ocr_languages: Optional[str] = None,
    ) -> Document:
        try:
            from bs4 import BeautifulSoup  # type: ignore
        except ImportError:
            raise ImportError(
                "`beautifulsoup4` package not found, please run "
                "`pip install beautifulsoup4`"
            )

        if include_attachments:
            attachment_texts = self.process_attachment(page["id"], ocr_languages)
        else:
            attachment_texts = []
        text = BeautifulSoup(page["body"]["storage"]["value"], "lxml").get_text(
            " ", strip=True
        ) + "".join(attachment_texts)
        if include_comments:
            comments = self.confluence.get_page_comments(
                page["id"], expand="body.view.value", depth="all"
            )["results"]
            comment_texts = [
                BeautifulSoup(comment["body"]["view"]["value"], "lxml").get_text(
                    " ", strip=True
                )
                for comment in comments
            ]
            text = text + "".join(comment_texts)

        return Document(
            page_content=text,
            metadata={
                "title": page["title"],
                "id": page["id"],
                "source": self.base_url.strip("/") + page["_links"]["webui"],
                "version": page["version"]["when"],
            },
        )
    
    # # add a new method
    # def print_hello(self):
    #     print("Hello, world!")


    # def load(
    #     self,
    #     space_key: Optional[str] = None,
    #     page_ids: Optional[List[str]] = None,
    #     label: Optional[str] = None,
    #     cql: Optional[str] = None,
    #     include_restricted_content: bool = False,
    #     include_archived_content: bool = False,
    #     include_attachments: bool = False,
    #     include_comments: bool = False,
    #     content_format: ContentFormat = ContentFormat.STORAGE,
    #     limit: Optional[int] = 50,
    #     max_pages: Optional[int] = 1000,
    #     ocr_languages: Optional[str] = None,
    # ) -> List[Document]:
    #     """
    #     :param space_key: Space key retrieved from a confluence URL, defaults to None
    #     :type space_key: Optional[str], optional
    #     :param page_ids: List of specific page IDs to load, defaults to None
    #     :type page_ids: Optional[List[str]], optional
    #     :param label: Get all pages with this label, defaults to None
    #     :type label: Optional[str], optional
    #     :param cql: CQL Expression, defaults to None
    #     :type cql: Optional[str], optional
    #     :param include_restricted_content: defaults to False
    #     :type include_restricted_content: bool, optional
    #     :param include_archived_content: Whether to include archived content,
    #                                      defaults to False
    #     :type include_archived_content: bool, optional
    #     :param include_attachments: defaults to False
    #     :type include_attachments: bool, optional
    #     :param include_comments: defaults to False
    #     :type include_comments: bool, optional
    #     :param content_format: Specify content format, defaults to ContentFormat.STORAGE
    #     :type content_format: ContentFormat
    #     :param limit: Maximum number of pages to retrieve per request, defaults to 50
    #     :type limit: int, optional
    #     :param max_pages: Maximum number of pages to retrieve in total, defaults 1000
    #     :type max_pages: int, optional
    #     :param ocr_languages: The languages to use for the Tesseract agent. To use a
    #                           language, you'll first need to install the appropriate
    #                           Tesseract language pack.
    #     :type ocr_languages: str, optional
    #     :raises ValueError: _description_
    #     :raises ImportError: _description_
    #     :return: _description_
    #     :rtype: List[Document]
    #     """
    #     if not space_key and not page_ids and not label and not cql:
    #         raise ValueError(
    #             "Must specify at least one among `space_key`, `page_ids`, "
    #             "`label`, `cql` parameters."
    #         )

    #     docs = []

        # if space_key:
        #     pages = self.paginate_request(
        #         self.confluence.get_all_pages_from_space,
        #         space=space_key,
        #         limit=limit,
        #         max_pages=max_pages,
        #         status="any" if include_archived_content else "current",
        #         expand=content_format.value,
        #     )
        #     docs += self.process_pages(
        #         pages,
        #         include_restricted_content,
        #         include_attachments,
        #         include_comments,
        #         content_format,
        #         ocr_languages,
        #     )

    #     if label:
    #         pages = self.paginate_request(
    #             self.confluence.get_all_pages_by_label,
    #             label=label,
    #             limit=limit,
    #             max_pages=max_pages,
    #         )
    #         ids_by_label = [page["id"] for page in pages]
    #         if page_ids:
    #             page_ids = list(set(page_ids + ids_by_label))
    #         else:
    #             page_ids = list(set(ids_by_label))

    #     if cql:
    #         pages = self.paginate_request(
    #             self._search_content_by_cql,
    #             cql=cql,
    #             limit=limit,
    #             max_pages=max_pages,
    #             include_archived_spaces=include_archived_content,
    #             expand=content_format.value,
    #         )
    #         docs += self.process_pages(
    #             pages,
    #             include_restricted_content,
    #             include_attachments,
    #             include_comments,
    #             content_format,
    #             ocr_languages,
    #         )

    #     if page_ids:
    #         for page_id in page_ids:
    #             get_page = retry(
    #                 reraise=True,
    #                 stop=stop_after_attempt(
    #                     self.number_of_retries  # type: ignore[arg-type]
    #                 ),
    #                 wait=wait_exponential(
    #                     multiplier=1,  # type: ignore[arg-type]
    #                     min=self.min_retry_seconds,  # type: ignore[arg-type]
    #                     max=self.max_retry_seconds,  # type: ignore[arg-type]
    #                 ),
    #                 before_sleep=before_sleep_log(logger, logging.WARNING),
    #             )(self.confluence.get_page_by_id)
    #             page = get_page(page_id=page_id, expand=content_format.value)
    #             if not include_restricted_content and not self.is_public_page(page):
    #                 continue
    #             doc = self.process_page(
    #                 page,
    #                 include_attachments,
    #                 include_comments,
    #                 content_format,
    #                 ocr_languages,
    #             )
    #             docs.append(doc)

    #     return docs
