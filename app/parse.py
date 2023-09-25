import aiohttp
import asyncio
import aiofiles
from bs4 import BeautifulSoup
import aiofiles.os
import os
import shutil
from fpdf import FPDF


class LibralyRuParser:
    def __init__(self):
        self.url = 'https://ilibrary.ru'
        self.headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'}


    async def parse_text(self, url, count, book_name):
        async with aiohttp.request('GET', url, headers=self.headers) as page:
            result_text_list = []

            r = await page.text()
            soup = BeautifulSoup(r, 'lxml')
            text_block = soup.find('div', id='text', class_='t hya')
            if text_block is None:
                return None
            try:
                page_title = text_block.find('h2').text.strip()
            except:
                page_title = ''
            if text_block.find('div', id='pmt1'):
                is_prose = True
            else:
                if text_block.find('span', class_='p'):
                    is_prose = False
                else:
                    return None

            if not await aiofiles.os.path.exists(f'data/{book_name}'):
                await aiofiles.os.mkdir(f'data/{book_name}')


            if not is_prose:
                result_text_list += [i.text.strip() for i in text_block.find_all('span', class_='p')]
            else:
                text_block_true = text_block.find_all('span', class_='pmm')
                for temp in text_block_true:
                    paragraph = temp.find_all('span', class_='p')
                    for pr in paragraph:
                        temp_list = []
                        texts = pr.find_all('span', class_='vl')
                        for text in texts:
                            temp_list.append(text.text.strip().replace('\xa0', ''))
                        result_text_list += temp_list

            async with aiofiles.open(f'data/{book_name}/{count}.txt', 'w', encoding='utf-8') as f:
                if page_title:
                    await f.write(page_title + '\n\n' + '\n'.join(result_text_list))
                else:
                    await f.write(page_title + '\n'.join(result_text_list))


    async def parse_text_from_book(self, url):
        async with aiohttp.request('GET', url, headers=self.headers) as page:
            r = await page.text()
            soup = BeautifulSoup(r, 'lxml')
            try:
                count_pages = int(soup.find('div', id='bnav').find_all('span')[-1].text.strip().split('/')[1])
            except AttributeError:
                return None


            urls = []
            if count_pages > 1:
                for i in range(1, count_pages + 1):
                    temp = url.split('/p.')[1].split('/')[0]
                    url = url.replace('p.' + temp, f'p.{i}')
                    urls.append(url)
            else:
                urls.append(url)

            return urls


async def parse(url):
    if await aiofiles.os.path.exists('data/'):
        shutil.rmtree('data/')
    await aiofiles.os.mkdir('data/')

    parser = LibralyRuParser()
    task1 = asyncio.create_task(parser.parse_text_from_book(url))
    results = await task1
    tasks = []
    j = 0
    for url_ in results:
        task2 = asyncio.create_task(parser.parse_text(url_, j, 'tgbot'))
        tasks.append(task2)
        await asyncio.sleep(0.1)
        j += 1
    r = await asyncio.gather(*tasks)


def create_pdf(path_to_folder, title, path_to_font, font_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font(font_name, '', path_to_font, uni=True)
    pdf.set_font(font_name, size=8)
    readlines = []
    ts = []
    for page in sorted(os.listdir(path_to_folder), key=lambda x: int(x.rstrip('.txt'))):
        with open(f'{path_to_folder}/{page}') as f:
            r = [i.replace('xa01', '').replace('\n', ' ') for i in f.readlines()]
            readlines.append(r)

    for pr in readlines:
        if pr[0][0] in 'IVXL' or 'действие' in pr[0].lower() or 'глава' in pr[0].lower() or 'примечания' in pr[0].lower() or 'примечание' in pr[0].lower():
            pdf.cell(105, 20, txt=pr[0], ln=1, align='C')
        pr_str = ''.join(pr).replace('\x97', '-').replace(pr[0], '').replace('\xa0', ' ')


        if not all(list(map(lambda x: len(x) < 105, pr))):
            for i in range(0, len(pr_str), 105):
                row = pr_str[i:i+105].strip().replace('\n', '')
                pdf.cell(105, 5, txt=row, ln=1, align='L')
        else:
            for row in pr:
                pdf.cell(105, 5, txt=row.replace('\x97', '-').replace('xa01', '').replace('\xa0', ' '), ln=1, align='L')
    pdf.output(f'books/{title}/book.pdf')


async def compare_book(path, name_book, path_to_font_, font_name_):
    result_text = ''
    parts = sorted(os.listdir(path), key=lambda x: int(x.rstrip('.txt')))
    for part in parts:
        async with aiofiles.open(path + part) as f:
            result_text += await f.read() + '\n\n'

    if not await aiofiles.os.path.exists(f'books/{name_book}'):
        await aiofiles.os.mkdir(f'books/{name_book}')
    async with aiofiles.open(f'books/{name_book}/book.txt', 'w', encoding='utf-8') as f:
        await f.write(result_text.replace('\x97', '-').replace('\xa0', ''))
    create_pdf(f'data/{name_book}/', name_book, path_to_font_, font_name_)


async def bot_api_parse(url, path_to_font__, font_name__):
    if os.path.exists('data/tgbot/'):
        shutil.rmtree('data/tgbot/')
    os.mkdir('data/tgbot/')
    await parse(url)
    if not os.path.exists('books/'):
        os.mkdir('books/')
    await compare_book('data/tgbot/', 'tgbot', path_to_font__, font_name__)
