import xkcd
import readersdigest
import brainyquote
import unittest
import os


class BrainyquoteTest(unittest.TestCase):

    def test_author_urls(self):
        url = "https://www.brainyquote.com/authors"
        authors_urls = brainyquote.author_urls(url)
        athrs = ['karl_marx',
                 'johnny_depp',
                 'joseph_stalin',
                 'bruce_lee',
                 'aristotle',
                 'a_p_j_abdul_kalam',
                 'mark_zuckerberg',
                 'woody_allen',
                 'vladimir_putin',
                 'robert_frost']
        test_preset = []
        for i in athrs:
            for j in authors_urls:
                if j.endswith(i):
                    test_preset.append(True)
                    break
            else:
                test_preset.append(False)

        self.assertTrue(all(test_preset))

    def test_download_quotes(self):
        driver = brainyquote.get_driver()
        url = "https://www.brainyquote.com/authors/a_p_j_abdul_kalam"
        quotes = brainyquote.download_quotes(driver, url, 1)
        quotes = quotes[0]
        self.assertTrue(quotes.get_id().startswith('/quotes'))


class XkcdTest(unittest.TestCase):

    def test_download_image_page_source(self):
        img_url = "https://www.xkcd.com/1/"
        page_source = xkcd.download_image_page_source(img_url)
        self.assertIsInstance(page_source, str)

    def test_download_image(self):
        template_image = xkcd.ImageData()
        template_image.set_content(
            message="Don't we all.",
            title="Barrel - Part 1",
            link="https://imgs.xkcd.com/comics/barrel_cropped_(1).jpg",
            file_format="jpg",
            number=1,
            filename="xkcd.jpg",
            filepath=os.getcwd() + '/' + "xkcd.jpg",
        )
        image_test = xkcd.download_image()
        self.assertEqual(template_image, image_test)


class ReadersDigestTest(unittest.TestCase):

    def test_download_jokes(self):
        url = "https://www.rd.com/"
        joke_types = ["/knock-knock",
                      "/corny",
                      "/one-liners",
                      "/riddles"]

        for typ in joke_types:
            joke = readersdigest.download_jokes(url, typ, 1)
            joke = joke[0]
            self.assertTrue("post" in joke.get_id())


if __name__ == '__main__':
    unittest.main(verbosity=2)
    # ReadersDigestTest().test_download_jokes()
    # BrainyquoteTest().test_download_quotes()